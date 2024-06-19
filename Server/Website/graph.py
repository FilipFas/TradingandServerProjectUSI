from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import matplotlib.pyplot as plt
import pandas as pd
import io
import base64

app = FastAPI()

def generate_graph_html(dataset):
    # Generate a simple plot using Matplotlib for the dataset
    plt.figure(figsize=(8, 6))
    plt.plot(dataset, color='#007bff', linewidth=2, label='Strategy Performance')
    plt.title('Strategy Performance', fontsize=20, fontweight='bold', color='#333')
    plt.xlabel('Date', fontsize=16, fontweight='bold', color='#333')
    plt.ylabel('Portfolio Value', fontsize=16, fontweight='bold', color='#333')
    plt.legend(fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    # Convert the plot to base64 encoded image for the dataset
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plot_data = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()

    # Generate HTML content with the plot
    html_content = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Arial', sans-serif;
                    background-color: #f8f9fa;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    max-width: 800px;
                    margin: 50px auto;
                    padding: 20px;
                    background-color: #fff;
                    border-radius: 20px;
                    box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
                    animation: slideInUp 0.5s ease;
                    text-align: center;
                }}
                .graph {{
                    margin: 20px auto;
                    padding: 20px;
                    background-color: #fff;
                    border-radius: 20px;
                    box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
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
                <h1>Graph Data</h1>
                <div class="graph">
                    <h2>Strategy Performance</h2>
                    <img src='data:image/png;base64,{plot_data}'/>
                </div>
            </div>
        </body>
        </html>
    """
    
    return html_content
