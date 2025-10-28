"""
News Controller - Handles news-related routes and operations
"""
import os
import json
import requests
from pathlib import Path
from flask import jsonify
from app_mvc.models.article_model import ArticleModel
from app_mvc.models.news_service import NewsFetcher

# Disable SSL warnings for local development
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class NewsController:
    """Controller for news-related endpoints"""

    def __init__(self):
        self.news_fetcher = NewsFetcher()
        self.article_model = ArticleModel()

    def fetch_news(self):
        """Fetch news from API and return JSON response"""
        try:
            result = self.news_fetcher.fetch_top_headlines()
            articles = result.get('data', {}).get('articles', [])
            print(f"Fetched {len(articles)} articles.")
            return jsonify(result), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    def ingest_payload(self, payload, table_name="articles"):
        """
        Process and insert articles from payload into database and send to Kafka

        Args:
            payload: Article data (dict or list)
            table_name: Database table name

        Returns:
            dict: Result with number of inserted rows
        """
        rows = self.article_model.take_from_payload(payload)
        if not rows:
            return {"inserted": 0, "note": "no valid rows after filtering (missing title/subject)"}

        self.article_model.batch_insert(rows, table_name=table_name)

        # Send to Kafka
        try:
            from kafka import KafkaProducer
            producer = KafkaProducer(
                bootstrap_servers="localhost:9092",
                value_serializer=lambda v: json.dumps(v).encode("utf-8")
            )

            for row in rows:
                message = {
                    "id": row.get("guid"),
                    "topic": row.get("topic")
                }
                producer.send("news-articles", message)

            producer.flush()
            producer.close()
        except Exception as e:
            print(f"Kafka error: {e}")

        return {"inserted": len(rows)}

    def fetch_and_ingest_once(self):
        """Fetch news from file or API and ingest into database"""
        news_path = Path("C:\Users\user-bin\project\news.json")

        # Try local file first
        if news_path.exists():
            with open(news_path, "r", encoding="utf-8") as f:
                payload = json.load(f)
            return self.ingest_payload(payload, table_name="articles")

        # Fetch from API if no local file
        try:
            api_key = os.getenv("NEWSAPI_KEY")
            url = "https://newsapi.org/v2/top-headlines"
            params = {"country": "us", "apiKey": api_key}
            r = requests.get(url, params=params, timeout=20, verify=False)
            r.raise_for_status()
            articles = r.json().get("articles", [])
            payload = {"data": {"articles": articles}}

            # Save to file for future use
            with open(news_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)

            return self.ingest_payload(payload, table_name="articles")
        except Exception as e:
            return {"inserted": 0, "note": f"no local JSON and API blocked: {e}"}
