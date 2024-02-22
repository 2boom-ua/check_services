#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2boom 2023-24

import json
import telebot
import os.path
import subprocess
from schedule import every, repeat, run_pending
import time
	
def telegram_message(message : str):
	try:
		tb.send_message(CHAT_ID, message, parse_mode='markdown')
	except Exception as e:
		print(f"error: {e}")

if __name__ == "__main__":	
	CURRENT_PATH = "/root/service_check"
	HOSTNAME = open('/proc/sys/kernel/hostname', 'r').read().strip('\n')
	EXCLUDE_SERVICE = []
	if os.path.exists(f"{CURRENT_PATH}/exlude_service.json"):
		parsed_json = json.loads(open(f"{CURRENT_PATH}/exlude_service.json", "r").read())
		EXCLUDE_SERVICE = parsed_json["list"]
	if os.path.exists(f"{CURRENT_PATH}/config.json"):
		parsed_json = json.loads(open(f"{CURRENT_PATH}/config.json", "r").read())
		MIN_REPEAT = int(parsed_json["MIN_REPEAT"])
		TOKEN = parsed_json["TOKEN"]
		CHAT_ID = parsed_json["CHAT_ID"]
		tb = telebot.TeleBot(TOKEN)
		telegram_message(f"*{HOSTNAME}* (services)\nservices monitor started: check period {MIN_REPEAT} minute(s)")
	else:
		print("config.json not found")

@repeat(every(MIN_REPEAT).minutes)
def check_services():
	DIR_PATH = "/etc/systemd/system/multi-user.target.wants"
	TMP_FILE = "/tmp/status_service.tmp"
	STATUS_DOT, RED_DOT, GREEN_DOT = "", "\U0001F534", "\U0001F7E2"
	SERVICE = []
	COUNT_SERVICE = ALL_SERVICES = RESULT_SERVICES = 0
	OLD_STATUS_STR = NEW_STATUS_STR = BAD_SERVICE_LIST = ""
	SERVICE = [FILE for FILE in os.listdir(DIR_PATH) if os.path.isfile(os.path.join(DIR_PATH, FILE)) and FILE.endswith('.service')]
	SERVICE = list(set(SERVICE) - set(EXCLUDE_SERVICE))
	ALL_SERVICES = len(SERVICE)
	if not os.path.exists(TMP_FILE) or len(SERVICE) != os.path.getsize(TMP_FILE):
		with open(TMP_FILE, "w") as file:
			OLD_STATUS_STR += "0" * len(SERVICE)
			file.write(OLD_STATUS_STR)
		file.close()
	else:
		with open(TMP_FILE, "r") as file:
			OLD_STATUS_STR = file.read()
		file.close()
	li = list(OLD_STATUS_STR)
	for i in range(ALL_SERVICES):
		check = subprocess.run(["systemctl", "is-active", SERVICE[i]], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		if check.stdout == b"active\n":
			COUNT_SERVICE += 1
			li[i] = "0"
		else:
			li[i] = "1"
			BAD_SERVICE_LIST += f"{RED_DOT} - *{SERVICE[i]}* is _inactive_!\n"
	if COUNT_SERVICE == ALL_SERVICES:
		STATUS_DOT = f"{GREEN_DOT} - "
	RESULT_SERVICES = ALL_SERVICES - COUNT_SERVICE
	BOT_MESSAGE = f"{STATUS_DOT}controlled service(s):\n|ALL| - {ALL_SERVICES}, |OK| - {COUNT_SERVICE}, |BAD| - {RESULT_SERVICES}\n{BAD_SERVICE_LIST} "
	NEW_STATUS_STR = "".join(li)
	if OLD_STATUS_STR != NEW_STATUS_STR:
		with open(TMP_FILE, "w") as file:	
			file.write(NEW_STATUS_STR)
		file.close()
		print (f"*{HOSTNAME}* (services)\n{BOT_MESSAGE}")
		telegram_message(f"*{HOSTNAME}* (services)\n{BOT_MESSAGE}")
while True:
    run_pending()
    time.sleep(1)