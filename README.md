# check_services
services status informer for Telegram, Discord, Gotify, Ntfy, Pushbullet? Slack  as linux service

```
pip install -r requirements.txt
```

**config.json**
```
{
	"TELEGRAM": {
		"ON": true,
		"TOKEN": "your_token",
		"CHAT_ID": "your_chat_id"
	},
	"DISCORD": {
		"ON": true,
		"WEB": "web_hook_url"
	},
	"GOTIFY": {
		"ON": true,
		"TOKEN": "your_token",
		"WEB": "server_url"
	},
	"NTFY": {
		"ON": true,
		"SUB": "your_subscribe",
		"WEB": "server_url"
	},
	"PUSHBULLET": {
		"ON": false,
		"API": "your_api_key"
	},
	"SLACK": {
		"ON": true,
		"WEB": "web_hook_url"
	},
	"MIN_REPEAT": 1
}
```
**make as service**
```
nano /etc/systemd/system/check_services.service
```
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
