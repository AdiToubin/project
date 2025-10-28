"""
Flask Application Server - MVC Architecture
"""
import os
import json
import threading
import time
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, render_template, request
from app_mvc.controllers.news_controller import NewsController
from app_mvc.controllers.api_controller import ApiController

# optional integrated services - disabled to avoid importing x/ which requires extra deps
HAS_X_SERVICES = False

# stubs for static analysis and to keep code safe when agents are disabled
uvicorn = None
image_service = None
image_agent = None
image_final_consumer = None
gradio_ui = None

# Load environment variables
load_dotenv()

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__, template_folder='mvc_view/templates')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize controllers
news_controller = NewsController()
api_controller = ApiController()

# ========== ROUTES ==========

@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')

@app.route('/news')
def news():
    """Render all news articles from local JSON"""
    json_path = Path(r"C:\Users\user-bin\project\news.json")
    if not json_path.exists():
        return "לא נמצא קובץ news.json", 404

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        articles = data.get("data", {}).get("articles", [])
        return render_template('news.html', articles=articles)
    except Exception as e:
        return f"שגיאה בטעינת החדשות: {e}", 500

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

def _start_background_services():
    """Start optional image services and Gradio UI"""
    if os.environ.get("NO_AGENTS") == "1":
        print("Skipping background agents (NO_AGENTS=1)")
        return

    if not HAS_X_SERVICES:
        print("x/services not available; skipping agents")
        return

    def _run_image_service():
        try:
            print("Starting image_service (uvicorn) on 127.0.0.1:8004")
            uvicorn.run(image_service.app, host="127.0.0.1", port=8004, log_level="info")
        except Exception as e:
            print(f"image_service error: {e}")

    def _run_image_agent():
        try:
            image_agent.run()
        except Exception as e:
            print(f"image_agent error: {e}")

    def _run_final_consumer():
        try:
            image_final_consumer.run()
        except Exception as e:
            print(f"image_final_consumer error: {e}")

    def _run_gradio():
        try:
            gradio_ui.run_gradio()
        except Exception as e:
            print(f"gradio_ui error: {e}")

    threads = [
        threading.Thread(target=_run_image_service, daemon=True),
        threading.Thread(target=_run_image_agent, daemon=True),
        threading.Thread(target=_run_final_consumer, daemon=True),
        threading.Thread(target=_run_gradio, daemon=True)
    ]

    for t in threads:
        t.start()
        time.sleep(0.6)

if __name__ == '__main__':
    # Do not start optional background agents automatically to keep runtime stable
    fetch_and_ingest_once()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
