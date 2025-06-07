#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2024-25 2boom.

import json
import sys
import os
import subprocess
import time
import requests
import logging
import random
import threading
from datetime import datetime
from schedule import every, repeat, run_pending
from urllib.parse import urlparse
from flask import Flask, render_template, url_for, jsonify
from threading import Thread

platform_webhook_url = []
platform_header = []
platform_payload = []
platform_format_message = []
services_data = []
exclude_services = []
list_non_monitoring = []
old_status = []
green_dot = ""
red_dot = ""
white_dot = ""
yellow_dot = ""
square_dots = {"green": "\U0001F7E9", "red": "\U0001F7E5", "white": "\U00002B1C", "yellow": "\U0001F7E8"}
round_dots = {"green": "\U0001F7E2", "red": "\U0001F534", "white": "\U000026AA", "yellow": "\U0001F7E1"}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.disabled = True

app = Flask(__name__)
app.logger.disabled = True


def get_base_url(url):
    """Get base URL without path or query."""
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}...."


def get_host_name() -> str:
    """Get the hostname."""
    hostname = ""
    hostname_path = '/proc/sys/kernel/hostname'
    if os.path.exists(hostname_path):
        with open(hostname_path, "r") as file:
            hostname = file.read().strip()
    return hostname


def fetch_service_status(dir_path) -> list:
    """Collects status, descriptions, and active since time of services"""
    global services_data

    services_list = []

    services = [
        file for file in os.listdir(dir_path)
        if file.endswith(".service") and os.path.islink(os.path.join(dir_path, file))
    ]
    services = [service for service in services if service not in exclude_services]

    for service in services:
        service_path = os.path.join(dir_path, service)
        description = "No description found"
        try:
            with open(service_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    if line.strip().startswith("Description="):
                        description = line.strip().split("=", 1)[1]
                        break
        except Exception as e:
            description = f"Error reading description: {e}"

        check = subprocess.run(["systemctl", "is-active", service], capture_output=True, text=True)
        status = "0" if check.returncode == 0 and check.stdout.strip() == "active" else "1"

        since_time = "N/A"
        try:
            result = subprocess.run(
                ["systemctl", "show", service, "--property=ActiveEnterTimestamp"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                line = result.stdout.strip()
                if "=" in line:
                    raw_time = line.split("=", 1)[1].strip()
                    if raw_time and raw_time.lower() != "n/a":
                        dt = datetime.strptime(raw_time, "%a %Y-%m-%d %H:%M:%S %Z")
                        since_time = dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            since_time = f"Error: {e}"

        services_list.append((service, description, status, since_time))

    services_data = services_list

    return [(service, status) for service, _, status, _ in services_list]


def non_monitoring_services(dir_path, exclude_services=[]) -> list:
    """Collects service name, description, and active since time (without status check)."""
    global list_non_monitoring

    services_list = []

    services = exclude_services
    
    for service in services:
        service_path = os.path.join(dir_path, service)

        if not os.path.exists(service_path):
            services_list.append((service, "Service file not found", "N/A"))
            continue

        description = "No description found"
        try:
            with open(service_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    if line.strip().startswith("Description="):
                        description = line.strip().split("=", 1)[1]
                        break
        except Exception as e:
            description = f"Error reading description: {e}"

        since_time = "N/A"
        try:
            result = subprocess.run(
                ["systemctl", "show", service, "--property=ActiveEnterTimestamp"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                line = result.stdout.strip()
                if "=" in line:
                    raw_time = line.split("=", 1)[1].strip()
                    if raw_time and raw_time.lower() != "n/a":
                        dt = datetime.strptime(raw_time, "%a %Y-%m-%d %H:%M:%S %Z")
                        since_time = dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            since_time = f"Error: {e}"

        services_list.append((service, description, since_time))

    list_non_monitoring = services_list

    return services_list


def send_message(message: str):
    """Internal function to send HTTP POST requests with error handling"""
    def send_request(url, json_data=None, data=None, headers=None):
        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                response = requests.post(url, json=json_data, data=data, headers=headers, timeout=(5, 20))
                response.raise_for_status()
                logger.info(f"Message successfully sent to {get_base_url(url)}. Status code: {response.status_code}")
                return
            except requests.exceptions.RequestException as e:
                logger.error(f"Attempt {attempt + 1}/{max_attempts} - Error sending message to {get_base_url(url)}: {e}")
                if attempt == max_attempts - 1:
                    logger.error(f"Failed to send message to {get_base_url(url)} after {max_attempts} attempts")
                else:
                    backoff_time = (2 ** attempt) + random.uniform(0, 1)
                    logger.warning(f"Retrying in {backoff_time:.2f} seconds...")
                    time.sleep(backoff_time)

    def to_html_format(message: str) -> str:
        """Convert Markdown-like syntax to HTML format."""
        message = ''.join(f"<b>{part}</b>" if i % 2 else part for i, part in enumerate(message.split('*')))
        return message.replace("\n", "<br>")

    def to_markdown_format(message: str, m_format: str) -> str:
        """Convert the message to the specified format"""
        if m_format == "html":
            return to_html_format(message)
        elif m_format == "markdown":
            return message.replace("*", "**")
        elif m_format == "text":
            return message.replace("*", "")
        elif m_format == "simplified":
            return message
        else:
            logger.error(f"Unknown format '{m_format}' provided. Returning original message.")
            return message

    for url, header, payload, format_message in zip(platform_webhook_url, platform_header, platform_payload, platform_format_message):
        data, ntfy = None, False
        formated_message = to_markdown_format(message, format_message)
        header_json = header if header else None

        for key in list(payload.keys()):
            if key == "title":
                delimiter = "<br>" if format_message == "html" else "\n"
                header, formated_message = formated_message.split(delimiter, 1)
                payload[key] = header.replace("*", "")
            elif key == "extras":
                formated_message = formated_message.replace("\n", "\n\n")
                payload["message"] = formated_message
            elif key == "data":
                ntfy = True
            payload[key] = formated_message if key in ["text", "content", "message", "body", "formatted_body", "data"] else payload[key]

        payload_json = None if ntfy else payload
        data = formated_message.encode("utf-8") if ntfy else None
        send_request(url, payload_json, data, header_json)


@app.route("/")
def index():
    try:
        services = sorted(services_data)
        exservices = sorted(list_non_monitoring)
        services_with_index = [(i+1, service[0], service[1], service[2], service[3]) for i, service in enumerate(services)]
        exservices_with_index = [(i+1, exservice[0], exservice[1], exservice[2]) for i, exservice in enumerate(exservices)]
        return render_template("index.html", 
                            hostname=hostname,
                            services=services_with_index,
                            exservices=exservices_with_index)
    except Exception as e:
        logger.error(f"Error in index route: {e}")
        return render_template("error.html", error=str(e)), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    try:
        return jsonify({"status": "healthy"}), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}.")
        return jsonify({"status": "error", "message": str(e)}), 500


def run_flask():
    """Run Flask app in a separate thread."""
    app.run(host='0.0.0.0', port=5152, debug=False, use_reloader=False)


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.realpath(__file__))
    config_file = os.path.join(base_dir, "config.json")
    exclude_file = os.path.join(base_dir, "exlude_service.json")
    dir_path = "/etc/systemd/system/multi-user.target.wants"

    config_json = {}
    startup_message = True
    default_dot_style = True
    min_repeat = 1

    if os.path.exists(exclude_file):
        try:
            with open(exclude_file, "r") as file:
                excluded_json = json.load(file)
                exclude_services = excluded_json.get("LIST", [])
        except (json.JSONDecodeError, OSError) as e:
            logger.error(f"Error reading exclude file: {e}")

    if os.path.exists(config_file):
        try:
            with open(config_file, "r") as file:
                config_json = json.load(file)
        except (json.JSONDecodeError, OSError) as e:
            logger.error(f"Error reading config file: {e}")

    startup_message = config_json.get("STARTUP_MESSAGE", startup_message)
    default_dot_style = config_json.get("DEFAULT_DOT_STYLE", default_dot_style)
    try:
        min_repeat = max(int(config_json.get("MIN_REPEAT", min_repeat)), 1)
    except (TypeError, ValueError):
        min_repeat = 1

    hostname = get_host_name()
    header = f"*{hostname}* (systemd)\n"

    dots = square_dots if not default_dot_style else round_dots
    green_dot, red_dot, white_dot, yellow_dot = dots["green"], dots["red"], dots["white"], dots["yellow"]

    no_messaging_keys = ["STARTUP_MESSAGE", "DEFAULT_DOT_STYLE", "MIN_REPEAT"]
    messaging_platforms = list(set(config_json.keys()) - set(no_messaging_keys))

    try:
        for platform in messaging_platforms:
            platform_conf = config_json.get(platform, {})
            if platform_conf.get("ENABLED", False):
                for key, value in platform_conf.items():
                    platform_key = f"platform_{key.lower()}"
                    current_value = globals().get(platform_key, [])
                    if not isinstance(current_value, list):
                        current_value = [current_value]
                    current_value.extend(value if isinstance(value, list) else [value])
                    globals()[platform_key] = current_value

        old_status = fetch_service_status(dir_path)
        non_monitoring_services(dir_path, exclude_services)

        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()

        logger.info("Service monitor started successfully")

    except Exception as e:
        logger.error(f"Failed to initialize: {str(e)}")
        sys.exit(1)


@repeat(every(min_repeat).minutes)
def CheckServices():
    """Periodically checks the status of services and sends a status update if there are changes."""
    global old_status
    new_status = fetch_service_status(dir_path)
    total_services = len(new_status)
    bad_services = 0
    message = ""

    result = list(set(new_status).difference(old_status))
    if not result:
        result = list(set(old_status).difference(new_status))

    if result:
        for service_name, service_status in result:
            if service_status == "1":
                bad_services += 1
                status_message = "inactive"
                message += f"{red_dot} *{service_name}*: {status_message}!\n"

        if bad_services == 0:
            message += f"{green_dot} monitoring service(s):\n"

    if old_status != new_status:
        ok_services = total_services - bad_services
        old_status = new_status

        if message:
            message += f"|ALL| - {total_services}, |OK| - {ok_services}, |BAD| - {bad_services}\n"
            send_message(f"{header}{message}")

while True:
    run_pending()
    time.sleep(1)