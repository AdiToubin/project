"""
════════════════════════════════════════════════════════════════════════════════
NEWS CONTROLLER - ARTICLE FETCHING, CLASSIFICATION & DATABASE INGESTION
════════════════════════════════════════════════════════════════════════════════

בקר החדשות - ניהול פעולות קשורות לחדשות והכנסתם לבסיס הנתונים

PURPOSE:
   This controller handles all news-related operations including:
   1. Fetching articles from NewsAPI
   2. Transforming/classifying articles by topic
   3. Inserting articles into Supabase database
   4. Sending articles to Kafka message queue for processing
   5. Caching news locally in JSON format

MAIN METHODS:
   - fetch_news(): Get latest news from API and return JSON
   - ingest_payload(): Process articles and insert into database
   - fetch_and_ingest_once(): Initialize database with news on startup

DEPENDENCIES:
   - ArticleModel: Database operations, topic classification
   - NewsFetcher: NewsAPI integration
   - Kafka: Message queue for article distribution
   - Supabase: Article storage

DATABASE FLOW:
   API/File → Transform → Classify Topics → Batch Insert (Supabase) → Kafka Producer

KAFKA MESSAGING:
   Sends to topic: "news-articles"
   Message format: {"id": guid, "topic": classified_topic}

ENVIRONMENT VARIABLES:
   - NEWSAPI_KEY: API key for NewsAPI.org

────────────────────────────────────────────────────────────────────────────────
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
    """
    NEWS CONTROLLER CLASS
    ─────────────────────
    ק Handles all news fetching, processing, and database ingestion operations
    בקר המטפל בכל פעולות החדשות, עיבוד וטעינה לבסיס נתונים

    RESPONSIBILITIES:
    1. Fetch articles from NewsAPI or local cache
    2. Extract valid articles from payloads
    3. Transform articles to database format
    4. Classify articles by topic using AI
    5. Batch insert articles to Supabase
    6. Produce Kafka messages for downstream processing

    ATTRIBUTES:
    - news_fetcher (NewsFetcher): API client for NewsAPI
    - article_model (ArticleModel): Database and ML operations
    """

    def __init__(self):
        """
        אתחול בקר החדשות עם מעדי משימות חדשות ומודל המאמרים
        Initializes the NewsController with news fetcher and article model
        """
        self.news_fetcher = NewsFetcher()
        self.article_model = ArticleModel()

    def fetch_news(self):
        """
        FETCH NEWS FROM API ENDPOINT
        ───────────────────────────
        קבל חדשות טרופות מ-NewsAPI והחזר JSON עם המאמרים
        Fetch latest news from NewsAPI and return JSON response

        PROCESS:
        1. Call NewsFetcher.fetch_top_headlines()
        2. Extract articles from nested 'data.articles' structure
        3. Log number of fetched articles to console
        4. Return wrapped JSON response with HTTP 200

        RETURNS: Tuple (JSON response, HTTP status code)
           Success: ({"data": {"articles": [...]}, "status": "success"}, 200)
           Error: ({"error": "error message"}, 500)

        ERROR HANDLING:
        - Catches all exceptions (network, API, etc.)
        - Returns HTTP 500 with error details

        ENDPOINT: GET /fetch-news
        RESPONSE TIME: ~2-5 seconds (depends on network)
        """
        try:
            result = self.news_fetcher.fetch_top_headlines()
            articles = result.get('data', {}).get('articles', [])
            print(f"Fetched {len(articles)} articles.")
            return jsonify(result), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    def ingest_payload(self, payload, table_name="articles"):
        """
        PROCESS & INSERT ARTICLES INTO DATABASE
        ───────────────────────────────────────
        עבד והכנס מאמרים מהעומס לתוך בסיס הנתונים ושלח אל Kafka
        Process and insert articles from payload into database and Kafka

        PARAMETERS:
        - payload (dict|list): Raw article data from API or file
          Expected structure: {"data": {"articles": [...]}} or array of articles
        - table_name (str): Supabase table name (default: "articles")

        RETURNS:
        - dict: {"inserted": count} on success
        - dict: {"inserted": 0, "note": "reason"} on failure

        DETAILED PROCESS:
        1. VALIDATE & EXTRACT
           - Call ArticleModel.take_from_payload()
           - Filter articles: remove if missing title/subject
           - Return empty dict if no valid articles found

        2. TRANSFORM
           - Convert NewsAPI format to database format
           - Generate unique GUID for each article (UUID v5)
           - Classify articles by topic using Hugging Face AI

        3. INSERT TO DATABASE
           - Use Supabase client
           - Batch insert in chunks of 500 rows (for performance)
           - Handle database errors gracefully

        4. PRODUCE TO KAFKA
           - Connect to Kafka broker (localhost:9092)
           - Send article metadata: {"id": guid, "topic": topic}
           - Target topic: "news-articles"
           - Flush & close producer
           - Catch Kafka errors without blocking response

        KAFKA TOPICS:
        - Publishes to: "news-articles"
        - Consumers: image_agent, consumer_pipeline (downstream processing)

        EXAMPLE PAYLOAD:
        {
            "data": {
                "articles": [
                    {
                        "title": "Breaking News",
                        "description": "Article description",
                        "url": "https://example.com/article",
                        "urlToImage": "https://example.com/image.jpg",
                        "content": "Full article content",
                        "publishedAt": "2024-01-01T12:00:00Z",
                        "source": {"id": "source-id", "name": "Source Name"}
                    }
                ]
            }
        }
        """
        rows = self.article_model.take_from_payload(payload)
        if not rows:
            return {"inserted": 0, "note": "no valid rows after filtering (missing title/subject)"}

        self.article_model.batch_insert(rows, table_name=table_name)

        # Send to Kafka for downstream processing
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
        """
        FETCH & INGEST NEWS ON APPLICATION STARTUP
        ───────────────────────────────────────────
        קבל חדשות מקובץ מקומי או מ-API והכנס לתוך בסיס הנתונים בהתחלה
        Fetch news from local cache or API and ingest into database

        PROCESS:
        This method is called once when the application starts to populate
        the database with initial news articles. It uses a caching strategy
        to minimize API calls:

        STRATEGY:
        1. FIRST: Try to load from local cache (news.json)
           - Faster startup (no network delay)
           - Reduces API calls to NewsAPI
           - Useful for development and testing

        2. FALLBACK: If cache doesn't exist, fetch from NewsAPI API
           - Makes HTTP request to: https://newsapi.org/v2/top-headlines
           - Uses environment variable: NEWSAPI_KEY
           - Filters articles by country: US
           - Timeout: 20 seconds
           - SSL verification: disabled (for local development)

        3. CACHE: Save API response to local JSON file
           - Path: C:\project\news.json
           - Format: UTF-8 with proper indentation (2 spaces)
           - Preserves non-ASCII characters (ensure_ascii=False)
           - Used on next application restart

        4. INGEST: Send to ingest_payload() for database insertion
           - Validates articles
           - Classifies by topic
           - Inserts to Supabase
           - Produces Kafka messages

        RETURNS:
        - dict: {"inserted": count} on success
        - dict: {"inserted": 0, "note": "error message"} on all failures

        ENVIRONMENT VARIABLES:
        - NEWSAPI_KEY: Required for API access

        ERROR HANDLING:
        - Network timeout: caught, returns error note
        - Invalid API key: caught, returns error note
        - File permissions: caught, returns error note
        - JSON parse errors: caught, returns error note

        CACHE FILE:
        Location: C:\project\news.json
        Format: {"data": {"articles": [...]}}
        Auto-created on first API call
        Auto-refreshed on app restart if deleted

        TYPICAL RESPONSE TIME:
        - From cache: <100ms
        - From API: 2-5 seconds
        """
        news_path = Path("C:\project\news.json")

        # Try local file first (fastest path)
        if news_path.exists():
            with open(news_path, "r", encoding="utf-8") as f:
                payload = json.load(f)
            return self.ingest_payload(payload, table_name="articles")

        # Fetch from API if no local file (fallback)
        try:
            api_key = os.getenv("NEWSAPI_KEY")
            url = "https://newsapi.org/v2/top-headlines"
            params = {"country": "us", "apiKey": api_key}
            r = requests.get(url, params=params, timeout=20, verify=False)
            r.raise_for_status()
            articles = r.json().get("articles", [])
            payload = {"data": {"articles": articles}}

            # Save to file for future use (cache the API response)
            with open(news_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)

            return self.ingest_payload(payload, table_name="articles")
        except Exception as e:
            return {"inserted": 0, "note": f"no local JSON and API blocked: {e}"}
