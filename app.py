"""
════════════════════════════════════════════════════════════════════════════════
MAIN FLASK APPLICATION SERVER - NEWS PROCESSING SYSTEM
════════════════════════════════════════════════════════════════════════════════

PROJECT: Advanced News Processing & Image Enrichment Platform
ARCHITECTURE: MVC (Model-View-Controller) with Kafka Message Streaming
LANGUAGE: Python 3.11 with Flask Framework

PURPOSE:
   This is the main entry point for a comprehensive news processing application that:
   1. Fetches news articles from NewsAPI
   2. Classifies articles by topic using AI (Hugging Face NER)
   3. Stores articles in Supabase database
   4. Processes articles through Kafka pipelines
   5. Enriches articles with relevant images from Pexels
   6. Uploads images to Cloudinary
   7. Provides REST APIs and web interfaces (Flask templates & Gradio)

MAIN COMPONENTS:
   ✓ REST API endpoints for news fetching and data processing
   ✓ NewsController - Handles article fetching and ingestion
   ✓ ApiController - Handles general API operations (process, calculate, health)
   ✓ Database layer - Supabase integration for persistent storage
   ✓ Kafka producer - Sends articles to message queue for processing
   ✓ Web templates - Hebrew-language Flask templates for article display
   ✓ Optional background services (image agent, Gradio UI) - disabled by default

ENVIRONMENT CONFIGURATION:
   Requires .env file with:
   - SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY (database)
   - NEWSAPI_KEY (for fetching news)
   - PEXELS_API_KEY (for image search)
   - CLOUDINARY_* (for image hosting)
   - SECRET_KEY (Flask sessions)
   - PORT (default: 5000)
   - NO_AGENTS (set to 1 to disable background services)

STARTUP PROCESS:
   1. Load environment variables from .env
   2. Initialize Flask app with templates from mvc_view/templates
   3. Suppress SSL warnings for development
   4. Initialize controllers (NewsController, ApiController)
   5. Call fetch_and_ingest_once() to populate database with initial news
   6. Start Flask development/production server on port 5000
   7. Optionally start background Kafka consumers and image processing services

DEPLOYMENT:
   Production: gunicorn app:app (as specified in Procfile)
   Development: python app.py
   Heroku/Cloud: Set PORT environment variable, Python 3.11.0

────────────────────────────────────────────────────────────────────────────────
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

# ════════════════════════════════════════════════════════════════════════════
# CONFIGURATION & INITIALIZATION
# ════════════════════════════════════════════════════════════════════════════

# OPTIONAL INTEGRATED SERVICES
# ─────────────────────────────
# תומך שירותים אופציונליים - מושבתים כברירת מחדל כדי להימנע מייבוא x/
# Optional integrated services - disabled by default to avoid importing x/
# which requires extra dependencies (uvicorn, gradio, kafka, etc.)
HAS_X_SERVICES = False

# STUBS FOR STATIC ANALYSIS & SAFETY
# ────────────────────────────────────
# שונים כדי להישאר בטוח כאשר הסוכנים מושבתים
# Stubs to keep code safe when agents are disabled
# Prevents NameError if background services are not loaded
uvicorn = None
image_service = None
image_agent = None
image_final_consumer = None
gradio_ui = None

# ENVIRONMENT VARIABLES
# ─────────────────────
# טעון משתנים סביבה מ-.env קובץ
# Load environment variables from .env file
# This includes: API keys, database credentials, feature flags, etc.
load_dotenv()

# SSL WARNINGS SUPPRESSION
# ────────────────────────
# להפחתת אזהרות SSL לפיתוח מקומי (לא לייצור!)
# Suppress SSL warnings for local development (NOT for production!)
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# FLASK APP INITIALIZATION
# ────────────────────────
# יצירת Flask אפליקציה עם תיקיית תבניות מ mvc_view/templates
# Creates Flask app instance with templates from mvc_view/templates
# Templates include: index.html (homepage), news.html (articles list)
app = Flask(__name__, template_folder='mvc_view/templates')

# SECRET KEY CONFIGURATION
# ────────────────────────
# מפתח סתום עבור session signing ו CSRF protection
# Secret key for session signing, cookie encryption, and CSRF protection
# In production, this should be a strong random string set in environment
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# MVC CONTROLLER INITIALIZATION
# ──────────────────────────────
# אתחול בקרי יישום עבור טיפול בנתחים
# Initialize MVC controllers for handling different route groups
news_controller = NewsController()   # Handles news fetching, classification, ingestion
api_controller = ApiController()     # Handles generic API operations (calculate, process, health)

# ════════════════════════════════════════════════════════════════════════════
# REST API ROUTES
# ════════════════════════════════════════════════════════════════════════════
# הנתחים לתיקייה של היישום - טיפול בבקשות HTTP
# Application routes for handling HTTP requests from clients

@app.route('/')
def index():
    """
    HOME PAGE ROUTE
    ───────────────
    דף הבית - מציג דף ברוכים הבאים עברית
    Route: GET /
    Returns: HTML template (index.html) - Welcome page with site information
    Status: 200 OK
    """
    return render_template('index.html')

@app.route('/news')
def news():
    """
    NEWS ARTICLES DISPLAY ROUTE
    ────────────────────────────
    הצג את כל המאמרים מקובץ ה JSON המקומי
    Route: GET /news
    Purpose: Load and display articles from locally cached news.json file
    Returns: HTML page with formatted articles list (news.html template)
    Status: 200 OK on success, 404 if file not found, 500 on error

    PROCESS:
    1. Check if news.json exists in project root
    2. Load JSON file with UTF-8 encoding
    3. Extract articles array from nested structure: data.articles
    4. Pass articles to Jinja2 template for HTML rendering
    5. Handle errors gracefully with Hebrew error messages
    """
    json_path = Path(r"C:\Users\efrat\Desktop\project\news.json")
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
    """
    GENERAL DATA PROCESSING ENDPOINT
    ─────────────────────────────────
    עבד נתונים כלליים דרך API
    Route: POST /api/process
    Content-Type: application/json
    Purpose: Generic endpoint for processing various types of data

    Request Body: JSON object with data to process
    Response: JSON response from ApiController
    Status: 200 OK on success, 400/500 on error

    DELEGATES TO: ApiController.process()
    """
    data = request.get_json()
    return api_controller.process(data)

@app.route('/api/calculate', methods=['POST'])
def calculate():
    """
    MATHEMATICAL CALCULATION ENDPOINT
    ──────────────────────────────────
    ביצוע חישובים מתמטיים: חיבור, חיסור, כפל, חילוק
    Route: POST /api/calculate
    Content-Type: application/json
    Purpose: Perform arithmetic operations on provided numbers

    Request Body JSON Format:
    {
        "operation": "add|subtract|multiply|divide",
        "operands": [num1, num2, ...],
        "a": number (alternative format),
        "b": number (alternative format)
    }

    Response: JSON with result and status
    Status: 200 OK on success, 400 on invalid operation, 500 on error

    DELEGATES TO: ApiController.calculate()
    OPERATIONS: add, subtract, multiply, divide
    """
    data = request.get_json()
    return api_controller.calculate(data)

@app.route('/health')
def health():
    """
    HEALTH CHECK ENDPOINT
    ─────────────────────
    בדוק את בריאות ה API והיישום
    Route: GET /health
    Purpose: Health check for monitoring and load balancing
    Returns: JSON with application status and timestamp
    Status: Always 200 OK if server is running

    USAGE:
    - Docker container health checks
    - Kubernetes liveness probes
    - Load balancer monitoring
    - Monitoring systems (Prometheus, Datadog, etc.)

    DELEGATES TO: ApiController.health()
    """
    return api_controller.health()

@app.route('/fetch-news')
def fetch_news():
    """
    FETCH NEWS FROM API ENDPOINT
    ────────────────────────────
    קבל חדשות טרופות מ NewsAPI ו הראה JSON
    Route: GET /fetch-news
    Purpose: Fetch latest news articles from NewsAPI
    Returns: JSON array with top headlines and metadata
    Status: 200 OK on success, 500 on API error

    FEATURES:
    - Connects to NewsAPI.org
    - Filters by country (US)
    - Returns article metadata (title, description, URL, etc.)
    - Includes article count in response

    REQUIRES: NEWSAPI_KEY environment variable

    DELEGATES TO: NewsController.fetch_news()
    """
    return news_controller.fetch_news()

# ════════════════════════════════════════════════════════════════════════════
# APPLICATION STARTUP & BACKGROUND SERVICES
# ════════════════════════════════════════════════════════════════════════════

def fetch_and_ingest_once():
    """
    INITIALIZE DATABASE WITH NEWS ARTICLES
    ───────────────────────────────────────
    טעין וטעון חדשות מ API או קובץ מקומי לתוך בסיס הנתונים בהתחלה
    Called during application startup to populate database with initial news

    PURPOSE:
    - Ensures database has articles before serving requests
    - Tries local news.json file first for faster startup
    - Falls back to NewsAPI if no local file exists
    - Saves API response to local JSON for future use

    PROCESS:
    1. Delegates to NewsController.fetch_and_ingest_once()
    2. Attempts to read from cached news.json file
    3. If not found, fetches from NewsAPI.org
    4. Classifies articles by topic using Hugging Face NER
    5. Inserts articles into Supabase database
    6. Sends articles to Kafka "news-articles" topic for processing
    7. Prints result summary

    RETURNS: Dictionary with number of inserted articles
    """
    res = news_controller.fetch_and_ingest_once()
    print(f"[startup] ingest result: {res}")

def _start_background_services():
    """
    START OPTIONAL BACKGROUND SERVICES (DISABLED BY DEFAULT)
    ─────────────────────────────────────────────────────────
    הפעל שירותים אופציונליים כגון עיבוד תמונה ו Gradio UI
    Start optional background services that process articles asynchronously

    WARNING: DISABLED BY DEFAULT
    Set HAS_X_SERVICES = True and NO_AGENTS != "1" to enable

    SERVICES STARTED (if enabled):
    1. image_service - FastAPI microservice (port 8004)
       - Searches images on Pexels
       - Uploads to Cloudinary
       - Provides API for image retrieval

    2. image_agent - Kafka Consumer
       - Listens to "news.summarized" topic
       - Calls image_service for relevant images
       - Sends results to "news.final" topic
       - Filters by IMAGE_TOPICS env variable

    3. image_final_consumer - Kafka Consumer
       - Listens to "news.final" topic
       - Updates Supabase articles with image URLs
       - Fallback search by guid and subject

    4. gradio_ui - Web Interface (port 7860)
       - Interactive article display
       - Topic filtering and search
       - Image gallery viewer
       - Manual refresh controls

    REQUIREMENTS:
    - Kafka broker running on localhost:9092
    - Pexels API key (PEXELS_API_KEY)
    - Cloudinary account (CLOUDINARY_*)
    - Gradio library installed

    THREADING MODEL:
    - Each service runs in separate daemon thread
    - 0.6 second delay between thread starts
    - Threads run independently and don't block main app
    """
    if os.environ.get("NO_AGENTS") == "1":
        print("Skipping background agents (NO_AGENTS=1)")
        return

    if not HAS_X_SERVICES:
        print("x/services not available; skipping agents")
        return

    def _run_image_service():
        """
        RUN FASTAPI IMAGE MICROSERVICE
        FastAPI service on port 8004 for fetching images from Pexels
        תירות FastAPI על port 8004 לטעינת תמונות מ Pexels
        """
        try:
            print("Starting image_service (uvicorn) on 127.0.0.1:8004")
            uvicorn.run(image_service.app, host="127.0.0.1", port=8004, log_level="info")
        except Exception as e:
            print(f"image_service error: {e}")

    def _run_image_agent():
        """
        RUN IMAGE AGENT KAFKA CONSUMER
        Kafka consumer that returns images for articles
        צרכן Kafka המחזיר תמונות למאמרים
        """
        try:
            image_agent.run()
        except Exception as e:
            print(f"image_agent error: {e}")

    def _run_final_consumer():
        """
        RUN FINAL IMAGE CONSUMER (DATABASE UPDATER)
        Kafka consumer that updates articles with image URLs
        צרכן Kafka עדכון מאמרים עם URL תמונות
        """
        try:
            image_final_consumer.run()
        except Exception as e:
            print(f"image_final_consumer error: {e}")

    def _run_gradio():
        """
        RUN GRADIO WEB INTERFACE
        Interactive web interface on port 7860 for article display
        ממשק ויב Gradio אינטראקטיבי על port 7860
        """
        try:
            gradio_ui.run_gradio()
        except Exception as e:
            print(f"gradio_ui error: {e}")

    # CREATE AND START DAEMON THREADS
    # ───────────────────────────────
    # יצירת חוטי רקע בנפרד לכל שירות
    threads = [
        threading.Thread(target=_run_image_service, daemon=True),
        threading.Thread(target=_run_image_agent, daemon=True),
        threading.Thread(target=_run_final_consumer, daemon=True),
        threading.Thread(target=_run_gradio, daemon=True)
    ]

    # START ALL THREADS WITH STAGGERED TIMING
    # ───────────────────────────────────────
    # התחל כל חוט עם עיכוב 0.6 שנייה בין להם
    for t in threads:
        t.start()
        time.sleep(0.6)

# ════════════════════════════════════════════════════════════════════════════
# APPLICATION ENTRY POINT
# ════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    # MAIN APPLICATION ENTRY POINT
    # ─────────────────────────────
    # נקודת הכניסה הראשונה של היישום

    # STARTUP SEQUENCE:
    # 1. Load environment variables (already done via load_dotenv())
    # 2. Initialize Flask controllers
    # 3. Populate database with initial news (fetch_and_ingest_once)
    # 4. OPTIONALLY start background services (disabled by default)
    # 5. Start Flask development/production server

    # DEPLOYMENT MODES:
    # Development: python app.py
    #   - Debug mode disabled
    #   - Single-threaded
    #   - Suitable for local development
    #
    # Production: gunicorn app:app
    #   - Uses Gunicorn WSGI server
    #   - Multi-worker process pool
    #   - Better performance and concurrency
    #   - As specified in Procfile

    # ENVIRONMENT VARIABLES:
    # - PORT: Server port (default: 5000)
    # - DEBUG: Set to True for debug mode (not recommended)
    # - NO_AGENTS: Set to "1" to disable background services

    # SERVER CONFIGURATION:
    # - Host: 0.0.0.0 (listen on all network interfaces)
    # - Port: Environment variable PORT or default 5000
    # - Debug: False (even in development, to avoid auto-reload issues with Kafka)

    # IMPORTANT: Do NOT start optional background agents automatically
    # They require Kafka, additional dependencies, and microservices
    # Only enable if you have proper infrastructure set up

    # Populate database with initial news articles
    fetch_and_ingest_once()

    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5000))

    # Start Flask server
    # Host 0.0.0.0 makes it accessible from outside containers/networks
    app.run(host='0.0.0.0', port=port, debug=False)
