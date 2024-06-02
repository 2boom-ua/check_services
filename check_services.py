#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2boom 2023-24

import json
import os.path
import subprocess
import time
import requests
from schedule import every, repeat, run_pending
from requests.exceptions import RequestException


def getHostname():
	hostname = ""
	if os.path.exists('/proc/sys/kernel/hostname'):
		with open('/proc/sys/kernel/hostname', "r") as file:
			hostname = file.read().strip('\n')
	return hostname


def SendMessage(message : str):
	message = message.replace("\t", "")
	if telegram_on:
		try:
			response = requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"})
		except requests.exceptions.RequestException as e:
			print("error:", e)
	if discord_on:
		try:
			response = requests.post(discord_web, json={"content": message.replace("*", "**")})
		except requests.exceptions.RequestException as e:
			print("error:", e)
	if slack_on:
		try:
			response = requests.post(slack_web, json = {"text": message})
		except requests.exceptions.RequestException as e:
			print("error:", e)
	message = message.replace("*", "")
	header = message[:message.index("\n")].rstrip("\n")
	message = message[message.index("\n"):].strip("\n")
	if gotify_on:
		try:
			response = requests.post(f"{gotify_web}/message?token={gotify_token}",\
			json={'title': header, 'message': message, 'priority': 0})
		except requests.exceptions.RequestException as e:
			print("error:", e)
	if ntfy_on:
		try:
			response = requests.post(f"{ntfy_web}/{ntfy_sub}", data=message.encode(encoding='utf-8'), headers={"Title": header})
		except requests.exceptions.RequestException as e:
			print("error:", e)
	if pushbullet_on:
		try:
			response = requests.post('https://api.pushbullet.com/v2/pushes',\
			json={'type': 'note', 'title': header, 'body': message},\
			headers={'Access-Token': pushbullet_api, 'Content-Type': 'application/json'})
		except requests.exceptions.RequestException as e:
			print("error:", e)

if __name__ == "__main__":	
	hostname = getHostname()
	current_path =  os.path.dirname(os.path.realpath(__file__))
	exclude_services = []
	telegram_on = discord_on = gotify_on = ntfy_on = slack_on = pushbullet_on = False
	token = chat_id = discord_web = gotify_web = gotify_token = ntfy_web = ntfy_sub = pushbullet_api = slack_web = messaging_service = ""
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
			token = parsed_json["TELEGRAM"]["TOKEN"]
			chat_id = parsed_json["TELEGRAM"]["CHAT_ID"]
			messaging_service += "- messenging: Telegram,\n"
		if discord_on:
			discord_web = parsed_json["DISCORD"]["WEB"]
			messaging_service += "- messenging: Discord,\n"
		if gotify_on:
			gotify_web = parsed_json["GOTIFY"]["WEB"]
			gotify_token = parsed_json["GOTIFY"]["TOKEN"]
			messaging_service += "- messenging: Gotify,\n"
		if ntfy_on:
			ntfy_web = parsed_json["NTFY"]["WEB"]
			ntfy_sub = parsed_json["NTFY"]["SUB"]
			messaging_service += "- messenging: Ntfy,\n"
		if pushbullet_on:
			pushbullet_api = parsed_json["PUSHBULLET"]["API"]
			messaging_service += "- messenging: Pushbullet,\n"
		if slack_on:
			slack_web = parsed_json["SLACK"]["WEB"]
			messaging_service += "- messenging: Slack,\n"
		min_repeat = int(parsed_json["MIN_REPEAT"])
		SendMessage(f"*{hostname}* (services)\nservices monitor:\n{messaging_service}- polling period: {min_repeat} minute(s).")
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
	if not old_status: old_status = "0" * len(services)
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
		SendMessage(f"*{hostname}* (services)\n{message}")


while True:
	run_pending()
	time.sleep(1)