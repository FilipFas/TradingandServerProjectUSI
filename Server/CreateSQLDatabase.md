# CREATE THE SQL DATABASE
This is a short guide on how to create the exact database that we used in our project. Of course, you can change it as you wish to better suit your needs.

### Install mySQL:
```bash
sudo apt-get update
sudo apt-get install mysql-server
sudo mysql_secure_installation
```
## Enter mySQL:
```bash
sudo mysql -u root -p
```
## Creating the database for the trading bot:
```bash
CREATE DATABASE trading_bot;
USE trading_bot;
```

## Move the CSV File to the Allowed Directory
MySQL has a security feature that restricts the directories from which you can load files using the LOAD DATA INFILE command. You need to move your CSV file to a directory allowed by MySQL.

### Find the allowed directory:
```bash

sudo mysql -u root -p
SHOW VARIABLES LIKE 'secure_file_priv';
```
This command will show the directory that MySQL is allowed to read from for the LOAD DATA INFILE command. Let's assume the directory is /var/lib/mysql-files/.

### Move your CSV file:

```bash
sudo mv /root/project/trade_results.csv /var/lib/mysql-files/
sudo chown mysql:mysql /var/lib/mysql-files/trade_results.csv
sudo chmod 644 /var/lib/mysql-files/trade_results.csv
```
## Load the Data into the Table
### Log in to MySQL:

```bash
sudo mysql -u root -p
```
### Use the correct database:

```bash
USE trading_bot
```
### Run the LOAD DATA INFILE command:
```bash
LOAD DATA INFILE '/var/lib/mysql-files/trade_results.csv'
INTO TABLE options
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(ticker, @date, nav, type, signal_price, quantity, opened, @closed, vol, @returns, @entry_time, @closing_time)
SET 
  date = STR_TO_DATE(@date, '%Y-%m-%d %H:%i:%s'),
  closed = NULLIF(@closed, ''),
  returns = NULLIF(@returns, ''),
  entry_time = STR_TO_DATE(NULLIF(@entry_time, ''), '%Y-%m-%d %H:%i:%s'),
  closing_time = STR_TO_DATE(NULLIF(@closing_time, ''), '%Y-%m-%d %H:%i:%s');
```
