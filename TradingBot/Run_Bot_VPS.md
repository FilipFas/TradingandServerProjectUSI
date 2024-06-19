# HOW TO RUN THE BOT ON VPS
## ADD CODE TO DIRECTORY

Start by adding the script for the trading bot in right directory (in our case 'project') in a Python 3 file.
```bash
nano bot.py
```
Add the script with relative functions to use:
```bash
nano functions.py
```

## SET UP AND ADD THE SERVICE
For a more robust and managed way to run your script, you can create a systemd service. This is particularly useful for scripts that need to run as background services.
### Create a systemd service file:
```bash
sudo nano /etc/systemd/system/trade_bot.service
```
### Add the following script:
```bash
[Unit]
Description=Trade Bot Service
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /path/to/your/script/bot.py
WorkingDirectory=/path/to/your/script
StandardOutput=append:/path/to/your/script/trade_bot.log
StandardError=append:/path/to/your/script/trade_bot_error.log
Restart=always

[Install]
WantedBy=multi-user.target
```
### Reload the systemd daemon:
```bash
sudo systemctl daemon-reload
```
### Enable and start the service:
```bash
sudo systemctl enable trade_bot.service
sudo systemctl start trade_bot.service
```
### Check the status of the service:
```bash
sudo systemctl status trade_bot.service
```
### View logs:
```bash
sudo journalctl -u trade_bot.service -f
```
