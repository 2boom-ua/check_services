## Service Monitoring Script
<div align="center">  
    <img src="https://github.com/2boom-ua/check_services/blob/main/check_services.jpg?raw=true" alt="" width="629" height="661">
</div>

### Overview

This Python script monitors the status of system services on a Linux machine. It checks the services managed by `systemd`, forwarding notifications through various messaging services when the crevice status changes detected. 

### Features

- **Service Status Monitoring:** Regularly checks if specified services are active or inactive.
- **Real-time notifications with support for multiple accounts** via:
  - Telegram
  - Discord
  - Slack
  - Gotify
  - Ntfy
  - Pushbullet
  - Pushover
  - Rocket.chat
  - Matrix
  - Mattermost
  - Floc
  - Pumble
  - Zulip
  - Apprise
  - Webntfy
  - Custom webhook
- **Configuration:** Easily configurable through JSON files for notification settings and excluded services.
- **Polling Period:** Adjustable polling interval to check service status.

### View
https://your_domain_name or http://server_ip:5152

### Requirements
- Python 3.x
- Dependencies: `requests`, `schedule`

### Edit config.json:
You can use any name and any number of records for each messaging platform configuration, and you can also mix platforms as needed. The number of message platform configurations is unlimited.

[Configuration examples for Telegram, Matrix, Apprise, Pumble, Mattermost, Discord, Ntfy, Gotify, Zulip, Flock, Slack, Rocket.Chat, Pushover, Pushbullet, Webntfy](docs/json_message_config.md)
```
    "CUSTOM_NAME": {
        "ENABLED": false,
        "WEBHOOK_URL": [
            "first url",
            "second url",
            "...."
        ],
        "HEADER": [
            {first JSON structure},
            {second JSON structure},
            {....}
        ],
        "PAYLOAD": [
            {first JSON structure},
            {second JSON structure},
            {....}
        ],
        "FORMAT_MESSAGE": [
            "markdown",
            "html",
            "...."
        ]
    },
```
| Item | Required | Description |
|------------|------------|------------|
| ENABLED | true/false | Enable or disable Custom notifications |
| WEBHOOK_URL | url | The URL of your Custom webhook |
| HEADER | JSON structure | HTTP headers for each webhook request. This varies per service and may include fields like {"Content-Type": "application/json"}. |
| PAYLOAD | JSON structure | The JSON payload structure for each service, which usually includes message content and format. Like as  {"body": "message", "type": "info", "format": "markdown"}|
| FORMAT_MESSAGE | markdown,<br>html,<br>text,<br>simplified | Specifies the message format used by each service, such as markdown, html, or other text formatting.|

- **markdown** - a text-based format with lightweight syntax for basic styling (Pumble, Mattermost, Discord, Ntfy, Gotify),
- **simplified** - simplified standard Markdown (Telegram, Zulip, Flock, Slack, RocketChat).
- **html** - a web-based format using tags for advanced text styling,
- **text** - raw text without any styling or formatting.

```
"STARTUP_MESSAGE": true,
"DEFAULT_DOT_STYLE": true,
"MIN_REPEAT": 1
```

| Item   | Required   | Description   |
|------------|------------|------------|
| STARTUP_MESSAGE | true/false | On/Off startup message. |
| DEFAULT_DOT_STYLE | true/false | Round/Square dots. |
| MIN_REPEAT | 1 | Set the poll period in minutes. Minimum is 1 minute. | 


### Edit exlude_service.json:
A **exlude_service.json** file in the same directory as the script, include the name of the services that aren't monitored. ***the presence of the file is not necessary***
```
{
   "LIST": [
      "fisrtservicename.service",
      "secondservicename.service",
      "..."
   ]
}
```

### Clone the repository:
```
git clone https://github.com/2boom-ua/check_services.git
cd check_services
```
### Install required Python packages:
```
pip install -r requirements.txt
```
## Docker
```bash
  docker build -t check_services .
```
or
```bash
  docker pull ghcr.io/2boom-ua/check_services:latest
```
### Dowload and edit config.json and exlude_service.json
```bash
curl -L -o ./config.json  https://raw.githubusercontent.com/2boom-ua/check_services/main/config.json
```
```bash
curl -L -o ./exlude_service.json  https://raw.githubusercontent.com/2boom-ua/check_services/main/exlude_service.json
```
### docker-cli
```bash
docker run --net host --name check_services --privileged -v ./config.json:/check_services/config.json -v ./exlude_service.json:/check_services/exlude_service.json -v /etc/systemd/system/multi-user.target.wants:/etc/systemd/system/multi-user.target.wants:ro -v /var/run/dbus:/var/run/dbus:ro -v /run/systemd/system:/run/systemd/system:ro -e DBUS_SYSTEM_BUS_ADDRESS=unix:path=/var/run/dbus/system_bus_socket -e TZ=UTC --restart always ghcr.io/2boom-ua/check_services:latest
```
### docker-compose
```
services:
  check_services:
    container_name: check_services
    image: ghcr.io/2boom-ua/check_services:latest
    privileged: true
    network_mode: host
    volumes:
      - ./config.json:/check_services/config.json
      - ./exlude_service.json:/check_services/exlude_service.json
      - /etc/systemd/system/multi-user.target.wants:/etc/systemd/system/multi-user.target.wants:ro
      - /var/run/dbus:/var/run/dbus:ro
      - /run/systemd/system:/run/systemd/system:ro
      - /etc/systemd/system:/etc/systemd/system:ro
      - /run/systemd/system:/run/systemd/system:ro
    environment:
      - DBUS_SYSTEM_BUS_ADDRESS=unix:path=/var/run/dbus/system_bus_socket
      - TZ=Etc/UTC
    restart: always
```

```bash
docker-compose up -d
```
---
### Running as a Linux Service
You can set this script to run as a Linux service for continuous monitoring.

Create a systemd service file:
```
nano /etc/systemd/system/check_services.service
```
Add the following content:
```
[Unit]
Description=services state change monitor
After=multi-user.target

[Service]
Type=simple
Restart=always
ExecStart=/usr/bin/python3 /opt/check_services/check_services.py

[Install]
WantedBy=multi-user.target
```
```
systemctl daemon-reload
```
```
systemctl enable check_services.service
```
```
systemctl start check_services.service
```
### License

This project is licensed under the MIT License - see the [MIT License](https://opensource.org/licenses/MIT) for details.

### Author

- **2boom** - [GitHub](https://github.com/2boom-ua)
