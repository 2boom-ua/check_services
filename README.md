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

### Edit config.json:
A **config.json** file in the same directory as the script, and include your API tokens and configuration settings.
```
{
    "TELEGRAM": {
        "ON": false,
        "TOKENS": [
            "first tocken",
            "second tocken",
            "...."
        ],
        "CHAT_IDS": [
            "first chat_id",
            "second chat_id",
            "...."
        ]
    },
    "DISCORD": {
        "ON": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
        ]
    },
    "SLACK": {
        "ON": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
        ]
    },
    "GOTIFY": {
        "ON": false,
        "TOKENS": [
            "first tocken",
            "second tocken",
            "...."
        ],
        "CHAT_URLS": [
            "first server_url",
            "second server_url",
            "...."
        ]
    },
    "NTFY": {
        "ON": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
		]
    },
    "PUSHBULLET": {
        "ON": false,
        "TOKENS": [
            "first tocken",
            "second tocken",
            "...."
        ]
    },
    "PUSHOVER": {
        "ON": false,
        "TOKENS": [
            "first tocken",
            "second tocken",
            "...."
        ],
        "USER_KEYS": [
            "first user_key",
            "second user_key",
            "...."
        ]
    },
    "MATRIX": {
        "ON": false,
        "TOKENS": [
            "first tocken",
            "second tocken",
            "...."
        ],
        "SERVER_URLS": [
            "first server_url",
            "second server_url",
            "...."
        ],
        "ROOM_IDS": [
            "!first room_id",
            "!second room_id",
            "...."
        ]
    },
    "MATTERMOST": {
        "ON": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
        ]
    },
    "ROCKET": {
        "ON": false,
        "TOKENS": [
            "first tocken",
            "second tocken",
            "...."
        ],
		"USER_IDS": [
            "first user_id",
            "second user_id",
            "...."
        ],
        "SERVER_URLS": [
           "first server_url",
            "second server_url",
            "...."
        ],
		"CHANNEL_IDS": [
            "#first channel",
            "#second channel",
            "...."
        ]
    },
    "FLOCK": {
        "ON": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
		]
    },
    "PUMBLE": {
        "ON": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
		]
    },
    "ZULIP": {
        "ON": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
		]
    },
    "CUSTOM": {
        "ON": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
		]
        "STD_BOLDS" : [
            true,
            false,
            "...."
                ]
    },
    "DEFAULT_DOT_STYLE": true,
    "MIN_REPEAT": 1
}
```
| Item   | Required   | Description   |
|------------|------------|------------|
| STD_BOLDS | true/false | "**" **standard Markdown**, "*" *non-standard Markdown* |
| | | Standard Markdown use - Pumble, Mattermost, Discord, Ntfy, Gotify |
| | | Non-standard Markdown use - Telegram, Zulip, Flock, Slack, RocketChat, Flock. |
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
