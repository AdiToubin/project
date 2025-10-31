"""
בקר החדשות - ניהול פעולות קשורות לחדשות והכנסתם לבסיס הנתונים
PURPOSE:
   This controller handles all news-related operations including:
   1. לוקח ידיעות חדשותיות מניוז-אייפיאיי
   2. מסווג לפי נושאים
   3. מכניס את הידיעות לבסיס הנתונים בסופבייס
   4. שולח לקפקא את הידיעות יעבוד נוסף
   5. תומך בטעינת חדשות מקובץ מקומי או מניוז-אייפיאיי בפורמט גייסון
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
    בקר המטפל בכל פעולות החדשות, עיבוד וטעינה לבסיס נתונים
    """
    def __init__(self):
        """
        אתחול בקר החדשות עם מעדי משימות חדשות ומודל המאמרים
        """
        self.news_fetcher = NewsFetcher()
        self.article_model = ArticleModel()

    def fetch_news(self):

        #מקבל חדשות מהניוז-אייפיי ומחזיר את התוצאה כגייסון
        
        try:
            result = self.news_fetcher.fetch_top_headlines()
            articles = result.get('data', {}).get('articles', [])
            print(f"Fetched {len(articles)} articles.")
            return jsonify(result), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # היא מביאה את הנתונים מבחוץ, ודואגת להזין אותם פנימה דרך הפונקציה הבאה

    def ingest_payload(self, payload, table_name="articles"):

        #מוציא רשימת מאמרים, מסנן את מה שלא תקין, ומחזיר רשומות מוכנות

        rows = self.article_model.take_from_payload(payload)
        if not rows:
            return {"inserted": 0, "note": "no valid rows after filtering (missing title/subject)"}

        #מכניס לבסיס הנתונים
        self.article_model.batch_insert(rows, table_name=table_name)

        #שולח הודעות לקפקא לעיבוד נוסף
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

        # להביא מאמרים מהקובץ המקומי אם קיים, אחרת מהניוז-איפיאיי ואז להכניס אותם לקפקא ובסופבייס

        news_path = Path(r"C:\Users\efrat\Desktop\project\news.json")

        # מנסה לקרוא מקובץ מקומי ראשון אם קיים
        if news_path.exists():
            with open(news_path, "r", encoding="utf-8") as f:
                payload = json.load(f)
            return self.ingest_payload(payload, table_name="articles")

        # אם לא, מנסה להביא מהניוז-אייפיאיי
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
