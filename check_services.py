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
from schedule import every, repeat, run_pending
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


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


def fetch_service_status2() -> list:
    """Collects status of services"""
    dir_path = "/etc/systemd/system/multi-user.target.wants"
    services_list = []
    services = [
        file for file in os.listdir(dir_path)
        if file.endswith(".service") and os.path.islink(f"{dir_path}/{file}")
    ]
    services = [service for service in services if service not in exclude_services]

    for service in services:
        check = subprocess.run(["systemctl", "is-active", service], capture_output=True, text=True)
        status = "0" if check.returncode == 0 and check.stdout.strip() == "active" else "1"
        services_list.append(f"{service} {status}")

    return services_list
    
def fetch_service_status() -> list:
    """Collects status and descriptions of services"""
    dir_path = "/etc/systemd/system/multi-user.target.wants"
    services_list = []

    services = [
        file for file in os.listdir(dir_path)
        if file.endswith(".service") and os.path.islink(os.path.join(dir_path, file))
    ]
    services = [service for service in services if service not in exclude_services]

    for service in services:
        # Get service description
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

        # Get service status
        check = subprocess.run(["systemctl", "is-active", service], capture_output=True, text=True)
        status = "0" if check.returncode == 0 and check.stdout.strip() == "active" else "1"

        #services_list.append(f"{service} {description} {status}")
        services_list.append((service, description, status))

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


if __name__ == "__main__":
    config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.json")
    exclude_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "exlude_service.json")
    exclude_services = []
    monitoring_message = ""
    dots = {"green": "\U0001F7E2", "red": "\U0001F534"}
    square_dot = {"green": "\U0001F7E9", "red": "\U0001F7E5"}

    if os.path.exists(exclude_file):
        with open(exclude_file, "r") as file:
            excluded_json = json.loads(file.read())
        exclude_services = excluded_json["LIST"]

    if os.path.exists(config_file):
        with open(config_file, "r") as file:
            config_json = json.loads(file.read())
        try:
            startup_message = config_json.get("STARTUP_MESSAGE", True)
            default_dot_style = config_json.get("DEFAULT_DOT_STYLE", True)
            min_repeat = max(int(config_json.get("MIN_REPEAT", 1)), 1)
        except (json.JSONDecodeError, ValueError, TypeError, KeyError):
            default_dot_style = startup_message = True
            min_repeat = 1

        hostname = get_host_name()
        header = f"*{hostname}* (systemd)\n"

        if not default_dot_style:
            dots = square_dot

        green_dot, red_dot = dots["green"], dots["red"]
        no_messaging_keys = ["STARTUP_MESSAGE", "DEFAULT_DOT_STYLE", "MIN_REPEAT"]
        messaging_platforms = list(set(config_json) - set(no_messaging_keys))

        for platform in messaging_platforms:
            if config_json[platform].get("ENABLED", False):
                for key, value in config_json[platform].items():
                    platform_key = f"platform_{key.lower()}"
                    if platform_key in globals():
                        globals()[platform_key] = (
                            globals()[platform_key] if isinstance(globals()[platform_key], list)
                            else [globals()[platform_key]]
                        )
                        globals()[platform_key].extend(value if isinstance(value, list) else [value])
                    else:
                        globals()[platform_key] = value if isinstance(value, list) else [value]
                monitoring_message += f"- messaging: {platform.lower().capitalize()},\n"

        monitoring_message = "\n".join([*sorted(monitoring_message.splitlines()), ""])
        old_status = fetch_service_status()
        monitoring_message += (
            f"- monitoring: {len(old_status)} service(s),\n"
            f"- excluded: {len(exclude_services)} service(s),\n"
            f"- default dot style: {default_dot_style}.\n"
            f"- polling period: {min_repeat} minute(s)."
        )

        if all(value in globals() for value in ["platform_webhook_url", "platform_header", "platform_payload", "platform_format_message"]):
            logger.info("Started!")

            if startup_message:
                send_message(f"{header}services monitor:\n{monitoring_message}")
        else:
            logger.error("config.json is wrong")
            sys.exit(1)

    else:
        logger.error("config.json not found")
        sys.exit(1)


@repeat(every(min_repeat).minutes)
def CheckServices():
    """Periodically checks the status of services and sends a status update if there are changes."""
    global old_status
    new_status = fetch_service_status()
    total_services = len(new_status)
    bad_services = 0
    message = ""

    result = list(set(new_status).difference(old_status))
    if not result:
        result = list(set(old_status).difference(new_status))

    if result:
        #for service in result:
            #service_name, service_description, service_status = service.split(',')
        for service_name, service_description, service_status in result:
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
