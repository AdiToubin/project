"""
Flask Application Server - MVC Architecture
"""
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request
from controllers.news_controller import NewsController
from controllers.api_controller import ApiController

# Load environment variables
load_dotenv()

# Disable SSL warnings for local development
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize controllers
news_controller = NewsController()
api_controller = ApiController()

# ========== ROUTES ==========

@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')

@app.route('/api/process', methods=['POST'])
def process():
    """Process data endpoint"""
    data = request.get_json()
    return api_controller.process(data)

@app.route('/api/calculate', methods=['POST'])
def calculate():
    """Calculate endpoint"""
    data = request.get_json()
    return api_controller.calculate(data)

@app.route('/health')
def health():
    """Health check endpoint"""
    return api_controller.health()

@app.route('/fetch-news')
def fetch_news():
    """Fetch news from API"""
    return news_controller.fetch_news()

# ========== STARTUP ==========

def fetch_and_ingest_once():
    """Fetch and ingest news articles on startup"""
    res = news_controller.fetch_and_ingest_once()
    print(f"[startup] ingest result: {res}")

if __name__ == '__main__':
    fetch_and_ingest_once()

    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
