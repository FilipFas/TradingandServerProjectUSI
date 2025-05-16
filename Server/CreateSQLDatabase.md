# CREATE THE SQL DATABASE
This is a short guide on how to create the exact database that we used in our project. Of course, you can change it as you wish to better suit your needs.

### Install MySQL:
```bash
sudo apt-get update
sudo apt-get install mysql-server
sudo mysql_secure_installation
```
## Enter MySQL:
```bash
sudo mysql -u root -p
```
## Creating the database for the trading bot:
```sql
CREATE DATABASE trading_bot;
USE trading_bot;
```
## Creating the table for trade results:
```sql
CREATE TABLE trade_results (
    trade_id VARCHAR(36),
    ticker VARCHAR(10),
    date DATETIME,
    nav DECIMAL(15, 2),
    type VARCHAR(10),
    signal_price DECIMAL(15, 4),
    quantity DECIMAL(15, 8),
    opened DECIMAL(15, 4),
    closed DECIMAL(15, 4),
    vol DECIMAL(15, 4),
    entry_time DATETIME,
    closing_time DATETIME
);
```
## Move the CSV File to the Allowed Directory
MySQL has a security feature that restricts the directories from which you can load files using the LOAD DATA INFILE command. You need to move your CSV file to a directory allowed by MySQL.

### Find the allowed directory:
```bash
sudo mysql -u root -p
SHOW VARIABLES LIKE 'secure_file_priv';
```
This command will show the directory that MySQL is allowed to read from for the LOAD DATA INFILE command. Let's assume the directory is /var/lib/mysql-files/.

### Create a new CSV with just the last 50 values from trade_results.csv
Create the new CSV called trade_results_trimmed.csv
```bash
import pandas as pd

# Load the CSV file
df = pd.read_csv('/root/project/trade_results.csv')

# Exclude the last row and take the last 50 rows
if len(df) > 50:
    new_df = df.iloc[-51:-1]  # Excluding the very last row
else:
    new_df = df.iloc[:-1]  # In case there are fewer than 50 rows

# Save the new trimmed data to a new CSV file
new_df.to_csv('/root/project/trade_results_trimmed.csv', index=False)
```
Shell Script (update_database.sh)

Also save this script in /root/project/:

```bash
#!/bin/bash
# Run the Python script to process the CSV
python /root/project/process_csv.py

# Run the MySQL command to load data
mysql -u your_username -p'your_password' -D your_database -e "LOAD DATA INFILE '/root/project/trade_results_trimmed.csv' INTO TABLE trade_results FIELDS TERMINATED BY ',' ENCLOSED BY '\"' LINES TERMINATED BY '\n' IGNORE 1 ROWS (trade_id, ticker, date, nav, type, signal_price, quantity, opened, closed, vol, entry_time, closing_time);"
```
Make it executable:
```bash
chmod +x /root/project/update_database.sh
```

### Move your CSV file:
```bash
sudo mv /root/project/trade_results.csv /var/lib/mysql-files/
sudo chown mysql:mysql /var/lib/mysql-files/trade_results.csv
sudo chmod 644 /var/lib/mysql-files/trade_results.csv
mv /root/project/trade_results_trimmed.csv /var/lib/mysql-files/

```
## Load the Data into the Table
### Log in to MySQL:
```bash
sudo mysql -u root -p
```
### Use the correct database:
```sql
USE trading_bot;
```
### Run the LOAD DATA INFILE command:
```sql
LOAD DATA INFILE '/var/lib/mysql-files/trade_results_trimmed.csv'
INTO TABLE trade_results
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(trade_id, ticker, @dummy_date, nav, type, signal_price, quantity, opened, @dummy_closed, vol, @dummy_entry_time, @dummy_closing_time)
SET
    date = NOW(),  -- Set the current date and time for the 'date' field
    closed = NULLIF(@dummy_closed, ''),
    entry_time = NOW(),  -- Set the current date and time for 'entry_time'
    closing_time = NOW();  -- Set the current date and time for 'closing_time'

```

### Explanation:
1. **Create the Database and Table**: We first create the database and the `trade_results` table with the appropriate columns and data types.
2. **Move CSV File**: Move the CSV file to the directory allowed by MySQL.
3. **Load Data**: Use the `LOAD DATA INFILE` command to load the data from the CSV file into the `trade_results` table. The `SET` clause ensures that the date and time fields are properly formatted.

By following these steps, you can create an SQL database from the `trade_results.csv` file.
