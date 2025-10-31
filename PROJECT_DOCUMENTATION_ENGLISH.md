# 📰 Project Documentation - News Processing & Image Enrichment Platform

## Table of Contents
1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Components & Responsibilities](#components--responsibilities)
4. [API Routes](#api-routes)
5. [Models & Classes](#models--classes)
6. [Data Flow](#data-flow)
7. [Environment Configuration](#environment-configuration)
8. [Getting Started](#getting-started)

---

## Project Overview

### About This Project
This is an advanced news processing system with automatic image enrichment:

**Core Capabilities:**
- 📡 Fetch news articles from NewsAPI
- 🤖 Automatic topic classification using AI (Hugging Face)
- 💾 Store articles in Supabase database
- 📨 Distribute via Kafka message queue

## תיעוד קצר בעברית

קובץ זה החליף את התיעוד הארוך באנגלית ותמצת את המידע החשוב בקצרה.

מה זה?
- מערכת לאיסוף חדשות, סיווג נושאים והעשרת תמונות.

רכיבים עיקריים
- Flask — ממשק ו־API (פורט 5000)
- NewsFetcher — משוך חדשות מ־NewsAPI
- ArticleModel — המרה והכנסה ל־Supabase
- Kafka (אופציונלי) — תורים לעיבוד אסינכרוני
- Image pipeline (Pexels + Cloudinary) — חיפוש והעלאת תמונות
- Gradio (אופציונלי) — ממשק אינטראקטיבי מקומי

קבצים חשובים
- `app.py` — כניסה ראשית, נקודת התחלה להרצה
- `app_mvc/controllers/news_controller.py` — לוגיקת משיכה והכנסה
- `app_mvc/models/article_model.py` — המרה, סיווג והכנסה ל־DB
- `app_mvc/models/news_service.py` — לקוח ל־NewsAPI
- `news.json` — קאש מקומי של חדשות (בשורש הפרויקט)

API מהיר (רלוונטי)
- GET /         — דף הבית
- GET /news     — רשימת מאמרים (מקרא מקומי: `news.json`)
- GET /fetch-news — משוך חדשות מ־NewsAPI (JSON)
- POST /refresh-news — רענון וטעינה (קיים ב־app.py)
- GET /health   — בדיקת בריאות

הערות תפעוליות
- קרא/עדכן משתני סביבה ב־`.env` (NEWSAPI_KEY, SUPABASE_*, CLOUDINARY_*)
- לאפשר רק שירותים שיש לך: NO_AGENTS=1 כדי להשבית שירותים רקע

התקנה מהירה (חלון פקודה, Windows)
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# ערכי את .env עם המפתחות שלך
python app.py
```

איפה כותבים ל־news.json?
- הקובץ נוצר ומעודכן ב־`app_mvc/controllers/news_controller.py` בתוך הפונקציה `fetch_and_ingest_once()`.

הערות לגבי בעיות נפוצות
- אם רואה `inserted: 0` — בדוק את `NEWSAPI_KEY`, את מבנה התגובה (`articles`) ואת הפילטר על כותרות (ArticleModel מסיר מאמרים בלי title).
- אם יש שגיאות נתיב — ודא שהנתיב ל־`news.json` תקין; עדיפו נתיב יחסתי (root של הפרויקט) או משתנה ENV `NEWS_JSON_PATH`.

לסיוע נוסף
- אם תרצי, אוכל לעדכן את הקבצים כדי להשתמש בנתיב יחסי ו/או להוסיף הודעות דיאגנוסטיקה קצרות. תגידי "תתקן" ואני איישם שינויים קטנים עם גיבוי.

**עודכן:** October 2025
