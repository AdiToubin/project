"""
------------------------------------------------------------
 consumer_pipeline.py
------------------------------------------------------------
📋 תפקיד הקובץ:
----------------
זהו ה-Pipeline השלם שלך:
1️⃣ מקבל הודעה מ-Kafka (id + topic)
2️⃣ מסנן רק נושאים רלוונטיים (Sports / Politics / Fashion)
3️⃣ שולף את הכתבה המלאה מ-Supabase
4️⃣ מבצע ניתוח ישויות (NER) ב-Hugging Face
5️⃣ מוצא תמונה מתאימה ב-Cloudinary
6️⃣ שולח את הנתונים לאתר שלך (Flask) בזמן אמת
------------------------------------------------------------
"""

import os, json, requests
from kafka import KafkaConsumer
from dotenv import load_dotenv
from transformers import pipeline
import cloudinary
from cloudinary import Search

# ------------------------------------------------------------
# 🔹 שלב 1 – טעינת משתני סביבה
# ------------------------------------------------------------
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

SITE_API_URL = os.getenv("SITE_API_URL", "http://127.0.0.1:5000/new_article")

# הגדרות Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

KAFKA_TOPIC = "news-articles"
ALLOWED_TOPICS = ["Technology", "Defense", "Sports","General","Politics","Business","Entertainment","Health","Science","Fashion"]


# ------------------------------------------------------------
# 🔹 שלב 2 – טעינת מודל Hugging Face NER
# ------------------------------------------------------------
print("🔍 טוען מודל Hugging Face (NER)...")
ner_pipeline = pipeline(
    "ner",
    model="dbmdz/bert-large-cased-finetuned-conll03-english",
    aggregation_strategy="simple"
)
print("✅ מודל NER נטען בהצלחה.")

# ------------------------------------------------------------
# 🔹 שלב 3 – התחברות ל-Kafka
# ------------------------------------------------------------
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id="news-pipeline"
)
print(f"📡 מאזין ל-Kafka Topic: {KAFKA_TOPIC}")

# ------------------------------------------------------------
# 🔹 שלב 4 – פונקציה: שליפת כתבה מלאה מ-Supabase
# ------------------------------------------------------------
def fetch_article(article_id: str):
    url = f"{SUPABASE_URL}/rest/v1/articles"
    params = {
    "guid": f"eq.{article_id}",
    "select": "guid,topic,subject,content,created_at"
      }

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }

    try:
        r = requests.get(url, headers=headers, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        if isinstance(data, list) and data:
            return data[0]
        else:
            print(f"⚠ לא נמצאה כתבה עבור id={article_id}")
            return None
    except Exception as e:
        print(f"❌ שגיאה בשליפת כתבה מ-Supabase: {e}")
        return None

# ------------------------------------------------------------
# 🔹 שלב 5 – לולאת העיבוד הראשית (ה-Pipeline בפעולה)
# ------------------------------------------------------------
for msg in consumer:
    payload = msg.value
    article_id = payload.get("id")
    topic = payload.get("topic")

    # 🧠 שלב 1: סינון לפי נושא
    # 🧠 שלב 1: ניקוי ותקנון שם הנושא
    topic_clean = topic.strip().capitalize() if topic else ""

    # 🧩 שלב 2: בדיקה מול רשימת הנושאים המותרים
    if topic_clean not in ALLOWED_TOPICS:
       print("🧾 נושא שהגיע:", topic)
       print(f"⏩ מדלג על נושא לא רלוונטי: {topic_clean}")
       continue

    print(f"\n🆕 כתבה רלוונטית בנושא '{topic}' (id={article_id})")

    # 📰 שלב 2: שליפת כתבה מלאה מ-Supabase
    article = fetch_article(article_id)
    if not article:
        continue

    subject = article.get("subject", "(ללא כותרת)")
    content = article.get("content", "")
    print(f"📖 נושא הכתבה: {subject[:80]}")

    # 🤖 שלב 3: ניתוח ישויות (NER)
    try:
        entities = ner_pipeline(content[:1000])  # מגבילים לטקסט קצר יותר
        keywords = [e["word"] for e in entities]
        print("🧠 ישויות שזוהו:", keywords)
    except Exception as e:
        print("❌ שגיאה בניתוח NER:", e)
        continue

    # 🖼 שלב 4: בחירת תמונה לפי הישות המרכזית / נושא
    main_keyword = keywords[0] if keywords else topic
    print(f"🔑 מילת חיפוש עיקרית לתמונה: {main_keyword}")

    try:
        result = Search().expression(main_keyword).execute()
        if result.get("resources"):
            image_url = result["resources"][0]["secure_url"]
            print("✅ תמונה נמצאה:", image_url)
        else:
            image_url = "https://via.placeholder.com/800x400?text=No+Image+Found"
            print("⚠ לא נמצאה תמונה מתאימה.")
    except Exception as e:
        image_url = "https://via.placeholder.com/800x400?text=Error"
        print("❌ שגיאה בחיפוש תמונה:", e)

    # 🌐 שלב 5: שליחת הנתונים לאתר שלך בזמן אמת
    data_to_send = {
        "id": article_id,
        "topic": topic,
        "subject": subject,
        "content": content,
        "entities": keywords,
        "image_url": image_url
    }

    try:
        r = requests.post(SITE_API_URL, json=data_to_send)
        if r.ok:
            print("🚀 נשלחה כתבה לאתר בהצלחה.")
        else:
            print("⚠ שגיאה בשליחה לאתר:", r.text)
    except Exception as e:
        print("❌ שגיאה בחיבור לאתר:", e)

    print("------------------------------------------------------------")
