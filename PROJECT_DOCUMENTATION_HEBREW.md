# 📰 תיעוד פרויקט - News Processing & Image Enrichment Platform

## תוכן עניינים
1. [סקירה כללית](#סקירה-כללית)
2. [אדריכלות המערכת](#אדריכלות-המערכת)
3. [רכיבים ותפקידיהם](#רכיבים-ותפקידיהם)
4. [ניתוב API](#ניתוב-api)
5. [מודלים ומחלקות](#מודלים-ומחלקות)
6. [זרימת נתונים](#זרימת-נתונים)
7. [הגדרות סביבה](#הגדרות-סביבה)
8. [הוראות הפעלה](#הוראות-הפעלה)

---

## סקירה כללית

### על הפרויקט
פרויקט זה הוא מערכת מתקדמת לעיבוד חדשות עם העשרה בתמונות:

**יכולויות עיקריות:**
- 📡 הבאת חדשות מ-NewsAPI
- 🤖 סיווג אוטומטי לפי נושא באמצעות AI (Hugging Face)
- 💾 אחסון בסיס נתונים Supabase
- 📨 משלוח דרך Kafka message queue
- 🖼️ חיפוש ותמונות רלוונטיות מ-Pexels/Cloudinary
- 🌐 ממשקי משתמש: Flask + Gradio

### טכנולוגיות ראשיות
- **Framework:** Flask (Python)
- **Database:** Supabase (PostgreSQL)
- **Message Queue:** Apache Kafka
- **ML/NLP:** Hugging Face Transformers (xlm-roberta-large-xnli)
- **Image APIs:** Pexels, Cloudinary
- **UI:** Jinja2 Templates (Flask), Gradio
- **Deployment:** Heroku/Cloud (gunicorn + Python 3.11)

---

## אדריכלות המערכת

### תרשים הזרימה הכללי

```
┌─────────────────────────────────────────────────────────────┐
│                    FLASK APPLICATION (PORT 5000)            │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────┐     ┌──────────────────────┐ │
│  │    NewsController        │     │    ApiController     │ │
│  ├──────────────────────────┤     ├──────────────────────┤ │
│  │ - fetch_news()           │     │ - process()          │ │
│  │ - ingest_payload()       │     │ - calculate()        │ │
│  │ - fetch_and_ingest_once()│     │ - health()           │ │
│  └──────────────────────────┘     └──────────────────────┘ │
│           │                                  │               │
│           ▼                                  ▼               │
│  ┌──────────────────────────┐     ┌──────────────────────┐ │
│  │   ArticleModel           │     │  BusinessLogic       │ │
│  │ (Supabase Ops)           │     │  (Data Processing)   │ │
│  └──────────────────────────┘     └──────────────────────┘ │
│           │                                                  │
│           ▼                                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          Supabase Database (PostgreSQL)              │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │ articles table:                                │  │  │
│  │  │ - id (GUID), title, url, topic,               │  │  │
│  │  │ - image_url, publishedAt, etc.               │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
│           │                                                  │
│           ▼                                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          Kafka Message Queue (localhost:9092)        │  │
│  │  Topics:                                             │  │
│  │  - "news-articles" → Image Agent                    │  │
│  │  - "news.final" → Final Consumer                    │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                          │
         ┌────────────────┼────────────────┐
         ▼                ▼                ▼
    ┌─────────┐    ┌──────────────┐   ┌────────────┐
    │ Flask   │    │  Kafka       │   │  Gradio UI │
    │Templates│    │  Consumers   │   │ (Optional) │
    │         │    │  & Agents    │   │            │
    └─────────┘    └──────────────┘   └────────────┘
```

### שכבות אדריכלות

#### 1. **Controller Layer** (בקרה)
טיפול בבקשות HTTP וניתוב ללוגיקה עסקית
- `NewsController`: ניהול חדשות
- `ApiController`: פעולות API כלליות

#### 2. **Model Layer** (מודלים)
ביצוע פעולות עיסקיות וגישה לנתונים
- `ArticleModel`: פעולות מאמרים בסופיין
- `BusinessLogic`: לוגיקה עיסקית כללית
- `NewsFetcher`: קבלת חדשות מ-API
- `KafkaUtils`: שליחת וקבלת הודעות

#### 3. **View Layer** (תצוגה)
עיצוב תגובות HTTP
- `json_response.py`: תגובות JSON סטנדרטיות
- `gradio_ui.py`: ממשק אינטראקטיבי (אופציונלי)

#### 4. **External Services** (שירותים חיצוניים)
- **NewsAPI**: קבלת חדשות
- **Supabase**: אחסון נתונים
- **Hugging Face**: סיווג נושאים בעזרת AI
- **Kafka**: תור ההודעות
- **Pexels/Cloudinary**: חיפוש והעלאת תמונות

---

## רכיבים ותפקידיהם

### 📁 מבנה תיקיות

```
c:\project/
├── app.py                          # נקודת כניסה ראשונית
├── requirements.txt                # תלויות Python
├── Procfile                        # הגדרת Heroku
├── runtime.txt                     # גרסת Python
├── .env                            # משתנים סביבה (סודות)
├── news.json                       # קייש מקומי של חדשות
│
├── app_mvc/                        # יישום MVC ראשי
│   ├── controllers/
│   │   ├── __init__.py
│   │   ├── api_controller.py       # בקר API כללי
│   │   └── news_controller.py      # בקר חדשות
│   ├── models/
│   │   ├── __init__.py
│   │   ├── article_model.py        # מודל מאמרים
│   │   ├── business_logic.py       # לוגיקה עיסקית
│   │   └── news_service.py         # שירות חדשות (NewsAPI)
│   └── views/
│       ├── __init__.py
│       └── json_response.py        # תגובות JSON
│
├── mvc_view/                       # עיבוד תמונות ו Kafka pipeline
│   ├── controllers/
│   │   └── image_agent.py          # סוכן תמונות (Kafka consumer)
│   ├── models/
│   │   ├── kafka_utils.py          # כלים Kafka
│   │   ├── image_service.py        # שירות תמונות (FastAPI)
│   │   ├── image_final_consumer.py # צרכן סופי (עדכון DB)
│   │   └── consumer_pipeline.py    # pipeline NER + תמונות
│   ├── views/
│   │   └── gradio_ui.py            # ממשק Gradio
│   └── templates/
│       ├── index.html              # דף בית עברית
│       └── news.html               # דף חדשות עברית
│
└── x/                              # שירותים אופציונליים (מושבתים)
    └── __init__.py
```

---

## ניתוב API

### 1. **GET /** - דף הבית
```
Route: GET /
Response: HTML (index.html)
Status: 200
Purpose: דף ברוכים הבאים בעברית
```

### 2. **GET /news** - רשימת חדשות
```
Route: GET /news
Response: HTML (news.html) עם רשימת מאמרים
Status: 200 (בהצלחה) | 404 (קובץ לא נמצא) | 500 (שגיאה)
Purpose: הצגת מאמרים מ-news.json המקומי
```

### 3. **GET /fetch-news** - קבלת חדשות מ-API
```
Route: GET /fetch-news
Response: JSON עם מאמרים טריים
Status: 200 (בהצלחה) | 500 (שגיאה API)
Purpose: הבאת חדשות טרופות מ-NewsAPI

Response Format:
{
  "status": "success",
  "data": {
    "articles": [
      {
        "title": "חדשות כותרת",
        "description": "תיאור",
        "url": "https://...",
        "urlToImage": "https://...",
        "topic": "Technology|Sports|...",
        "guid": "uuid-v5-hash"
      }
    ]
  }
}
```

### 4. **POST /api/process** - עיבוד נתונים
```
Route: POST /api/process
Content-Type: application/json
Request Body: כל נתונים JSON
Response: {"status": "success|error", "result": {...}}
Status: 200 (בהצלחה) | 400 (שגיאה)
Purpose: עיבוד כללי של נתונים
```

### 5. **POST /api/calculate** - חישובים מתמטיים
```
Route: POST /api/calculate
Content-Type: application/json

Request Body:
{
  "num1": 10,              // מספר ראשון
  "num2": 5,               // מספר שני
  "operation": "add"       // add|subtract|multiply|divide
}

Response Success:
{
  "status": "success",
  "result": 15,
  "operation": "add"
}

Response Error:
{
  "status": "error",
  "message": "division by zero"
}

Status: 200 (בהצלחה) | 400 (שגיאה)
Supported Operations: add, subtract, multiply, divide
```

### 6. **GET /health** - בדיקת בריאות
```
Route: GET /health
Response: {"status": "healthy"}
Status: 200 (תמיד אם שרת פעיל)
Purpose: בדיקה שהשרת חי (Docker, Kubernetes, LB monitoring)
Response Time: <1ms
```

---

## מודלים ומחלקות

### ArticleModel (app_mvc/models/article_model.py)

**תפקיד:** ניהול פעולות מאמרים בסופיין

**מתודות עיקריות:**

1. **take_from_payload(payload)**
   - הוצאת מאמרים חוקיים מעומס
   - סינון: מסיר מאמרים ללא כותרת/נושא
   - פלט: רשימת מאמרים מעובדים

2. **transform_article(raw_article)**
   - המרה מפורמט NewsAPI לפורמט בסופיין
   - יצירת GUID (UUID v5) ייחודי
   - הוספת timestamp

3. **guess_topic(title, description)**
   - סיווג נושא באמצעות Hugging Face NER
   - אופציות: Sports, Economy, Defense, Weather, Technology, Politics, World, General
   - ג return בחזרה נושא מסווג

4. **batch_insert(rows, table_name)**
   - הוספה בתוך סופיין בחבילות של 500
   - אופטימיזציה עבור ביצועים
   - טיפול בשגיאות מסד נתונים

### NewsFetcher (app_mvc/models/news_service.py)

**תפקיד:** קבלת חדשות מ-NewsAPI

**מתודות:**

1. **fetch_top_headlines(country="us")**
   - קבלת חדשות עליונות מ-newsapi.org
   - מסנן לפי ארץ
   - timeout: 20 שניות
   - ניסיון עם SSL לא מאומת (פיתוח מקומי)

### BusinessLogic (app_mvc/models/business_logic.py)

**תפקיד:** לוגיקה עיסקית כללית

**מתודות:**

1. **process_data(data)**
   - עיבוד כללי של נתונים
   - transformation וvalidation

2. **calculate(num1, num2, operation)**
   - חישובים: add, subtract, multiply, divide
   - טיפול בשגיאות (div by zero)

### KafkaUtils (mvc_view/models/kafka_utils.py)

**תפקיד:** כלים להפקה/צריכה של Kafka

**פונקציות:**

1. **create_producer()**
   - יצירת Kafka producer
   - Server: localhost:9092
   - Serializer: JSON

2. **create_consumer(topic, group_id)**
   - יצירת Kafka consumer
   - צרכן קבוצה עבור ניהול offset

---

## זרימת נתונים

### זרימה 1: הבאה וטעינה של חדשות

```
Application Startup
        │
        ▼
fetch_and_ingest_once()
        │
    ┌───┴───┐
    │       │
    ▼       ▼
  (cache  (API)
   exists?)
    │       │
    ▼       ▼
  Load    Fetch from
  JSON    NewsAPI
    │       │
    │       ▼
    │    Save to JSON
    │    (cache)
    │       │
    └───┬───┘
        │
        ▼
   ingest_payload()
        │
    ┌───┼───┬────────┐
    │   │   │        │
    ▼   ▼   ▼        ▼
  Validate Transform Classify Batch Insert
  Articles to DB   Topics   to Supabase
    │   │   │        │
    └───┼───┼────────┘
        │   │
        │   ▼
        │  Produce to Kafka
        │  Topic: "news-articles"
        │  Message: {id, topic}
        │
        ▼
    Response
    {"inserted": count}
```

### זרימה 2: עיבוד תמונות (אופציונלי)

```
Kafka Topic: "news-articles"
        │
        ▼
image_agent (Consumer)
        │
        ▼
   Search Images
   (Pexels API)
        │
        ▼
  Upload to Cloudinary
        │
        ▼
Kafka Topic: "news.final"
        │
        ▼
image_final_consumer
        │
        ▼
Update Supabase
with Image URLs
```

---

## הגדרות סביבה

### משתנים נדרשים (.env file)

```bash
# ═══════════════════════════════════════════════════════════════
# DATABASE CONFIGURATION
# ═══════════════════════════════════════════════════════════════
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# ═══════════════════════════════════════════════════════════════
# NEWS API
# ═══════════════════════════════════════════════════════════════
NEWSAPI_KEY=your-newsapi-key

# ═══════════════════════════════════════════════════════════════
# IMAGE APIs
# ═══════════════════════════════════════════════════════════════
PEXELS_API_KEY=your-pexels-api-key
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# ═══════════════════════════════════════════════════════════════
# APPLICATION SETTINGS
# ═══════════════════════════════════════════════════════════════
SECRET_KEY=your-strong-secret-key-here
PORT=5000

# ═══════════════════════════════════════════════════════════════
# FEATURE FLAGS
# ═══════════════════════════════════════════════════════════════
NO_AGENTS=1                    # Set to 1 to disable background services
FEATURE_TOPICS=Technology,Defense,Sports   # Topics to feature in Gradio UI
IMAGE_TOPICS=Technology,World,Sports       # Topics to process images for

# ═══════════════════════════════════════════════════════════════
# KAFKA (if enabled)
# ═══════════════════════════════════════════════════════════════
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
```

### משתנים אופציונליים

```bash
DEBUG=False                    # Flask debug mode (not recommended)
FLASK_ENV=production
DATABASE_URL=                  # Alternative DB connection string
```

---

## הוראות הפעלה

### הקדם-דרישות

```bash
# Python 3.11+
python --version

# pip (מנהל חבילות)
pip --version
```

### התקנה מקומית

```bash
# 1. Clone repository
git clone https://github.com/AdiToubin/project.git
cd project

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file with required variables
cp .env.example .env
# Edit .env with your API keys

# 5. Run application
python app.py
```

### פתיחה בדפדפן

```
http://localhost:5000/          # דף הבית
http://localhost:5000/news      # רשימת חדשות
http://localhost:5000/health    # בדיקת בריאות
```

### הפעלה בייצור (Production)

```bash
# Using gunicorn
gunicorn app:app --bind 0.0.0.0:5000 --workers 4

# Or deploy to Heroku
git push heroku main
```

### Docker

```bash
# Build image
docker build -t news-app .

# Run container
docker run -p 5000:5000 --env-file .env news-app

# Health check
curl http://localhost:5000/health
```

---

## בעיות נפוצות

### 1. "NEWSAPI_KEY not found"
**פתרון:** יש להוסיף NEWSAPI_KEY ל-.env file

### 2. "Kafka connection refused"
**פתרון:** וודא שBroker של Kafka פעיל על localhost:9092
```bash
# בדוק אם Kafka פעיל
docker ps | grep kafka
```

### 3. "Supabase connection error"
**פתרון:** בדוק משתנים SUPABASE_URL ו-SUPABASE_SERVICE_ROLE_KEY

### 4. "SSL error in local development"
**פתרון:** SSL מנוטרל כברירת מחדל לפיתוח מקומי

---

## עוד מידע

### קישורים שימושיים
- [Flask Documentation](https://flask.palletsprojects.com/)
- [NewsAPI Documentation](https://newsapi.org/docs)
- [Supabase Docs](https://supabase.com/docs)
- [Kafka Documentation](https://kafka.apache.org/documentation/)
- [Hugging Face](https://huggingface.co/)

### צרו קשר עם מפתחים
- GitHub Issues: [project/issues](https://github.com/AdiToubin/project/issues)
- Email: support@example.com

---

**תאריך עדכון:** אוקטובר 2024
**גרסה:** 1.0.0
**Status:** Active Development
