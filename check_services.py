#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2boom 2023-24

import json
import telebot
import os.path
import subprocess
import time
import requests
from gotify import Gotify
import discord_notify as dn
from schedule import every, repeat, run_pending

def send_message(message : str):
	if TELEGRAM_ON:
		try:
			tb.send_message(CHAT_ID, message, parse_mode="markdown")
		except Exception as e:
			print(f"error: {e}")
	if DISCORD_ON:
		try:
			notifier.send(message.replace("*", "**").replace("\t", ""), print_message=False)
		except Exception as e:
			print(f"error: {e}")
	message = message.replace("*", "").replace("\t", "")
	header = message[:message.index("\n")].rstrip("\n")
	message = message[message.index("\n"):].strip("\n")
	if GOTIFY_ON:
		gotify = Gotify(base_url=GOTIFY_WEB, app_token=GOTIFY_TOKEN)
		try:
			gotify.create_message(message, title = header)
		except Exception as e:
			print(f"error: {e}")
	if NTFY_ON:
		try:
			requests.post(f"{NTFY_WEB}/{NTFY_SUB}", data=message.encode(encoding='utf-8'), headers={"Title": header})
		except Exception as e:
			print(f"error: {e}")
			
def messaging_service():
	messaging = ""
	if TELEGRAM_ON:
		messaging += "- messenging: Telegram,\n"
	if DISCORD_ON:
		messaging += "- messenging: Discord,\n"
	if GOTIFY_ON:
		messaging += "- messenging: Gotify,\n"
	if NTFY_ON:
		messaging += "- messenging: Ntfy,\n"
	return messaging

if __name__ == "__main__":	
	HOSTNAME = open('/proc/sys/kernel/hostname', 'r').read().strip('\n')
	CURRENT_PATH =  os.path.dirname(os.path.realpath(__file__))
	EXCLUDE_SERVICE = []
	TELEGRAM_ON = DISCORD_ON = GOTIFY_ON = NTFY_ON = False
	TOKEN = CHAT_ID = DISCORD_WEB = GOTIFY_WEB = GOTIFY_TOKEN = NTFY_WEB = NTFY_SUB = ""
	if os.path.exists(f"{CURRENT_PATH}/exlude_service.json"):
		parsed_json = json.loads(open(f"{CURRENT_PATH}/exlude_service.json", "r").read())
		EXCLUDE_SERVICE = parsed_json["list"]
	if os.path.exists(f"{CURRENT_PATH}/config.json"):
		parsed_json = json.loads(open(f"{CURRENT_PATH}/config.json", "r").read())
		TELEGRAM_ON = parsed_json["TELEGRAM"]["ON"]
		DISCORD_ON = parsed_json["DISCORD"]["ON"]
		GOTIFY_ON = parsed_json["GOTIFY"]["ON"]
		NTFY_ON = parsed_json["NTFY"]["ON"]
		if TELEGRAM_ON:
			TOKEN = parsed_json["TELEGRAM"]["TOKEN"]
			CHAT_ID = parsed_json["TELEGRAM"]["CHAT_ID"]
			tb = telebot.TeleBot(TOKEN)
		if DISCORD_ON:
			DISCORD_WEB = parsed_json["DISCORD"]["WEB"]
			notifier = dn.Notifier(DISCORD_WEB)
		if GOTIFY_ON:
			GOTIFY_WEB = parsed_json["GOTIFY"]["WEB"]
			GOTIFY_TOKEN = parsed_json["GOTIFY"]["TOKEN"]
		if NTFY_ON:
			NTFY_WEB = parsed_json["NTFY"]["WEB"]
			NTFY_SUB = parsed_json["NTFY"]["SUB"]
		MIN_REPEAT = int(parsed_json["MIN_REPEAT"])
		send_message(f"*{HOSTNAME}* (services)\nservices monitor:\n{messaging_service()}- polling period: {MIN_REPEAT} minute(s).")
	else:
		print("config.json not found")

@repeat(every(MIN_REPEAT).minutes)
def check_services():
	DIR_PATH = "/etc/systemd/system/multi-user.target.wants"
	TMP_FILE = "/tmp/status_service.tmp"
	STATUS_DOT, RED_DOT, GREEN_DOT = "", "\U0001F534", "\U0001F7E2"
	service = []
	count_service = all_services = result_services = 0
	MESSAGE = old_status_str = new_status_str = bad_service_list = ""
	service = [file for file in os.listdir(DIR_PATH) if os.path.isfile(os.path.join(DIR_PATH, file)) and file.endswith('.service')]
	service = list(set(service) - set(EXCLUDE_SERVICE))
	all_services = len(service)
	if not os.path.exists(TMP_FILE) or len(service) != os.path.getsize(TMP_FILE):
		with open(TMP_FILE, "w") as file:
			old_status_str = "0" * len(service)
			file.write(old_status_str)
		file.close()
	with open(TMP_FILE, "r") as file:
		old_status_str = file.read()
	file.close()
	li = list(old_status_str)
	for i in range(all_services):
		check = subprocess.run(["systemctl", "is-active", service[i]], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		if check.stdout == b"active\n":
			count_service += 1
			li[i] = "0"
		else:
			li[i] = "1"
			bad_service_list += f"{RED_DOT} *{service[i]}*: inactive!\n"
	if count_service == all_services:
		STATUS_DOT = f"{GREEN_DOT}"
	result_services = all_services - count_service
	MESSAGE = f"{STATUS_DOT} monitoring service(s):\n|ALL| - {all_services}, |OK| - {count_service}, |BAD| - {result_services}\n{bad_service_list} "
	new_status_str = "".join(li)
	if old_status_str != new_status_str:
		with open(TMP_FILE, "w") as file:	
			file.write(new_status_str)
		file.close()
		send_message(f"*{HOSTNAME}* (services)\n{MESSAGE}")
while True:
    run_pending()
    time.sleep(1)