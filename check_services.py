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
from flask import Flask, render_template, url_for, jsonify, make_response
from threading import Thread

platform_webhook_url = []
platform_header = []
platform_payload = []
platform_format_message = []
services_data = []
exclude_services = []
list_non_monitoring = []
old_status = []

green_dot = red_dot = white_dot = yellow_dot = ""

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
    """Get base url"""
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


def send_message(message: str):
    """Send HTTP POST requests with retry logic."""
    def send_request(url, json_data=None, data=None, headers=None):
        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                response = requests.post(url, json=json_data, data=data, headers=headers, timeout=(5, 20))
                response.raise_for_status()
                return
            except requests.exceptions.RequestException as e:
                logger.error("error_send_request_failed" + f" {attempt + 1}/{max_attempts} - {url}: {e}")
                if attempt == max_attempts - 1:
                    logger.error("error_send_request_max_attempts" + f" {url}")
                else:
                    backoff_time = (2 ** attempt) + random.uniform(0, 1)
                    logger.warning("log_retrying" + f" {backoff_time:.2f} seconds...")
                    time.sleep(backoff_time)

    def to_html_format(message: str) -> str:
        message = ''.join(f"<b>{part}</b>" if i % 2 else part for i, part in enumerate(message.split('*')))
        return message.replace("\n", "<br>")

    def to_markdown_format(message: str, markdown_type: str) -> str:
        formatters = {
            "html": lambda msg: to_html_format(msg),
            "markdown": lambda msg: msg.replace("*", "**"),
            "text": lambda msg: msg.replace("*", ""),
            "simplified": lambda msg: msg,
        }
        formatter = formatters.get(markdown_type)
        if formatter:
            return formatter(message)
        logger.error("error_unknown_format" + f" '{markdown_type}'")
        return message

    for url, header, payload, format_message in zip(platform_webhook_url, platform_header, platform_payload, platform_format_message):
        data, ntfy = None, False
        formatted_message = to_markdown_format(message, format_message)
        header_json = header if header else None

        if isinstance(payload, dict):
            for key in list(payload.keys()):
                if key == "title":
                    delimiter = "<br>" if format_message == "html" else "\n"
                    header, formatted_message = formatted_message.split(delimiter, 1)
                    payload[key] = header.replace("*", "")
                elif key == "extras":
                    formatted_message = formatted_message.replace("\n", "\n\n")
                    payload["message"] = formatted_message
                elif key == "data":
                    ntfy = True
                payload[key] = formatted_message if key in ["text", "content", "message", "body", "formatted_body", "data"] else payload[key]

        payload_json = None if ntfy else payload
        data = formatted_message.encode("utf-8") if ntfy else None
        send_request(url, payload_json, data, header_json)


def get_enabled_not_running_services():
    """Returns a list of systemd services that are enabled but not running."""
    try:
        enabled_cmd = ["systemctl", "list-unit-files", "--type=service", "--state=enabled"]
        enabled_output = subprocess.check_output(enabled_cmd, text=True)

        enabled_services = [
            line.split()[0] for line in enabled_output.splitlines()
            if line and "enabled" in line and ".service" in line
        ]

        not_running_services = []
        for service in enabled_services:
            active_cmd = ["systemctl", "is-active", service]
            try:
                active_output = subprocess.check_output(active_cmd, text=True).strip()
                if active_output != "active":
                    not_running_services.append(service)
            except subprocess.CalledProcessError:
                not_running_services.append(service)
        
        return not_running_services
    
    except subprocess.CalledProcessError as e:
        print(f"Error executing systemctl: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []


def fetch_service_status() -> list:
    """Fetches the status of all enabled services excluding specified services."""
    global services_data
    services_list = []

    try:
        result = subprocess.run(
            ["systemctl", "list-unit-files", "--type=service", "--state=enabled", "--no-pager", "--no-legend"],
            capture_output=True, text=True, check=True
        )
        services = [line.split()[0] for line in result.stdout.splitlines() if line.strip()]
    except Exception as e:
        services_data = []
        return [(f"Error: {e}", "1")]

    services = [service for service in services if service not in exclude_services]

    for service in services:
        description = "No description found"
        try:
            desc = subprocess.run(
                ["systemctl", "show", service, "--property=Description"],
                capture_output=True, text=True
            )
            if desc.returncode == 0 and "=" in desc.stdout:
                description = desc.stdout.strip().split("=", 1)[1]
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
                        try:
                            if raw_time.count(" ") >= 3:
                                dt = datetime.strptime(raw_time, "%a %Y-%m-%d %H:%M:%S %Z")
                            else:
                                dt = datetime.strptime(raw_time, "%Y-%m-%d %H:%M:%S")
                            since_time = dt.strftime("%Y-%m-%d %H:%M:%S")
                        except Exception:
                            since_time = raw_time
        except Exception as e:
            since_time = f"Error: {e}"

        services_list.append((service, description, status, since_time))

    services_data = services_list
    return [(service, status) for service, _, status, _ in services_list]


def non_monitoring_services(exclude_services=[]) -> list:
    """Returns information about services that are excluded from monitoring."""
    global list_non_monitoring
    services_list = []

    if not exclude_services:
        list_non_monitoring = []
        return []

    for service in exclude_services:
        if not service.endswith(".service"):
            service += ".service"

        description = "No description found"
        try:
            desc = subprocess.run(
                ["systemctl", "show", service, "--property=Description"],
                capture_output=True, text=True
            )
            if desc.returncode == 0 and "=" in desc.stdout:
                description = desc.stdout.strip().split("=", 1)[1]
        except Exception as e:
            description = f"Error reading description: {e}"

        since_time = "Skipped service"
        services_list.append((service, description, since_time))

    list_non_monitoring = services_list
    return services_list


@app.after_request
def add_security_headers(response):
    # Recommended security headers
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@app.route("/")
def index():
    try:
        services = sorted(services_data)
        exservices = sorted(list_non_monitoring)
        services_with_index = [(i+1, service[0], service[1], service[2], service[3]) for i, service in enumerate(services)]
        exservices_with_index = [(i+1, exservice[0], exservice[1], exservice[2]) for i, exservice in enumerate(exservices)]
        return render_template("index.html", hostname=hostname, services=services_with_index, exservices=exservices_with_index)
    except Exception as e:
        logger.error(f"Error in index route: {e}")
        return render_template("error.html", error=str(e)), 500


def run_flask():
    app.run(host='0.0.0.0', port=5152, debug=False, use_reloader=False)


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.realpath(__file__))
    config_file = os.path.join(base_dir, "config.json")
    monitoring_message = ""
    config_json = {}
    startup_message = False
    default_dot_style = True
    notify_enabled = False
    min_repeat = 1

    dots = square_dots if not default_dot_style else round_dots
    green_dot, red_dot, white_dot, yellow_dot = dots["green"], dots["red"], dots["white"], dots["yellow"]
    
    hostname = get_host_name()
    header = f"*{hostname}* (systemd)\n"

    if os.path.exists(config_file):
        with open(config_file, "r") as file:
            config_json = json.loads(file.read())
        try:
            startup_message = config_json.get("STARTUP_MESSAGE", False)
            default_dot_style = config_json.get("DEFAULT_DOT_STYLE", True)
            notify_enabled = config_json.get("NOTIFY_ENABLED", False)
            if not notify_enabled:
                startup_message = False
            no_messaging_keys = ["STARTUP_MESSAGE", "DEFAULT_DOT_STYLE", "NOTIFY_ENABLED"]
            messaging_platforms = list(set(config_json) - set(no_messaging_keys))
            for platform in messaging_platforms:
                if config_json[platform].get("ENABLED", False):
                    for key, value in config_json[platform].items():
                        platform_key = f"platform_{key.lower()}"
                        if platform_key in globals():
                            globals()[platform_key] = (globals()[platform_key] if isinstance(globals()[platform_key], list) else [globals()[platform_key]])
                            globals()[platform_key].extend(value if isinstance(value, list) else [value])
                        else:
                            globals()[platform_key] = value if isinstance(value, list) else [value]
                    monitoring_message += f"- messaging: {platform.lower().capitalize()},\n"
            monitoring_message += (
                f"- default dot style: {default_dot_style}.\n"
                f"- polling period: {min_repeat} minute(s)."
            )

            if all(value in globals() for value in ["platform_webhook_url", "platform_header", "platform_payload", "platform_format_message"]):
                logger.info(f"Started!")
                if startup_message:
                    send_message(f"{header}systemd monitor:\n{monitoring_message}")
            else:
                logger.error("config.json is wrong")

        except (json.JSONDecodeError, ValueError, TypeError, KeyError):
            logger.error("Error or incorrect settings in config.json. Default settings will be used.")
    else:
        logger.error("config.json not found")

    exclude_services = get_enabled_not_running_services()
    old_status = fetch_service_status()
    non_monitoring_services(exclude_services)

    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()


@repeat(every(min_repeat).minutes)
def check_services():
    global old_status

    new_status = fetch_service_status()
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
            if notify_enabled:
                send_message(f"{header}{message}")

while True:
    run_pending()
    time.sleep(1)