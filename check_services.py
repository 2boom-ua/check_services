#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2boom 2023-24

import json
import os.path
import subprocess
import time
import requests
from schedule import every, repeat, run_pending


def getHostname():
	hostname = ""
	if os.path.exists('/proc/sys/kernel/hostname'):
		with open('/proc/sys/kernel/hostname', "r") as file:
			hostname = file.read().strip('\n')
	return hostname


def sendMessage(message : str):
	if telegram_on:
		try:
			for telegram_token, telegram_chat_id in zip(telegram_tokens, telegram_chat_ids):
				requests.post(f"https://api.telegram.org/bot{telegram_token}/sendMessage", json = {"chat_id": telegram_chat_id, "text": message, "parse_mode": "Markdown"})
		except requests.exceptions.RequestException as e:
			print("error:", e)
	if discord_on:
		try:
			for discord_token in discord_tokens:
				requests.post(f"https://discord.com/api/webhooks/{discord_token}", json = {"content": message.replace("*", "**")})
		except requests.exceptions.RequestException as e:
			print("Error:", e)
	if slack_on:
		try:
			for slack_token in slack_tokens:
				requests.post(f"https://hooks.slack.com/services/{slack_token}", json = {"text": message})
		except requests.exceptions.RequestException as e:
			print("Error:", e)
	message = message.replace("*", "")
	header = message[:message.index("\n")].rstrip("\n")
	message = message[message.index("\n"):].strip("\n")
	if gotify_on:
		try:
			for gotify_chat_web, gotify_token in zip(gotify_chat_webs, gotify_tokens):
				requests.post(f"{gotify_chat_web}/message?token={gotify_token}",\
				json={'title': header, 'message': message, 'priority': 0})
		except requests.exceptions.RequestException as e:
			print("Error:", e)
	if ntfy_on:
		try:
			for ntfy_chat_web, ntfy_token in zip(ntfy_chat_webs, ntfy_tokens):
				requests.post(f"{ntfy_chat_web}/{ntfy_token}", data = message.encode(encoding = 'utf-8'), headers = {"title": header})
		except requests.exceptions.RequestException as e:
			print("Error:", e)
	if pushbullet_on:
		try:
			for pushbullet_token in pushbullet_tokens:
				requests.post('https://api.pushbullet.com/v2/pushes',\
				json = {'type': 'note', 'title': header, 'body': message},\
				headers = {'Access-Token': pushbullet_token, 'Content-Type': 'application/json'})
		except requests.exceptions.RequestException as e:
			print("Error:", e)

if __name__ == "__main__":	
	hostname = getHostname()
	header = f"*{hostname}* (services)\n"
	current_path =  os.path.dirname(os.path.realpath(__file__))
	exclude_services = []
	monitoring_mg = ""
	old_status = ""
	if os.path.exists(f"{current_path}/exlude_service.json"):
		with open(f"{current_path}/exlude_service.json", "r") as file:
			parsed_json = json.loads(file.read())
		exclude_services = parsed_json["list"]
	if os.path.exists(f"{current_path}/config.json"):
		with open(f"{current_path}/config.json", "r") as file:
			parsed_json = json.loads(file.read())
		telegram_on = parsed_json["TELEGRAM"]["ON"]
		discord_on = parsed_json["DISCORD"]["ON"]
		gotify_on = parsed_json["GOTIFY"]["ON"]
		ntfy_on = parsed_json["NTFY"]["ON"]
		pushbullet_on = parsed_json["PUSHBULLET"]["ON"]
		slack_on = parsed_json["SLACK"]["ON"]
		if telegram_on:
			telegram_tokens = parsed_json["TELEGRAM"]["TOKENS"]
			telegram_chat_ids = parsed_json["TELEGRAM"]["CHAT_IDS"]
			monitoring_mg += "- messenging: Telegram,\n"
		if discord_on:
			discord_tokens = parsed_json["DISCORD"]["TOKENS"]
			monitoring_mg += "- messenging: Discord,\n"
		if slack_on:
			slack_tokens = parsed_json["SLACK"]["TOKENS"]
			monitoring_mg += "- messenging: Slack,\n"
		if gotify_on:
			gotify_tokens = parsed_json["GOTIFY"]["TOKENS"]
			gotify_chat_webs = parsed_json["GOTIFY"]["CHAT_WEB"]
			monitoring_mg += "- messenging: Gotify,\n"
		if ntfy_on:
			ntfy_tokens = parsed_json["NTFY"]["TOKENS"]
			ntfy_chat_webs = parsed_json["NTFY"]["CHAT_WEB"]
			monitoring_mg += "- messenging: Ntfy,\n"
		if pushbullet_on:
			pushbullet_tokens = parsed_json["PUSHBULLET"]["TOKENS"]
			monitoring_mg += "- messenging: Pushbullet,\n"
		min_repeat = int(parsed_json["MIN_REPEAT"])
		sendMessage(f"{header}services monitor:\n{monitoring_mg}- polling period: {min_repeat} minute(s).")
	else:
		print("config.json not found")


@repeat(every(min_repeat).minutes)
def check_services():
	dir_path = "/etc/systemd/system/multi-user.target.wants"
	status_dot, red_dot, green_dot = "", "\U0001F534", "\U0001F7E2"
	current_status = services = []
	global old_status 
	count_service = all_services = result_services = 0
	message = new_status = bad_service_list = ""
	services = [file for file in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, file)) and file.endswith('.service')]
	services = list(set(services) - set(exclude_services))
	all_services = len(services)
	if not old_status or len(services) != len(old_status): old_status = "0" * len(services)	
	current_status = list(old_status)
	for i, service in enumerate(services):
		check = subprocess.run(["systemctl", "is-active", service], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		if check.stdout == b"active\n":
			count_service += 1
			current_status[i] = "0"
		else:
			current_status[i] = "1"
			bad_service_list += f"{red_dot} *{service}*: inactive!\n"
	if count_service == all_services: status_dot = green_dot
	result_services = all_services - count_service
	message = f"{status_dot} monitoring service(s):\n|ALL| - {all_services}, |OK| - {count_service}, |BAD| - {result_services}\n{bad_service_list}".lstrip()
	new_status = "".join(current_status)
	if old_status != new_status:
		old_status = new_status
		sendMessage(f"{header}{message}")


while True:
	run_pending()
	time.sleep(1)
