## Service Monitoring Script
<div align="center">  
    <img src="https://github.com/2boom-ua/check_services/blob/main/check_services.jpg?raw=true" alt="" width="260" height="168">
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
  - Custom webhook
- **Configuration:** Easily configurable through JSON files for notification settings and excluded services.
- **Polling Period:** Adjustable polling interval to check service status.


### Requirements
- Python 3.x
- Docker installed and running
- Dependencies: `requests`, `schedule`

### Clone the repository:
```
git clone https://github.com/2boom-ua/check_services.git
cd check_services
```
### Install required Python packages:

```
pip install -r requirements.txt
```

## Edit config.json:
You can use any name and any number of records for each messaging platform configuration, and you can also mix platforms as needed. The number of message platform configurations is unlimited.

[Configuration examples for Telegram, Matrix, Apprise, Pumble, Mattermost, Discord, Ntfy, Gotify, Zulip, Flock, Slack, Rocket.Chat, Pushover, Pushbullet](docs/json_message_config.md)
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
            ...
        ],
        "PYLOAD": [
            {first JSON structure},
            {second JSON structure},
            ...
        ],
        "FORMAT_MESSAGE": [
            "markdown",
            "html",
            ...
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
 "DEFAULT_DOT_STYLE": true,
    "MIN_REPEAT": 1
```

| Item   | Required   | Description   |
|------------|------------|------------|
| DEFAULT_DOT_STYLE | true/false | Round/Square dots. |
| MIN_REPEAT | 1 | Set the poll period in minutes. Minimum is 1 minute. | 


## Edit exlude_service.json:
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

## Running as a Linux Service
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

## License

This project is licensed under the MIT License - see the [MIT License](https://opensource.org/licenses/MIT) for details.

## Author

- **2boom** - [GitHub](https://github.com/2boom-ua)
