# check_services
services change status notifier for Telegram, Discord, Gotify

*** [Gotify - a simple server for sending and receiving messages (in real time per WebSocket). ](https://github.com/gotify/server)

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
		"WEB": "web_your_channel"
	},
	"GOTIFY": {
		"ON": true,
		"TOKEN": "your_token",
		"WEB": "server_url"
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
Description=check active services
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
