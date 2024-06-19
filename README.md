# Trading and Server Project USI

This project has been developed according to the instruction given by Prof. Peter Gruber PhD, as part of the course "Programming in Finance and Economics II" at Università della Svizzera Italiana.

## Project Description
The TradingProject aims to leverage a Virtual Private Server (VPS) to execute an algorithmic trading bot. The bot is designed to interact with the Crypto market, execute trades based on a predefined strategy, and store the results for analysis. Additionally, the project includes functionality to display these trading results in a user-friendly format.

Results can be consulted here: https\\www.algotradingproject.online

Folder structure:
```bash
TradingandServerProjectUSI/
    Server/
        Website/
    TradingBot/
    README.md
    LICENSE
```
## Technologies Used
Programming Languages: Python, HTML, SQL.

Frameworks/Libraries: pandas, numpy, Flask, Binance, FastAPI, pathlib, graph, jinja2, matplotlib, io, base64

Infrastructure: Virtual Private Server (VPS) Linux environment, provided by Racknerd.



## Contributors
- Fasoli Filippo, Student Master in Finance, Minor Quantitative Finance (fasolfi@usi.ch)
- Fornaio Angelo, Student Master in Finance, Minor Quantitative Finance
- Morando Marco, Student Master in Finance, Minor Digital Finance

## License
Here you can access the license: [MIT License](/LICENSE)


## Installation and Usage
### VPS Server
Firstly, it's important to buy the right VPS. We suggest purchasing one with at least 2GB of RAM, 50GB of SSD, and 1 IPv4 address. Here you can find some good deals ([RackNerd](https://www.racknerd.com/BlackFriday/)). 

*Disclaimer: We're not affiliated with nor sponsored by RackNerd, and we do not receive any referral benefits for mentioning them.*

After that you need to setup your VPS to better suit the purpose of the project. ([Here](Server/VPS_Setup.md)) the instructions that we used.

Other informations on how we setup our SQL database on the VPS can be found [here](Server/CreateSQLdatabase.md).

#### Website
We used the powefull Python package [FastAPI](https://fastapi.tiangolo.com/) for most of the work on the VPS, to create the website and connect it with the VPS. [Here](/Server/Website) you can find how to replicate our steps.

To furthere proceed with the project we purchased a domain for our website from [Namecheap](https://www.namecheap.com/domains) and connected it with a SSH Certificate to update the website from http to https (a more secure protocol). To do that we used the free platform [Certbot](https://certbot.eff.org), that not only provide a SSH Certificate for free but also present all the necessary steps to install it in a simple way.

Complete this steps the website is only and is now accessible at the following [link](https://www.algotradingproject.online).



### Algotrading Bot
The Algotrading Bot runs using Python, before running it check if all the requirements are correctly installed ([Bot Requirements](/TradingBot/requirements.txt)). If not sure, run the following code:
```bash
pip install -r requirements.txt
```
To access the Binance API, and so to run the bot, is important to create new API keys and update the [relative file](/TradingBot/api_keys.json) containing them. Here the [link](https://testnet.binancefuture.com/en/futures/BTCUSDT) to create the API keys (requires the creation of an account to access).

In the dedicated page is possible to check each function and what it does ([Functions](/TradingBot/functions.py)). After that you can run the program contained in [main.py](/TradingBot/main.py). 

*Changes can be done but we reserve them to the curiosity of the reader. We also suggest, when making changes, to double check everything to avoid unpleasent errors.*

## Project Status
The TradingProject is currently under active development. We are continuously refining the algorithmic trading strategy and enhancing the display of trading results. 

*The VPS and the website will be running until April 2025, after that the contracts with the VPS and domain providers will expire and the results will be no more accessible from the website page.*

*Also the website will be accessible only during the following hours (from 6:00 to 18:00 CET) to avoid excessive bandwidth usage.*

## Contact Information
For inquiries, feedback, or contributions, please contact fasolfi@usi.ch.

## Credits and Attribution
Financial data sourced from BinanceAPI .
Special thanks to Prof. Peter Gruber PhD for the support during the development of this project.

## Disclaimer

**Important Notice**: This project is solely focused on paper trading, where simulated trades are executed without real money. We do not provide any investment advice, nor do we endorse or suggest any specific trading strategies. 

It's crucial to understand that financial markets carry inherent risks, and there's the potential to lose all invested capital or more. Before engaging in any trading or investment activities, it's essential to obtain proper education, understand the risks involved, and consider consulting with a qualified financial advisor. 

By using this project or any information provided herein, users acknowledge and agree that they are solely responsible for their trading decisions and any outcomes that may result. We disclaim any liability for losses incurred through the use of this project or reliance on its content. Use discretion and trade responsibly.

