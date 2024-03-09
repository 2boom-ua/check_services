# check_services
services change status notifier

**config.json**
```
{
	"TELEGRAM": {
		"TOKEN": "your_token",
		"CHAT_ID": "your_chat_id"
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
ExecStart=/usr/bin/python3 /root/service_check/check_services.py

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
