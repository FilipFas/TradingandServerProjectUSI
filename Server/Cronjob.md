# HOW TO AUTOMATE THE DATABASE POPULATION WITH CRONJOB

To set up a cron job that constantly populates the database with data from the CSV file, you will need to create a script that performs the data loading operation and then set up a cron job to run this script at regular intervals.

## Create the Data Loading Script
Create a Python script, load_csv_to_db.py, to load data from the CSV file into the MySQL database.
```bash
import mysql.connector
from mysql.connector import Error
```
### Define the function to load data
```bash
def load_data():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='trading_bot',
            user='root',
            password='your_mysql_root_password'  # replace with your MySQL root password
        )

        if connection.is_connected():
            cursor = connection.cursor()
            
            # SQL command to load data
            load_data_sql = """
            LOAD DATA INFILE '/var/lib/mysql-files/trade_results.csv'
            INTO TABLE options
            FIELDS TERMINATED BY ','
            ENCLOSED BY '"'
            LINES TERMINATED BY '\\n'
            IGNORE 1 ROWS
            (ticker, @date, nav, type, signal_price, quantity, opened, @closed, vol, @returns, @entry_time, @closing_time)
            SET 
                date = STR_TO_DATE(@date, '%Y-%m-%d %H:%i:%s'),
                closed = NULLIF(@closed, ''),
                returns = NULLIF(@returns, ''),
                entry_time = STR_TO_DATE(NULLIF(@entry_time, ''), '%Y-%m-%d %H:%i:%s'),
                closing_time = STR_TO_DATE(NULLIF(@closing_time, ''), '%Y-%m-%d %H:%i:%s');
            """
            cursor.execute(load_data_sql)
            connection.commit()
            print("Data loaded successfully from CSV to MySQL table")

    except Error as e:
        print(f"Error: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")
# Run the function
if __name__ == "__main__":
    load_data()
```
## Make the Script Executable
Make sure the script has execute permissions:

```bash
chmod +x /path/to/load_csv_to_db.py
```
## Set Up the Cron Job
Edit the cron jobs for your user by running:

```bash
crontab -e
```
Add the following line to schedule the script to run at regular intervals. For example, to run the script every 5 minutes:
```bash
*/5 * * * * /usr/bin/python3 /path/to/load_csv_to_db.py >> /path/to/load_csv_to_db.log 2>&1
```
This cron job entry does the following:
```bash
*/5 * * * *: Runs the command every 5 minutes.
/usr/bin/python3: Specifies the Python interpreter.
/path/to/load_csv_to_db.py: Path to your data loading script.
>> /path/to/load_csv_to_db.log 2>&1: Appends standard output and standard error to a log file for debugging.
>>
```
### Verify the Cron Job
You can check if your cron job has been set up correctly by listing your cron jobs:
```bash
crontab -l
```
### Monitor the Log File
Check the log file specified in the cron job to ensure that the script runs correctly and captures any errors:
```bash
tail -f /path/to/load_csv_to_db.log
```
## Final Notes
Path Adjustments: Ensure all paths in the script and cron job are correct and accessible.
Permissions: Ensure the MySQL user has the necessary permissions to load the data from the CSV file.
Error Handling: The script logs errors and ensures the MySQL connection is closed properly.
By setting up this cron job, your database will be regularly updated with the latest data from the CSV file.
