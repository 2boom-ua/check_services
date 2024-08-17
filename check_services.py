#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright: 2boom 2023-24

import json
import os.path
import subprocess
import time
import requests
from schedule import every, repeat, run_pending


def getHostname():
	hostname = ""
	hostname_path = '/proc/sys/kernel/hostname'
	if os.path.exists(hostname_path):
		with open(hostname_path, "r") as file:
			hostname = file.read().strip()
	return hostname


def send_message(message: str):
	def send_request(url, json_data=None, data=None, headers=None):
		try:
			response = requests.post(url, json=json_data, data=data, headers=headers)
			response.raise_for_status()
		except requests.exceptions.RequestException as e:
			print(f"Error sending message: {e}")
	if telegram_on:
		for token, chat_id in zip(telegram_tokens, telegram_chat_ids):
			url = f"https://api.telegram.org/bot{token}/sendMessage"
			json_data = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
			send_request(url, json_data)
	if discord_on:
		for token in discord_tokens:
			url = f"https://discord.com/api/webhooks/{token}"
			json_data = {"content": message.replace("*", "**")}
			send_request(url, json_data)
	if slack_on:
		for token in slack_tokens:
			url = f"https://hooks.slack.com/services/{token}"
			json_data = {"text": message}
			send_request(url, json_data)
	header, message = message.replace("*", "").split("\n", 1)
	message = message.strip()
	if gotify_on:
		for token, chat_url in zip(gotify_tokens, gotify_chat_urls):
			url = f"{chat_url}/message?token={token}"
			json_data = {'title': header, 'message': message, 'priority': 0}
			send_request(url, json_data)
	if ntfy_on:
		for token, chat_url in zip(ntfy_tokens, ntfy_chat_urls):
			url = f"{chat_url}/{token}"
			data_data = message.encode(encoding = 'utf-8')
			headers_data = {"title": header}
			send_request(url, None, data_data, headers_data)
	if pushbullet_on:
		for token in pushbullet_tokens:
			url = "https://api.pushbullet.com/v2/pushes"
			json_data = {'type': 'note', 'title': header, 'body': message}
			headers_data = {'Access-Token': token, 'Content-Type': 'application/json'}
			send_request(url, json_data, None, headers_data)
	if pushover_on:
		for token, user_key in zip(pushover_tokens, pushover_user_keys):
			url = "https://api.pushover.net/1/messages.json"
			json_data = {"token": token, "user": user_key, "message": message, "title": header}
			send_request(url, json_data)


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
		telegram_on, discord_on, gotify_on, ntfy_on, pushbullet_on, pushover_on, slack_on = (parsed_json[key]["ON"] for key in ["TELEGRAM", "DISCORD", "GOTIFY", "NTFY", "PUSHBULLET", "PUSHOVER", "SLACK"])
		services = {
		"TELEGRAM": ["TOKENS", "CHAT_IDS"], "DISCORD": ["TOKENS"], "SLACK": ["TOKENS"],
		"GOTIFY": ["TOKENS", "CHAT_URLS"], "NTFY": ["TOKENS", "CHAT_URLS"], "PUSHBULLET": ["TOKENS"], "PUSHOVER": ["TOKENS", "USER_KEYS"]
		}
		for service, keys in services.items():
			if parsed_json[service]["ON"]:
				globals().update({f"{service.lower()}_{key.lower()}": parsed_json[service][key] for key in keys})
				monitoring_mg += f"- messaging: {service.capitalize()},\n"
		min_repeat = int(parsed_json["MIN_REPEAT"])
		send_message(f"{header}services monitor:\n{monitoring_mg}- polling period: {min_repeat} minute(s).")
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
		if check.returncode == 0 and check.stdout == b"active\n":
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
		send_message(f"{header}{message}")


while True:
	run_pending()
	time.sleep(1)