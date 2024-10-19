import json
import os.path
import subprocess
import time
import requests
from schedule import every, repeat, run_pending

def getHostname() -> str:
	"""Get the hostname."""
	hostname = ""
	hostname_path = '/proc/sys/kernel/hostname'
	if os.path.exists(hostname_path):
		with open(hostname_path, "r") as file:
			hostname = file.read().strip()
	return hostname


def FetchServiceStatus() -> tuple:
	"""Collects status of services"""
	dir_path = "/etc/systemd/system/multi-user.target.wants"
	services_list = []
	services = [file for file in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, file)) and file.endswith(".service")]
	services = [service for service in services if service not in exclude_services]
	for service in services:
		check = subprocess.run(["systemctl", "is-active", service], capture_output=True, text=True)
		status = "0" if check.returncode == 0 and check.stdout.strip() == "active" else "1"
		services_list.append(f"{service} {status}")
	return services_list
	

def SendMessage(message: str):
	"""Send notifications to various messaging services (Telegram, Discord, Gotify, Ntfy, Pushbullet, Pushover, Matrix, Zulip, Flock, Slack, RocketChat, Pumble, Mattermost, CUSTOM)."""
	"""CUSTOM - single_asterisks - Zulip, Flock, Slack, RocketChat, Flock, double_asterisks - Pumble, Mattermost """
	def SendRequest(url, json_data=None, data=None, headers=None):
		"""Send an HTTP POST request and handle exceptions."""
		try:
			response = requests.post(url, json=json_data, data=data, headers=headers)
			response.raise_for_status()
		except requests.exceptions.RequestException as e:
			print(f"Error sending message: {e}")
			
	def toHTMLformat(message: str) -> str:
		"""Format the message with bold text and HTML line breaks."""
		html_message = ""
		for i, string in enumerate(message.split('*')):
			html_message += f"<b>{string}</b>" if i % 2 else string
		html_message = html_message.replace("\n", "<br>")
		return html_message

	if telegram_on:
		for token, chat_id in zip(telegram_tokens, telegram_chat_ids):
			url = f"https://api.telegram.org/bot{token}/sendMessage"
			json_data = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
			SendRequest(url, json_data)
	if slack_on:
		for url in slack_webhook_urls:
			json_data = {"text": message}
			SendRequest(url, json_data)
	if rocket_on:
		for url in rocket_webhook_urls:
			json_data = {"text": message}
			SendRequest(url, json_data)
	if zulip_on:
		for url in zulip_webhook_urls:
			json_data = {"text": message}
			SendRequest(url, json_data)
	if flock_on:
		for url in flock_webhook_urls:
			json_data = {"text": message}
			SendRequest(url, json_data)
	if custom_on:
		for url, std_bold in zip(custom_webhook_urls, custom_std_bolds):
			bold_markdown = "**" if std_bold else "*"
			json_data = {"text": message.replace("*", bold_markdown)}
			SendRequest(url, json_data)
	if matrix_on:
		for token, server_url, room_id in zip(matrix_tokens, matrix_server_urls, matrix_room_ids):
			url = f"{server_url}/_matrix/client/r0/rooms/{room_id}/send/m.room.message?access_token={token}"
			html_message = toHTMLformat(message)
			json_data = {"msgtype": "m.text", "body": html_message, "format": "org.matrix.custom.html", "formatted_body": html_message}
			SendRequest(url, json_data)
	if discord_on:
		for url in discord_webhook_urls:
			json_data = {"content": message.replace("*", "**")}
			SendRequest(url, json_data)
	if mattermost_on:
		for url in mattermost_webhook_urls:
			json_data = {'text': message.replace("*", "**")}
			SendRequest(url, json_data)
	if pumble_on:
		for url in pumble_webhook_urls:
			json_data = {"text": message.replace("*", "**")}
			SendRequest(url, json_data)
	if apprise_on:
		for url in apprise_webhook_urls:
			headers_data = {"Content-Type": "application/json"}
			json_data = {"body": message.replace("*", "**"), "type": "info"}
			SendRequest(url, json_data, None, headers_data)
	if ntfy_on:
		for url in ntfy_webhook_urls:
			headers_data = {"Markdown": "yes"}
			SendRequest(url, None, message.replace("*", "**").encode(encoding = "utf-8"), headers_data)

	header, message = message.split("\n", 1)
	message = message.strip()

	if gotify_on:
		for token, server_url in zip(gotify_tokens, gotify_server_urls):
			url = f"{server_url}/message?token={token}"
			json_data = {'title': header.replace("*", ""), "message": message.replace("*", "**").replace("\n", "\n\n"), "priority": 0, "extras": {"client::display": {"contentType": "text/markdown"}}}
			SendRequest(url, json_data)
	if pushover_on:
		for token, user_key in zip(pushover_tokens, pushover_user_keys):
			url = "https://api.pushover.net/1/messages.json"
			html_message = toHTMLformat(message)
			json_data = {"token": token, "user": user_key, "message": html_message, "title": header.replace("*", ""), "html": "1"}
			SendRequest(url, json_data)
	if pushbullet_on:
		for token in pushbullet_tokens:
			url = "https://api.pushbullet.com/v2/pushes"
			json_data = {'type': 'note', 'title': header.replace("*", ""), 'body': message.replace("*", "")}
			headers_data = {'Access-Token': token, 'Content-Type': 'application/json'}
			SendRequest(url, json_data, None, headers_data)


if __name__ == "__main__":
	"""Load configuration and initialize monitoring"""
	hostname = getHostname()
	header = f"*{hostname}* (systemd)\n"
	current_path =  os.path.dirname(os.path.realpath(__file__))
	exclude_services = []
	monitoring_mg = ""
	dots = {"green": "\U0001F7E2", "red": "\U0001F534"}
	square_dot = {"green": "\U0001F7E9", "red": "\U0001F7E5"}
	if os.path.exists(f"{current_path}/exlude_service.json"):
		with open(f"{current_path}/exlude_service.json", "r") as file:
			excluded_json = json.loads(file.read())
		exclude_services = excluded_json["LIST"]
	if os.path.exists(f"{current_path}/config.json"):
		with open(f"{current_path}/config.json", "r") as file:
			config_json = json.loads(file.read())
		default_dot_style = config_json["DEFAULT_DOT_STYLE"]
		if not default_dot_style:
			dots = square_dot
		green_dot, red_dot = dots["green"], dots["red"]
		messaging_platforms = ["TELEGRAM", "DISCORD", "GOTIFY", "NTFY", "PUSHBULLET", "PUSHOVER", "SLACK", "MATRIX", "MATTERMOST", "PUMBLE", "ROCKET", "ZULIP", "FLOCK", "APPRISE", "CUSTOM"]
		telegram_on, discord_on, gotify_on, ntfy_on, pushbullet_on, pushover_on, slack_on, matrix_on, mattermost_on, pumble_on, rocket_on, zulip_on, flock_on, apprise_on, custom_on = (config_json[key]["ENABLED"] for key in messaging_platforms)
		services = {
			"TELEGRAM": ["TOKENS", "CHAT_IDS"],
			"DISCORD": ["WEBHOOK_URLS"],
			"SLACK": ["WEBHOOK_URLS"],
			"GOTIFY": ["TOKENS", "SERVER_URLS"],
			"NTFY": ["WEBHOOK_URLS"],
			"PUSHBULLET": ["TOKENS"],
			"PUSHOVER": ["TOKENS", "USER_KEYS"],
			"MATRIX": ["TOKENS", "SERVER_URLS", "ROOM_IDS"],
			"MATTERMOST": ["WEBHOOK_URLS"],
			"PUMBLE": ["WEBHOOK_URLS"],
			"ROCKET": ["WEBHOOK_URLS"],
			"ZULIP": ["WEBHOOK_URLS"],
			"FLOCK": ["WEBHOOK_URLS"],
			"APPRISE": ["WEBHOOK_URLS"],
			"CUSTOM": ["WEBHOOK_URLS", "STD_BOLDS"]
		}
		for service, keys in services.items():
			if config_json[service]["ENABLED"]:
				globals().update({f"{service.lower()}_{key.lower()}": config_json[service][key] for key in keys})
				monitoring_mg += f"- messaging: {service.capitalize()},\n"
		old_status = FetchServiceStatus()
		min_repeat = max(int(config_json.get("MIN_REPEAT", 1)), 1)
		monitoring_mg += (
			f"- monitoring: {len(old_status)} service(s),\n"
			f"- excluded: {len(exclude_services)} service(s),\n"
			f"- default dot style: {default_dot_style}.\n"
			f"- polling period: {min_repeat} minute(s)."
		)
		SendMessage(f"{header}services monitor:\n{monitoring_mg}")
	else:
		print("config.json not found")


@repeat(every(min_repeat).minutes)
def CheckServices():
	"""Periodically checks the status of services and sends a status update if there are changes."""
	global old_status
	new_status = FetchServiceStatus()
	total_services = len(new_status)
	ok_services = bad_services = 0
	message, result = "", []
	if len(old_status) >= len(new_status):
		result = list(set(new_status).difference(old_status))
	else:
		result = list(set(old_status).difference(new_status))
	if result:
		for service in result:
			service_name, service_status = service.split()[0], service.split()[-1]
			if service_status == "1":
				bad_services += 1
				status_message = "inactive"
				message += f"{red_dot} *{service_name}*: {status_message}!\n"
		if bad_services == 0: message += f"{green_dot} monitoring service(s):\n"
	if old_status != new_status:
		ok_services = total_services - bad_services
		old_status = new_status
		message += f"|ALL| - {total_services}, |OK| - {ok_services}, |BAD| - {bad_services}\n"
		SendMessage(f"{header}{message}")
		
		
while True:
	run_pending()
	time.sleep(1)
