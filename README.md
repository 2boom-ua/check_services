## Service Monitoring Script

### Overview

This Python script monitors the status of system services on a Linux machine. It checks the services managed by `systemd`, sending notifications through various messaging services when changes occur. 

### Features

- **Service Status Monitoring:** Regularly checks if specified services are active or inactive.
- **Notifications:** Sends alerts via:
  - Telegram
  - Discord
  - Slack
  - Gotify
  - Ntfy
  - Pushbullet
  - Pushover
  - Matrix
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
        "ON": true,
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
        "TOKENS": [
            "first tocken",
            "second tocken",
            "...."
        ]
    },
    "SLACK": {
        "ON": false,
        "TOKENS": [
            "first tocken",
            "second tocken",
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
        "ON": true,
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
    "PUSHBULLET": {
        "ON": false,
        "TOKENS": [
            "first tocken",
            "second tocken",
            "...."
        ]
    },
    "PUSHOVER": {
        "ON": true,
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
    "DEFAULT_DOT_STYLE": true,
    "MIN_REPEAT": 1
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
