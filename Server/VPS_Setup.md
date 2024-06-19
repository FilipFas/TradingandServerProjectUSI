# VIRTUAL PRIVATE SERVER (VPS) SETUP

## Open the Terminal (OS) or cmd (Windows)

Insert the following code to connect to the VPS via SSH:

```bash
ssh root@[Your VPS IP Address]
```

To enhance security, consider changing the SSH port. Use the following command:
```bash
ssh -p 7010 root@[Your VPS IP Adress]
```
Next, limit the outgoing and incoming traffic on the VPS:
```bash
sudo apt install iftop

sudo iftop  # to monitor outgoing/incoming traffic on the VPS

# Limit incoming traffic
sudo iptables -A INPUT -p tcp --sport 7010 -m hashlimit --hashlimit-name limit_port_7010 --hashlimit-above 300kbps --hashlimit-mode srcip --hashlimit-burst 50 --hashlimit-htable-expire 300000 -j DROP  

# Limit outgoing traffic
sudo iptables -A OUTPUT -p tcp --sport 7010 -m hashlimit --hashlimit-name limit_port_7010 --hashlimit-above 300kbps --hashlimit-mode srcip --hashlimit-burst 50 --hashlimit-htable-expire 300000 -j DROP  

sudo iptables-save > /etc/iptables/rules.v4  # Save the new rule
sudo iptables -l  # View all rules
```
## Add SQLite3, Python3, pip and cron to the server
Install SQLite3, Python3, pip and cron if not already installed:
```bash
sudo apt-get update
sudo apt install sqlite3
sudo apt install python3
sudo apt-get install -y python3-pip
sudo apt-get install cron
```
## Install Python modules:
```bash
pip3 install pandas
pip3 install numpy
pip3 install sqlite3
```
## Create a new directory
Create a new directory named 'project' on the VPS:

```bash
mkdir project
```
## Cron-job setup
Create a cronjob to download and store data. Access the crontab page and then execute the copy and paste the commands that follows.
```bash
crontab -e
```
## Running the API
After installing all the dependancies, run the python program with 'nano'
```bash
nano main.py
```
Than go to http://[Your VPS IP Adress]:8000 to see the results

IMPORTANT: be sure that the page is always accessible
