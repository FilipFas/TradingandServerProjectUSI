# WEBSITE

## HOW TO CONNECT IT TO A DOMAIN:
### Configure DNS Settings
You need to set up an A (Address) record for your domain to point to the IP address.

Log in to your domain registrar's control panel: This is the website where you bought your domain name.
Find the DNS management section: This is sometimes called DNS Settings, Manage DNS, or similar.
Add an A record:
Name: Leave it blank or enter @ to point the root domain (e.g., example.com).
Type: Select A record.
Value: Enter 'Your IP Address.
TTL: Use the default value, or you can set it to a low value (like 600 seconds) for quicker propagation.

### Handle the Port Forwarding
DNS A records point only to an IP address, not to a specific port. To handle redirection to http://IP Address:8000, you need to configure your web server to redirect or proxy traffic from the default HTTP port (80) to port 8000. You can do this using a reverse proxy.

Install Nginx: If not already installed, you can install Nginx on your server.
```bash
sudo apt update
sudo apt install nginx
```
Edit the Nginx configuration file to set up the reverse proxy.
```bash
sudo nano /etc/nginx/sites-available/default
```
Add the following configuration:
```bash
server {
    listen 80;
    server_name yourdomain www.yourdomain;

    location ~ /.well-known/acme-challenge {
        allow all;
        root /var/www/html;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl;
    server_name yourdomain www.yourdomain;

    ssl_certificate /etc/letsencrypt/live/algotradingproject.online/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/algotradingproject.online/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    location / {
        proxy_pass http://IP ADDRESS;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

```
Replace yourdomain.com with your actual domain name.
Enable the configuration.
```bash
sudo ln -s /etc/nginx/sites-available/default /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```
Use tmux to Run Uvicorn Continuously:
If Uvicorn works when started manually, use tmux to keep it running continuously:

Install tmux if it’s not already installed:

```bash
sudo apt update
sudo apt install tmux
```
Start a new tmux session:
```bash
tmux new -s fastapi_session
```

Start Uvicorn inside the tmux session:
```bash
uvicorn website:app --host 0.0.0.0 --port 8000 --reload
```
Detach from the tmux session by pressing Ctrl + b, then d.

Uvicorn will continue running in the background. You can reattach to the session with:
```bash
tmux attach -t fastapi_session
```
