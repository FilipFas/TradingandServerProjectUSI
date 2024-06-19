from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import matplotlib.pyplot as plt
import pandas as pd
import io
import base64
import matplotlib.dates as mdates

app = FastAPI()

def generate_graph_html(dataset):
    # Setup the plot
    plt.figure(figsize=(10, 6))
    plt.plot(dataset['date'], dataset['nav'], color='#007bff', linewidth=2, label='NAV Performance')
    plt.title('NAV Performance Over Time', fontsize=20, fontweight='bold', color='#333')
    plt.xlabel('Date', fontsize=16, fontweight='bold', color='#333')
    plt.ylabel('NAV (USD)', fontsize=16, fontweight='bold', color='#333')
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Formatting the date
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())  # Setting major ticks to be at every month
    plt.gcf().autofmt_xdate()  # Rotation for better alignment of date labels
    plt.legend(fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()

    # Convert the plot to base64 encoded image
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plot_data = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()

    # Generate HTML content with the plot
    html_content = f"""
        <html>
        <head>
            <title>NAV Performance Graph</title>
            <style>
                body {{
                    font-family: 'Arial', sans-serif;
                    background-color: #f8f9fa;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    max-width: 1000px;
                    margin: 50px auto;
                    padding: 20px;
                    background-color: #fff;
                    border-radius: 20px;
                    box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
                    text-align: center;
                }}
                .graph img {{
                    max-width: 100%;
                    height: auto;
                    border-radius: 20px;
                    box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
                }}
                h1, h2 {{
                    color: #333;
                    font-weight: bold;
                    margin-bottom: 20px;
                }}
                h2 {{
                    font-size: 24px;
                    color: #007bff;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>NAV Performance Graph</h1>
                <div class="graph">
                    <img src='data:image/png;base64,{plot_data}'/>
                </div>
            </div>
        </body>
        </html>
    """
    
    return html_content
