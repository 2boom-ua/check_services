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
	"""Get the hostname."""
	hostname = ""
	hostname_path = '/proc/sys/kernel/hostname'
	if os.path.exists(hostname_path):
		with open(hostname_path, "r") as file:
			hostname = file.read().strip()
	return hostname


def SendMessage(message: str):
	"""Send notifications to various messaging services (Telegram, Discord, Slack, Gotify, Ntfy, Pushbullet, Pushover, Matrix)."""
	def SendRequest(url, json_data=None, data=None, headers=None):
		"""Send an HTTP POST request and handle exceptions."""
		try:
			response = requests.post(url, json=json_data, data=data, headers=headers)
			response.raise_for_status()
		except requests.exceptions.RequestException as e:
			print(f"Error sending message: {e}")
	if telegram_on:
		for token, chat_id in zip(telegram_tokens, telegram_chat_ids):
			url = f"https://api.telegram.org/bot{token}/sendMessage"
			json_data = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
			SendRequest(url, json_data)
	if discord_on:
		for token in discord_tokens:
			url = f"https://discord.com/api/webhooks/{token}"
			json_data = {"content": message.replace("*", "**")}
			SendRequest(url, json_data)
	if slack_on:
		for token in slack_tokens:
			url = f"https://hooks.slack.com/services/{token}"
			json_data = {"text": message}
			SendRequest(url, json_data)
	if matrix_on:
		for token, server_url, room_id in zip(matrix_tokens, matrix_server_urls, matrix_room_ids):
			url = f"{server_url}/_matrix/client/r0/rooms/{room_id}/send/m.room.message?access_token={token}"
			matrix_message = "<br>".join(string.replace('*', '<b>', 1).replace('*', '</b>', 1) for string in message.split("\n"))
			json_data = {"msgtype": "m.text", "body": matrix_message, "format": "org.matrix.custom.html", "formatted_body": matrix_message}
			headers_data = {"Content-Type": "application/json"}
			SendRequest(url, json_data, None, headers_data)
	
	header, message = message.replace("*", "").split("\n", 1)
	message = message.strip()

	if gotify_on:
		for token, chat_url in zip(gotify_tokens, gotify_chat_urls):
			url = f"{chat_url}/message?token={token}"
			json_data = {'title': header, 'message': message, 'priority': 0}
			SendRequest(url, json_data)
	if ntfy_on:
		for token, chat_url in zip(ntfy_tokens, ntfy_chat_urls):
			url = f"{chat_url}/{token}"
			data_data = message.encode(encoding = 'utf-8')
			headers_data = {"title": header}
			SendRequest(url, None, data_data, headers_data)
	if pushbullet_on:
		for token in pushbullet_tokens:
			url = "https://api.pushbullet.com/v2/pushes"
			json_data = {'type': 'note', 'title': header, 'body': message}
			headers_data = {'Access-Token': token, 'Content-Type': 'application/json'}
			SendRequest(url, json_data, None, headers_data)
	if pushover_on:
		for token, user_key in zip(pushover_tokens, pushover_user_keys):
			url = "https://api.pushover.net/1/messages.json"
			json_data = {"token": token, "user": user_key, "message": message, "title": header}
			SendRequest(url, json_data)


if __name__ == "__main__":
	"""Load configuration and initialize monitoring"""
	hostname = getHostname()
	header = f"*{hostname}* (services)\n"
	current_path =  os.path.dirname(os.path.realpath(__file__))
	exclude_services = []
	monitoring_mg = ""
	old_status = ""
	dots = {"green": "\U0001F7E2", "red": "\U0001F534"}
	square_dot = {"green": "\U0001F7E9", "red": "\U0001F7E5"}
	if os.path.exists(f"{current_path}/exlude_service.json"):
		with open(f"{current_path}/exlude_service.json", "r") as file:
			parsed_json = json.loads(file.read())
		exclude_services = parsed_json["list"]
	if os.path.exists(f"{current_path}/config.json"):
		with open(f"{current_path}/config.json", "r") as file:
			parsed_json = json.loads(file.read())
		default_dot_style = parsed_json["DEFAULT_DOT_STYLE"]
		if not default_dot_style:
			dots = square_dot
		green_dot, red_dot = dots["green"], dots["red"]
		telegram_on, discord_on, gotify_on, ntfy_on, pushbullet_on, pushover_on, slack_on, matrix_on = (parsed_json[key]["ON"] for key in ["TELEGRAM", "DISCORD", "GOTIFY", "NTFY", "PUSHBULLET", "PUSHOVER", "SLACK", "MATRIX"])
		services = {"TELEGRAM": ["TOKENS", "CHAT_IDS"], "DISCORD": ["TOKENS"], "SLACK": ["TOKENS"],"GOTIFY": ["TOKENS", "CHAT_URLS"],
			"NTFY": ["TOKENS", "CHAT_URLS"], "PUSHBULLET": ["TOKENS"], "PUSHOVER": ["TOKENS", "USER_KEYS"], "MATRIX": ["TOKENS", "SERVER_URLS", "ROOM_IDS"]}
		for service, keys in services.items():
			if parsed_json[service]["ON"]:
				globals().update({f"{service.lower()}_{key.lower()}": parsed_json[service][key] for key in keys})
				monitoring_mg += f"- messaging: {service.capitalize()},\n"
		min_repeat = int(parsed_json["MIN_REPEAT"])
		SendMessage(f"{header}services monitor:\n{monitoring_mg}- polling period: {min_repeat} minute(s).")
	else:
		print("config.json not found")


@repeat(every(min_repeat).minutes)
def CheckServices():
	"""Periodically check for services status"""
	dir_path = "/etc/systemd/system/multi-user.target.wants"
	status_dot = ""
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
		SendMessage(f"{header}{message}")


while True:
	run_pending()
	time.sleep(1)
