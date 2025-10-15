"""
Flask Application Server
"""
import os, json, requests
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from model.logic import BusinessLogic
from services.news_fetcher import NewsFetcher
from ingest_articles import ingest_payload

# מטען משתני סביבה
load_dotenv()

# להעלים אזהרות SSL לא מאומת (מקומי בלבד)
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

logic = BusinessLogic()
news_fetcher = NewsFetcher()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/process', methods=['POST'])
def process():
    try:
        data = request.get_json()
        result = logic.process_data(data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/calculate', methods=['POST'])
def calculate():
    try:
        data = request.get_json()
        num1 = float(data.get('num1', 0))
        num2 = float(data.get('num2', 0))
        operation = data.get('operation', 'add')
        result = logic.calculate(num1, num2, operation)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'}), 200

@app.route('/fetch-news')
def fetch_news():
    try:
        articles = news_fetcher.fetch_top_headlines()
        print(f"Fetched {len(articles)} articles.")
        return jsonify(articles), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# -------- ריצה אחת לפני העלאת השרת: מביא -> שומר -> מכניס --------
def fetch_and_ingest_once():
    news_path = Path(__file__).parent / "news.json"
    api_key = os.getenv("NEWSAPI_KEY")

    # 1) קודם מנסה קובץ מקומי (עוקף חסימות SSL של ה-API)
    if news_path.exists():
        with open(news_path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        return ingest_payload(payload, table_name="articles")

    # 2) אין קובץ? ננסה להביא מה-API (עם verify=False כדי לעקוף SSL מקומי)
    try:
        url = "https://newsapi.org/v2/top-headlines"
        params = {"country": "us", "apiKey": api_key}
        r = requests.get(url, params=params, timeout=20, verify=False)  # לפיתוח מקומי בלבד
        r.raise_for_status()
        articles = r.json().get("articles", [])
        payload = {"data": {"articles": articles}}

        # נשמור גם לקובץ לשימוש עתידי
        with open(news_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        return ingest_payload(payload, table_name="articles")
    except Exception as e:
        return {"inserted": 0, "note": f"no local JSON and API blocked: {e}"}

if __name__ == '__main__':
    res = fetch_and_ingest_once()
    print(f"[startup] ingest result: {res}")

    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
