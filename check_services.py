#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2boom 2023

import json
import telebot
import os.path
import subprocess
from schedule import every, repeat, run_pending
import time

def get_host_name():
	if os.path.exists("/proc/sys/kernel/hostname"):
		return open("/proc/sys/kernel/hostname").read().strip("\n")
	else:
		return ""
		
def hbold(item):
	return telebot.formatting.hbold(item)
	
current_path = "/root/service_check"
if os.path.exists(f"{current_path}/config.json"):
	parsed_json = json.loads(open(f"{current_path}/config.json", "r").read())
	min_repeat = int(parsed_json["minutes"])
else:
	min_repeat = 3
RED_DOT, GREEN_DOT = "\U0001F534", "\U0001F7E2"
hostname = hbold(get_host_name())

if os.path.exists(f"{current_path}/telegram_bot.json"):
	parsed_json = json.loads(open(f"{current_path}/telegram_bot.json", "r").read())
	TOKEN = parsed_json["TOKEN"]
	CHAT_ID = parsed_json["CHAT_ID"]
	tb = telebot.TeleBot(TOKEN)
	try:
		tb.send_message(CHAT_ID, f"{hostname} (services)\nservices monitor started: check period {min_repeat} minute(s)", parse_mode='html')
	except Exception as e:
		print(f"error: {e}")
else:
	print("telegram_bot.json not found")

@repeat(every(min_repeat).minutes)
def check_services():
	mode = mode_command = "silent"
	dir_path = "/etc/systemd/system/multi-user.target.wants"
	tmp_file = "/tmp/status_service.tmp"
	files_file = os.listdir(dir_path)
	service = exclude_service = []
	count_service = all_service = 0
	old_status_str = new_status_str = BAD_SERVICE_LIST = ""
	if os.path.exists(f"{current_path}/exlude_service.json"):
		parsed_json = json.loads(open(f"{current_path}/exlude_service.json", "r").read())
		exclude_service = parsed_json["list"]
	for i in range(len(files_file)):
		if os.path.isfile(f"{dir_path}/{files_file[i]}") and files_file[i].endswith('.service'):
			if len(exclude_service) > 0:
				for j in range(len(exclude_service)):
					if files_file[i] != exclude_service[j]:
						service.append(files_file[i])
			else:
				service.append(files_file[i])
	all_service = len(service)
	if not os.path.exists(tmp_file) or len(service) != os.path.getsize(tmp_file):
		with open(tmp_file, "w") as status_file:
			for i in range(len(service)):
				old_status_str += "0"
			status_file.write(old_status_str)
		status_file.close()

	with open(tmp_file, "r") as status_file:
		old_status_str = status_file.read()
		li = list(old_status_str)
		status_file.close()
	
	for i in range(len(service)):
		check = subprocess.run(["systemctl", "is-active", service[i]], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		if check.stdout == b"active\n":
			count_service += 1
			li[i] = "0"
		else:
			li[i] = "1"
			BAD_SERVICE_LIST += f"{RED_DOT} - {hbold(service[i])} is inactive!\n"
	if count_service == all_service:
		dot = f"{GREEN_DOT} - "
	else:
		dot = ""
	result_services = all_service - count_service
	bot_message = f"{dot}controlled service(s):\n|ALL| - {all_service}, |OK| - {count_service}, |BAD| - {result_services}\n{BAD_SERVICE_LIST} "
	new_status_str = "".join(li)
	if old_status_str == new_status_str:
		mode = "silent"
	else:
		with open(tmp_file, "w") as status_file:	
			status_file.write(new_status_str)
			status_file.close()
		mode = "info"
	if mode_command == "info" or mode == "info":
		print (f"{hostname} (services)\n{bot_message}")
		try:
			tb.send_message(CHAT_ID, f"{hostname} (services)\n{bot_message}", parse_mode='html')
		except Exception as e:
			print(f"error: {e}")

while True:
    run_pending()
    time.sleep(1)