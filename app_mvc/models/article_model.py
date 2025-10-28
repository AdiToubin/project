"""
Article Model - Handles article data operations with Supabase
"""
import os
import uuid
import requests
from typing import Any, Dict, List
from dotenv import load_dotenv

# ---- Zero-Shot (HF API) ----
HF_TOKEN = os.getenv("HF_TOKEN") or ""  # שימי טוקן בסביבה
HF_MODEL = "joeddav/xlm-roberta-large-xnli"
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
HF_HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}

CANDIDATE_LABELS = ["Sports", "Economy", "Defense", "Weather", "Technology", "Politics", "World", "General"]

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
        # include image_url so inserts/upserts can store image links when available
        self.allowed_cols = {"guid", "subject", "content", "notes", "topic", "image_url"}

    @staticmethod
    def guess_topic(title: str | None, source: str | None) -> str:
        text = (title or "").strip().lower()
        if not text:
            return "General"

        # Try Hugging Face API first
        try:
            payload = {
                "inputs": text,
                "parameters": {"candidate_labels": CANDIDATE_LABELS, "multi_label": False}
            }
            r = requests.post(HF_API_URL, headers=HF_HEADERS, json=payload, timeout=60)
            r.raise_for_status()
            data = r.json()
            top_label = data["labels"][0]
            top_score = float(data["scores"][0])
            if top_score >= 0.35:  # Lowered threshold from 0.45 to 0.35
                return top_label
        except Exception as e:
            print(f"⚠️ HF API failed: {e}, using fallback classification")

        # Fallback: Keyword-based classification
        keywords = {
            "Sports": ["sports", "football", "basketball", "soccer", "game", "team", "player", "match", "league"],
            "Politics": ["politics", "election", "congress", "senate", "president", "minister", "parliament", "vote", "political"],
            "Fashion": ["fashion", "style", "clothing", "designer", "dress", "model", "wear", "trend", "collection"],
            "Technology": ["tech", "computer", "software", "ai", "technology", "digital", "app", "cyber", "innovation"],
            "Economy": ["economy", "business", "market", "stock", "finance", "trade", "company", "industry", "economic"],
            "Defense": ["defense", "military", "war", "army", "navy", "security", "weapon", "soldier", "combat"],
            "Weather": ["weather", "storm", "rain", "temperature", "climate", "wind", "forecast", "cold", "hot"],
            "World": ["world", "international", "global", "country", "nation", "foreign", "worldwide", "region"]
        }

        for topic, words in keywords.items():
            if any(word in text for word in words):
                print(f"✅ Topic classified as '{topic}' using keywords")
                return topic

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
