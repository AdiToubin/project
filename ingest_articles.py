import os
import uuid
from typing import Any, Dict, List

from supabase import create_client
from dotenv import load_dotenv

# ---- ENV ----
load_dotenv()
SUPABASE_URL = "https://xgkntcsnnuhdepgnjzio.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhna250Y3NubnVoZGVwZ25qemlvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTU1OTUwNSwiZXhwIjoyMDc1MTM1NTA1fQ.0vcBOnz3MJBv_ZPnkCt9gQH-K5iPPtFiLg-pO98OVq0"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---- קביעת נושא לפי כותרת או מקור ----
def guess_topic(title: str | None, source: str | None) -> str:
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

    # fallback לפי מקור
    if "cnn" in source or "bbc" in source:
        return "World"
    return "General"

# נשלח לטבלה רק את העמודות שקיימות אצלך
ALLOWED_COLS = {"guid", "subject", "content", "notes", "topic"}

def transform_article(a: Dict[str, Any]) -> Dict[str, Any]:
    """
    ממפה רשומת article מה-JSON לעמודות הטבלה:
    guid (uuid חדש), subject (title), content, notes (source/url/description)
    """
    src = a.get("source") or {}
    title = (a.get("title") or "").strip() or None
    content = a.get("content") or a.get("description")
    url = a.get("url")
    source_name = src.get("name")

    # notes: עדיפות לקישור + מקור; אחרת תיאור אם יש
    notes = None
    if url and source_name:
        notes = f"{source_name} | {url}"
    elif url:
        notes = url
    elif source_name:
        notes = source_name
    else:
        notes = a.get("description")

    topic = guess_topic(title, source_name)

    row = {
        "guid": str(uuid.uuid4()),
        "subject": title,
        "content": content,
        "notes": notes,
    }

    # מחזירים רק עמודות שקיימות בטבלה ושאינן None
    return {k: v for k, v in row.items() if k in ALLOWED_COLS and v is not None}

def take_from_payload(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    מצפה למבנה: { data: { articles: [...] } } בדיוק כמו ששלחת.
    מסנן החוצה רשומות בלי title (כלומר בלי subject).
    """
    if isinstance(payload, list):
        articles = payload
    else:
        articles = ((payload or {}).get("data") or {}).get("articles") or []

    rows = []
    for a in articles:
        row = transform_article(a)
        # דלג אם אין subject (title)
        if not row.get("subject"):
            continue
        rows.append(row)
    return rows

def batch_insert(
    rows: List[Dict[str, Any]],
    table_name: str = "articles",
    chunk_size: int = 500,
    upsert_on: str | None = None  # אין אצלך אינדקס ייחודי, אז ברירת מחדל insert רגיל
):
    for i in range(0, len(rows), chunk_size):
        chunk = rows[i:i+chunk_size]
        if upsert_on:
            supabase.table(table_name).upsert(chunk, on_conflict=upsert_on).execute()
        else:
            supabase.table(table_name).insert(chunk).execute()

def ingest_payload(payload: Dict[str, Any], table_name: str = "articles"):
    rows = take_from_payload(payload)
    if not rows:
        return {"inserted": 0, "note": "no valid rows after filtering (missing title/subject)"}
    batch_insert(rows, table_name=table_name, upsert_on=None)  # insert רגיל
    return {"inserted": len(rows)}
