"""
Article Model - Handles article data operations with Supabase
"""
import os
import uuid
import requests
from typing import Any, Dict, List
from dotenv import load_dotenv

load_dotenv()

class ArticleModel:
    """Model for managing article data in Supabase"""

    def __init__(self):
        self.supabase_url = (os.getenv("SUPABASE_URL") or "").rstrip("/")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or ""
        self.rest_url = f"{self.supabase_url}/rest/v1"
        self.headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
        self.allowed_cols = {"guid", "subject", "content", "notes", "topic"}

    @staticmethod
    def guess_topic(title: str | None, source: str | None) -> str:
        """Determine article topic based on title and source"""
        if not title:
            title = ""
        title = title.lower()
        source = (source or "").lower()

        if any(w in title for w in ["football", "nba", "sport", "soccer", "game"]):
            return "Sports"
        if any(w in title for w in ["stock", "market", "economy", "finance", "dollar", "business"]):
            return "Economy"
        if any(w in title for w in ["gaza", "idf", "war", "attack", "israel", "security", "russia", "ukraine"]):
            return "Defense"
        if any(w in title for w in ["weather", "forecast", "temperature", "storm", "rain"]):
            return "Weather"
        if any(w in title for w in ["tech", "ai", "app", "software", "google", "apple"]):
            return "Technology"
        if any(w in title for w in ["politic", "president", "minister", "election", "law", "government"]):
            return "Politics"
        if "cnn" in source or "bbc" in source:
            return "World"
        return "General"

    @staticmethod
    def _make_guid(article: Dict[str, Any]) -> str:
        """Generate deterministic GUID for article"""
        url = article.get("url")
        title = (article.get("title") or "").strip()
        try:
            if url:
                return str(uuid.uuid5(uuid.NAMESPACE_URL, url))
            if title:
                return str(uuid.uuid5(uuid.NAMESPACE_DNS, f"subject:{title}"))
        except Exception:
            pass
        return str(uuid.uuid4())

    def transform_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Transform raw article data into database format"""
        src = article.get("source") or {}
        title = (article.get("title") or "").strip() or None
        content = article.get("content") or article.get("description")
        url = article.get("url")
        source_name = src.get("name")

        # Build notes field
        if url and source_name:
            notes = f"{source_name} | {url}"
        elif url:
            notes = url
        elif source_name:
            notes = source_name
        else:
            notes = article.get("description")

        topic = self.guess_topic(title, source_name)

        row = {
            "guid": self._make_guid(article),
            "subject": title,
            "content": content,
            "notes": notes,
            "topic": topic,
        }
        return {k: v for k, v in row.items() if k in self.allowed_cols and v is not None}

    def batch_insert(self, rows: List[Dict[str, Any]], table_name: str = "articles", chunk_size: int = 500):
        """Insert articles into database in batches"""
        if not rows:
            return
        url = f"{self.rest_url}/{table_name}"
        for i in range(0, len(rows), chunk_size):
            chunk = rows[i:i+chunk_size]
            r = requests.post(url, headers=self.headers, json=chunk, timeout=30, verify=False)
            r.raise_for_status()

    def take_from_payload(self, payload: Dict[str, Any] | List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract and transform articles from various payload formats"""
        if isinstance(payload, list):
            articles = payload
        elif isinstance(payload, dict) and "articles" in payload:
            articles = payload.get("articles") or []
        else:
            articles = ((payload or {}).get("data") or {}).get("articles") or []

        rows = []
        for a in articles:
            row = self.transform_article(a)
            if not row.get("subject"):
                continue
            rows.append(row)
        return rows
