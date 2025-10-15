import os, uuid, requests
from typing import Any, Dict, List
from dotenv import load_dotenv

# ---- ENV ----
load_dotenv()
SUPABASE_URL = (os.getenv("SUPABASE_URL") or "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or ""

# ---- REST config (עוקף ספריית supabase וה-SSL שלה) ----
REST_URL = f"{SUPABASE_URL}/rest/v1"
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

# אם את לא רוצה לראות אזהרות על verify=False:
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ---- קביעת נושא לפי כותרת/מקור ----
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
    if "cnn" in source or "bbc" in source:
        return "World"
    return "General"

# נשלח לטבלה רק את העמודות שקיימות אצלך
# אם אין לך עמודה topic בטבלה, או תוסיפי אותה ב-SQL, או הסירי אותה מהסט הזה
ALLOWED_COLS = {"guid", "subject", "content", "notes", "topic"}

def _make_guid(a: Dict[str, Any]) -> str:
    """
    GUID דטרמיניסטי: עדיפות ל-URL; אם אין—כותרת; אחרת uuid4.
    """
    url = a.get("url")
    title = (a.get("title") or "").strip()
    try:
        if url:
            return str(uuid.uuid5(uuid.NAMESPACE_URL, url))
        if title:
            return str(uuid.uuid5(uuid.NAMESPACE_DNS, f"subject:{title}"))
    except Exception:
        pass
    return str(uuid.uuid4())

def transform_article(a: Dict[str, Any]) -> Dict[str, Any]:
    """
    article -> guid, subject, content, notes, topic
    """
    src = a.get("source") or {}
    title = (a.get("title") or "").strip() or None
    content = a.get("content") or a.get("description")
    url = a.get("url")
    source_name = src.get("name")

    # notes: עדיפות לקישור + מקור; אחרת תיאור
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
        "guid": _make_guid(a),
        "subject": title,
        "content": content,
        "notes": notes,
        "topic": topic,
    }
    # מחזירים רק עמודות שקיימות ושאינן None
    return {k: v for k, v in row.items() if k in ALLOWED_COLS and v is not None}

def take_from_payload(payload: Dict[str, Any] | List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    תומך בפורמטים:
    - list ישיר
    - {"articles": [...]}
    - {"data": {"articles": [...]}}
    """
    if isinstance(payload, list):
        articles = payload
    elif isinstance(payload, dict) and "articles" in payload:
        articles = payload.get("articles") or []
    else:
        articles = ((payload or {}).get("data") or {}).get("articles") or []

    rows = []
    for a in articles:
        row = transform_article(a)
        if not row.get("subject"):
            continue
        rows.append(row)
    return rows

def batch_insert(rows: List[Dict[str, Any]], table_name: str = "articles", chunk_size: int = 500):
    """
    הכנסה דרך REST (verify=False לעקיפת SSL מקומי).
    אם תרצי upsert על guid: צרי unique index ואז נעבור ל-on_conflict.
    """
    if not rows:
        return
    url = f"{REST_URL}/{table_name}"
    for i in range(0, len(rows), chunk_size):
        chunk = rows[i:i+chunk_size]
        r = requests.post(url, headers=HEADERS, json=chunk, timeout=30, verify=False)
        r.raise_for_status()

def ingest_payload(payload: Dict[str, Any] | List[Dict[str, Any]], table_name: str = "articles"):
    rows = take_from_payload(payload)
    if not rows:
        return {"inserted": 0, "note": "no valid rows after filtering (missing title/subject)"}
    batch_insert(rows, table_name=table_name)
    return {"inserted": len(rows)}
