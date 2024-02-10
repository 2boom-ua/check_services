#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2boom 2023-24

import json
import telebot
import os.path
import subprocess
from schedule import every, repeat, run_pending
import time

def get_str_from_file(filename : str):
	if os.path.exists(filename):
		with open(filename, "r") as file:
			ret = file.read().strip("\n")
		file.close()
		return ret
	return ""
	
def bold_html_txt(message : str):
	return f"<b>{message}</b>"
	
def telegram_message(message : str):
	try:
		tb.send_message(CHAT_ID, message, parse_mode='html')
	except Exception as e:
		print(f"error: {e}")

if __name__ == "__main__":	
	CURRENT_PATH = "/root/service_check"
	RED_DOT, GREEN_DOT = "\U0001F534", "\U0001F7E2"
	HOSTNAME = bold_html_txt(get_str_from_file("/proc/sys/kernel/hostname"))
	if os.path.exists(f"{CURRENT_PATH}/config.json"):
		parsed_json = json.loads(open(f"{CURRENT_PATH}/config.json", "r").read())
		MIN_REPEAT = int(parsed_json["MIN_REPEAT"])
		TOKEN = parsed_json["TOKEN"]
		CHAT_ID = parsed_json["CHAT_ID"]
		tb = telebot.TeleBot(TOKEN)
		telegram_message(f"{HOSTNAME} (services)\nservices monitor started: check period {MIN_REPEAT} minute(s)")
	else:
		print("config.json not found")

@repeat(every(MIN_REPEAT).minutes)
def check_services():
	DIR_PATH = "/etc/systemd/system/multi-user.target.wants"
	TMP_FILE = "/tmp/status_service.tmp"
	files_file = os.listdir(DIR_PATH)
	service = exclude_service = []
	count_service = all_service = 0
	old_status_str = new_status_str = bad_service_list = ""
	if os.path.exists(f"{CURRENT_PATH}/exlude_service.json"):
		parsed_json = json.loads(open(f"{CURRENT_PATH}/exlude_service.json", "r").read())
		exclude_service = parsed_json["list"]
	for i in range(len(files_file)):
		if os.path.isfile(f"{DIR_PATH}/{files_file[i]}") and files_file[i].endswith('.service'):
			if len(exclude_service) > 0:
				for j in range(len(exclude_service)):
					if files_file[i] != exclude_service[j]:
						service.append(files_file[i])
			else:
				service.append(files_file[i])
	all_service = len(service)
	if not os.path.exists(TMP_FILE) or len(service) != os.path.getsize(TMP_FILE):
		with open(TMP_FILE, "w") as file:
			for i in range(len(service)):
				old_status_str += "0"
			file.write(old_status_str)
		file.close()
	with open(TMP_FILE, "r") as file:
		old_status_str = file.read()
		li = list(old_status_str)
	file.close()
	for i in range(len(service)):
		check = subprocess.run(["systemctl", "is-active", service[i]], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		if check.stdout == b"active\n":
			count_service += 1
			li[i] = "0"
		else:
			li[i] = "1"
			bad_service_list += f"{RED_DOT} - {bold_html_txt(service[i])} is inactive!\n"
	if count_service == all_service:
		dot = f"{GREEN_DOT} - "
	else:
		dot = ""
	result_services = all_service - count_service
	BOT_MESSAGE = f"{dot}controlled service(s):\n|ALL| - {all_service}, |OK| - {count_service}, |BAD| - {result_services}\n{bad_service_list} "
	new_status_str = "".join(li)
	if old_status_str != new_status_str:
		with open(TMP_FILE, "w") as file:	
			file.write(new_status_str)
		file.close()
		print (f"{HOSTNAME} (services)\n{BOT_MESSAGE}")
		telegram_message(f"{HOSTNAME} (services)\n{BOT_MESSAGE}")
while True:
    run_pending()
    time.sleep(1)