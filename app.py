"""
Flask Application Server - MVC Architecture
"""
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request
from app_mvc.controllers.news_controller import NewsController
from app_mvc.controllers.api_controller import ApiController
import threading
import time

# optional integrated services
try:
    from x import image_service, image_agent, image_final_consumer, gradio_ui
    import uvicorn
    HAS_X_SERVICES = True
except Exception as e:
    # Print traceback so failures during import are visible in logs
    import traceback
    print("Failed to import optional 'x' services:")
    traceback.print_exc()
    HAS_X_SERVICES = False

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


def _start_background_services():
    """Start external image services and Gradio UI in background threads.

    This is convenient for local development. Set environment variable
    NO_AGENTS=1 to skip starting the extra services.
    """
    if os.environ.get("NO_AGENTS") == "1":
        print("Skipping background agents (NO_AGENTS=1)")
        return

    if not HAS_X_SERVICES:
        print("x/services not available; skipping agents")
        return

    # image microservice (FastAPI / uvicorn)
    def _run_image_service():
        try:
            print("Starting image_service (uvicorn) on 127.0.0.1:8004")
            uvicorn.run(image_service.app, host="127.0.0.1", port=8004, log_level="info")
        except Exception as e:
            print(f"image_service error: {e}")

    # agent worker
    def _run_image_agent():
        try:
            image_agent.run()
        except Exception as e:
            print(f"image_agent error: {e}")

    # final consumer
    def _run_final_consumer():
        try:
            image_final_consumer.run()
        except Exception as e:
            print(f"image_final_consumer error: {e}")

    # gradio UI
    def _run_gradio():
        try:
            gradio_ui.run_gradio()
        except Exception as e:
            print(f"gradio_ui error: {e}")

    threads = []
    threads.append(threading.Thread(target=_run_image_service, daemon=True))
    threads.append(threading.Thread(target=_run_image_agent, daemon=True))
    threads.append(threading.Thread(target=_run_final_consumer, daemon=True))
    threads.append(threading.Thread(target=_run_gradio, daemon=True))

    for t in threads:
        t.start()
        time.sleep(0.6)


if __name__ == '__main__':
    # start background agents and UI (unless disabled)
    _start_background_services()

    # initial fetch/ingest
    fetch_and_ingest_once()

    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
