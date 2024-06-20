from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pathlib import Path
from graph import generate_graph_html  # function defined in graph.py
import pandas as pd
import mysql.connector

app = FastAPI()

# Database connection settings
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = 'insert your password'
DB_NAME = 'trading_bot'

# Define the HTML content
@app.get("/", response_class=HTMLResponse)
async def read_root():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ALGOTRADING STRATEGIES ON CRYPTO</title>
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css" rel="stylesheet">
        <style>
            body {
                font-family: 'Roboto', sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
                color: #333;
            }
            nav {
                background-color: #1f2937;
                color: #fff;
                padding: 15px 20px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                position: fixed;
                width: 100%;
                top: 0;
                z-index: 1000;
                transition: background-color 0.3s ease;
            }
            nav ul {
                list-style: none;
                display: flex;
                justify-content: center;
                padding: 0;
                margin: 0;
            }
            nav ul li {
                margin: 0 15px;
            }
            nav ul li a {
                color: #fff;
                text-decoration: none;
                font-weight: bold;
                transition: color 0.3s ease;
            }
            nav ul li a:hover {
                color: #3b82f6;
            }
            nav.scrolled {
                background-color: rgba(31, 41, 55, 0.9);
            }
            .hero {
                background: url('https://source.unsplash.com/1600x900/?cryptocurrency,finance') no-repeat center center/cover;
                height: 70vh;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #fff;
                text-align: center;
                padding: 0 20px;
                position: relative;
                z-index: 1;
            }
            .hero::after {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
                z-index: -1;
            }
            .hero h1 {
                font-size: 3em;
                margin-bottom: 20px;
            }
            .hero p {
                font-size: 1.2em;
                margin-bottom: 20px;
            }
            .btn-primary {
                background-color: #3b82f6;
                color: #fff;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-size: 1em;
                cursor: pointer;
                transition: background-color 0.3s ease;
                text-transform: uppercase;
            }
            .btn-primary:hover {
                background-color: #2563eb;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            .section {
                background-color: #fff;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                margin: 20px 0;
                padding: 40px 20px;
                text-align: center;
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }
            .section:hover {
                transform: translateY(-10px);
                box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
            }
            .section h2 {
                margin-top: 0;
                font-size: 2.5em;
                color: #1f2937;
            }
            .section p {
                font-size: 1.1em;
                color: #4b5563;
                margin-bottom: 20px;
            }
            .section .btn-secondary {
                background-color: #e2e8f0;
                color: #1f2937;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-size: 1em;
                cursor: pointer;
                transition: background-color 0.3s ease;
                text-transform: uppercase;
            }
            .section .btn-secondary:hover {
                background-color: #cbd5e1;
            }
            footer {
                background-color: #1f2937;
                color: #fff;
                padding: 20px 0;
                text-align: center;
                margin-top: 40px;
            }
            footer p {
                margin: 0;
                font-size: 0.9em;
            }
            footer a {
                color: #3b82f6;
                text-decoration: none;
            }
            footer a:hover {
                text-decoration: underline;
            }
        </style>
        <script>
            window.addEventListener('scroll', () => {
                const nav = document.querySelector('nav');
                if (window.scrollY > 50) {
                    nav.classList.add('scrolled');
                } else {
                    nav.classList.remove('scrolled');
                }
            });
        </script>
    </head>
    <body>
        <nav>
            <ul>
                <li><a href="#hero">Home</a></li>
                <li><a href="#strategy">Strategy</a></li>
                <li><a href="#graphics">Graphics</a></li>
                <li><a href="/docs">API Docs</a></li>
            </ul>
        </nav>
        <div id="hero" class="hero">
            <div>
                <h1>ALGOTRADING STRATEGY ON CRYPTO</h1>
                <p>Our API provides real time performance for a trading that uses Bollinger Bands and RSI as indicators.</p>
                <button class="btn-primary" onclick="location.href='/docs'">Explore API Documentation</button>
            </div>
        </div>
        <div class="container">
            <div id="strategy" class="section">
                <h2>BOLLINGER-RSI CONVERGENCE STRATEGY</h2>
                <p>This strategy applies a unique combination of Bollinger Bands and the Relative Strength Index (RSI) to identify optimal trading opportunities in BTC.</p>
                <p>Click here to see the code for replicating this strategy.</p>
                <button class="btn-secondary" onclick="window.location.href='https://github.com/FilipFas/TradingandServerProjectUSI';">Try Strategy</button>
            </div>

            <div id="graphics" class="section">
                <h2>GRAPHICS</h2>
                <p>Click <a href="/graph">here</a> to access all the relative graphics.</p>
                <button class="btn-secondary" onclick="location.href='/graph'">View Graphics</button>
            </div>
        </div>
        <footer>
            <div class="container">
                <p>Developed by Angelo, Filippo, and Marco for the Programming in Finance and Economics II Course at Università della Svizzera Italiana.</p>
            </div>
        </footer>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

def fetch_nav_values():
    connection = None
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        if connection.is_connected():
            query = "SELECT date, nav FROM trade_results WHERE nav IS NOT NULL ORDER BY date"
            df = pd.read_sql(query, connection)
            return df  # Return DataFrame directly
        else:
            print("Failed to connect to the database.")
            return pd.DataFrame()
    except mysql.connector.Error as e:
        print(f"Error: {e}")
        return pd.DataFrame()
    finally:
        if connection and connection.is_connected():
            connection.close()

@app.get("/graph", response_class=HTMLResponse)
async def get_graph_html(request: Request):
    # Fetch NAV values from the database
    nav_data = fetch_nav_values()
    
    # Generate graph HTML using the NAV values
    graph_html = generate_graph_html(nav_data)  # Ensure this function is prepared to handle DataFrame with 'date' and 'nav'
    return graph_html

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0")
