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
A **config.json** file in the same directory as the script, and include your API tokens and configuration settings.

#### TELEGRAM
```
{
    "TELEGRAM": {
        "ENABLED": false,
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
```
| Item | Required | Description |
|------------|------------|------------|
| ENABLED | true/false | Enable or disable Telegram notifications |
| TOKENS | String | The token of your Telegram bot |
| CHAT_IDS | String | The ID of the Telegram chat where notifications will be sent |


#### DISCORD
```
    "DISCORD": {
        "ENABLED": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
        ]
    },
```
| Item | Required | Description |
|------------|------------|------------|
| ENABLED | true/false | Enable or disable Discord notifications |
| WEBHOOK_URLS | url | The URL of your Discord webhook |


#### SLACK
```
    "SLACK": {
        "ENABLED": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
        ]
    },
```
| Item | Required | Description |
|------------|------------|------------|
| ENABLED | true/false | Enable or disable Slack notifications |
| WEBHOOK_URLS | url | The URL of your Slack webhook |


#### GOTIFY
```
    "GOTIFY": {
        "ENABLED": false,
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
```
| Item | Required | Description |
|------------|------------|------------|
| ENABLED | true/false | Enable or disable Gotify notifications |
| SERVER_URLS | url | The URL of your Gotify server |
| TOKENS | String | The token for your Gotify application |


#### NTFY
```
    "NTFY": {
        "ENABLED": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
		]
    },
```
| Item | Required | Description |
|------------|------------|------------|
| ENABLED | true/false | Enable or disable Ntfy notifications |
| WEBHOOK_URLS | url | The URL of your self-hosted Ntfy server (or use https://ntfy.sh) |


#### PUSHBULLET
```
    "PUSHBULLET": {
        "ENABLED": false,
        "TOKENS": [
            "first tocken",
            "second tocken",
            "...."
        ]
    },
```
| Item | Required | Description |
|------------|------------|------------|
| ENABLED | true/false | Enable or disable Pushbullet notifications |
| TOKENS | String | The token for your Pushbullet application |


#### PUSHOVER
```
    "PUSHOVER": {
        "ENABLED": false,
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
```
| Item | Required | Description |
|------------|------------|------------|
| ENABLED | true/false | Enable or disable Pushover notifications |
| TOKENS | String | The token for your Pushover application |
| USER_KEYS | String | The user key for your Pushover application |


#### MATRIX
```
    "MATRIX": {
        "ENABLED": false,
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
```
| Item | Required | Description |
|------------|------------|------------|
| ENABLED | true/false | Enable or disable Matrix notifications |
| TOKENS | String | The token for your Matrix application |
| SERVER_URLS | url | The URL of your Matrix server |


#### MATTERMOST
```
    "MATTERMOST": {
        "ENABLED": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
        ]
    },
```
| Item | Required | Description |
|------------|------------|------------|
| ENABLED | true/false | Enable or disable Mattermost notifications |
| WEBHOOK_URLS | url | The URL of your Mattermost webhook |


#### ROCKET
```
    "ROCKET": {
        "ENABLED": false,
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
```
| Item | Required | Description |
|------------|------------|------------|
| ENABLED | true/false | Enable or disable Rocket.Chat notifications |
| SERVER_URLS | url | The URL of your Rocket.Chat server |
| TOKENS | String | The token for your Rocket.Chat application |
| CHANNEL_IDS | String | The ID of the Rocket.Chat channel where notifications will be sent |


#### FLOCK
```
    "FLOCK": {
        "ENABLED": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
		]
    },
```
| Item | Required | Description |
|------------|------------|------------|
| ENABLED | true/false | Enable or disable Flock notifications |
| WEBHOOK_URLS | url | The URL of your Flock webhook |


#### PUMBLE
```
    "PUMBLE": {
        "ENABLED": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
		]
    },
```
| Item | Required | Description |
|------------|------------|------------|
| ENABLED | true/false | Enable or disable Pumble notifications |
| WEBHOOK_URLS | url | The URL of your Pumble webhook |


#### ZULIP
```
    "ZULIP": {
        "ENABLED": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
		]
    },
```
| Item | Required | Description |
|------------|------------|------------|
| ENABLED | true/false | Enable or disable Zulip notifications |
| WEBHOOK_URLS | url | The URL of your Zulip webhook |


#### APPRISE
```
    "APPRISE": {
        "ENABLED": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
        ],
        "FORMAT_MESSAGES": [
            "markdown",
            "html",
            ...
        ]
    },
```
| Item | Required | Description |
|------------|------------|------------|
| ENABLED | true/false | Enable or disable Apprise notifications |
| WEBHOOK_URLS | url | The URL of your Apprise webhook |
| FORMATS | markdown,<br>html,<br>text,<br>asterisk | The format(s) to be used for the notification (e.g., markdown/html/text/asterisk) |


#### CUSTOM
```
    "CUSTOM": {
        "ENABLED": false,
        "WEBHOOK_URLS": [
            "first url",
            "second url",
            "...."
        ],
        "HEADERS": [
            {first JSON structure},
            {second JSON structure},
            ...
        ],
        "PYLOADS": [
            {first JSON structure},
            {second JSON structure},
            ...
        ],
        "FORMAT_MESSAGES": [
            "markdown",
            "html",
            ...
        ]
    },
```
| Item | Required | Description |
|------------|------------|------------|
| **CUSTOM** | | |
| ENABLED | true/false | Enable or disable Custom notifications |
| WEBHOOK_URLS | url | The URL of your Custom webhook |
| HEADERS | JSON structure | HTTP headers for each webhook request. This varies per service and may include fields like {"Content-Type": "application/json"}. |
| PAYLOAD | JSON structure | The JSON payload structure for each service, which usually includes message content and format. Like as  {"body": "message", "type": "info", "format": "markdown"}|
| FORMAT_MESSAGE | markdown,<br>html,<br>text,<br>asterisk | Specifies the message format used by each service, such as markdown, html, or other text formatting.|

- **markdown** - a simple text-based format with lightweight syntax for basic styling (Pumble, Mattermost, Discord, Ntfy, Gotify),
- **html** - a web-based format using tags for advanced text styling,
- **text** - raw text without any styling or formatting.
- **asterisk** - non-standard Markdown (Telegram, Zulip, Flock, Slack, RocketChat).

##### Examples for Telegram, Matrix, Apprise, Ntfy, Zulip, Gotify, Pushover, Pushbullet
```
    "CUSTOM": {
        "ENABLED": true,
        "WEBHOOK_URLS": [
            "https://api.telegram.org/bot{token}/sendMessage",
            "{server_url}/_matrix/client/r0/rooms/{room_id}/send/m.room.message?access_token={token}",
            "{server_url}/notify/{config_id}",
            "{server_url}/{subsribe}",
            "{organizattion}.zulipchat.com/api/v1/external/slack_incoming?api_key={api_key}",
            "{server_url}/message?token={token}",
            "https://api.pushover.net/1/messages.json",
            "https://api.pushbullet.com/v2/pushes"
        ],
        "HEADERS": [
            {},
            {"Content-Type": "application/json"},
            {"Content-Type": "application/json"},
            {"Content-Type": "application/json", "Priority": "1", "Markdown": "yes"},
            {},
            {},
            {"Content-type": "application/json"},
            {"Content-Type": "application/json", "Access-Token": "{token}"}
        ],
        "PYLOADS": [
            {"chat_id": "{chat_id}", "text": "message", "parse_mode": "Markdown"},
            {"msgtype": "m.text", "body": "message", "format": "org.matrix.custom.html", "formatted_body": "message"},
            {"body": "message", "type": "info", "format": "markdown"},
            {"data": "message"},
            {"text": "message"},
            {"title": "title", "message": "message", "priority": 0, "extras": {"client::display": {"contentType": "text/markdown"}}},
            {"token": "{token}", "user": "{user_key}", "title": "header", "message": "message", "html": "1"},
            {"type": "note", "title": "header", "body": "message"}
        ],
        "FORMAT_MESSAGES": [
            "asterisk",
            "html",
            "markdown",
            "markdown",
            "asterisk",
            "markdown",
            "markdown",
            "text"
        ]
    }
```

```
 "DEFAULT_DOT_STYLE": true,
    "MIN_REPEAT": 15
```

| Item   | Required   | Description   |
|------------|------------|------------|
| DEFAULT_DOT_STYLE | true/false | Round/Square dots. |
| MIN_REPEAT | 15 | Set the poll period in minutes. Minimum is 1 minute. | 


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
