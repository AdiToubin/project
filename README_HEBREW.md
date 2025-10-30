# 📰 מערכת עיבוד חדשות עם העשרה בתמונות

![Python Version](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🌟 סקירה כללית

מערכת מתקדמת לעיבוד חדשות עם הכשרה בתמונות רלוונטיות. המערכת קוראת חדשות מ-NewsAPI, מסווגת אותן לפי נושא באמצעות AI, שומרת בסופיין, ומחפשת תמונות רלוונטיות.

### ✨ יכולויות עיקריות

- 📡 **הבאת חדשות** מ-NewsAPI בזמן אמת
- 🤖 **סיווג אוטומטי** של נושאים באמצעות Hugging Face
- 💾 **אחסון בסיס נתונים** ב-Supabase
- 📨 **משלוח דרך Kafka** להנדסה אסינכרונית
- 🖼️ **חיפוש תמונות** מ-Pexels ו-Cloudinary
- 🌐 **ממשקי משתמש** Flask + Gradio (אופציונלי)
- ✅ **בדיקות בריאות** לניטור וקנטיינרים

---

## 🚀 התחלה מהירה

### דרישות מראש
- Python 3.11 ומעלה
- pip (מנהל חבילות)
- חשבון Supabase (או בסיס נתונים אחר)
- API key מ-NewsAPI

### התקנה

```bash
# 1. Clone the repository
git clone https://github.com/AdiToubin/project.git
cd project

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create environment file
cp .env.example .env
# Edit .env with your API keys

# 5. Run application
python app.py
```

### גישה לאפליקציה

```
🏠 דף הבית:        http://localhost:5000/
📰 רשימת חדשות:    http://localhost:5000/news
✅ בדיקת בריאות:   http://localhost:5000/health
🔄 קבלת חדשות:    http://localhost:5000/fetch-news
```

---

## 📋 משתנים סביבה (Environment Variables)

### חובה

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-key-here
NEWSAPI_KEY=your-newsapi-key-here
SECRET_KEY=your-secret-key-here
```

### אופציונלי

```bash
PEXELS_API_KEY=your-pexels-key           # עבור חיפוש תמונות
CLOUDINARY_CLOUD_NAME=your-cloud-name    # עבור אחסון תמונות
NO_AGENTS=1                              # להשבתת שירותים רקע
```

📖 **עיון מלא:** ראה `PROJECT_DOCUMENTATION_HEBREW.md`

---

## 🏗️ אדריכלות המערכת

```
┌─────────────────────────┐
│  Flask Application      │
│  (Port 5000)            │
├─────────────────────────┤
│  Controllers            │
│  • NewsController       │
│  • ApiController        │
├─────────────────────────┤
│  Models                 │
│  • ArticleModel         │
│  • BusinessLogic        │
│  • NewsFetcher          │
├─────────────────────────┤
│  Supabase Database      │
└─────────────────────────┘
          ↓
    Kafka Queue
          ↓
   Optional Services
   • Image Processing
   • Gradio UI
```

---

## 🔌 נקודות קצה של API

### GET /
דף הבית הראשי בעברית

### GET /news
רשימת מאמרים מהקאש המקומי

### GET /fetch-news
הבאת חדשות טרופות מהAPI וסיווגן

**Response:**
```json
{
  "status": "success",
  "data": {
    "articles": [
      {
        "title": "כותרת",
        "description": "תיאור",
        "topic": "Technology",
        "guid": "550e8400-...",
        "url": "https://..."
      }
    ]
  }
}
```

### GET /health
בדיקת בריאות היישום

**Response:**
```json
{
  "status": "healthy"
}
```

### POST /api/calculate
ביצוע חישובים מתמטיים

**Request:**
```json
{
  "num1": 10,
  "num2": 5,
  "operation": "multiply"
}
```

**Response:**
```json
{
  "status": "success",
  "result": 50
}
```

### POST /api/process
עיבוד נתונים כלליים

---

## 📁 מבנה הפרויקט

```
project/
├── app.py                      # נקודת הכניסה
├── requirements.txt            # תלויויות
├── PROJECT_DOCUMENTATION_*.md  # תיעוד מלא
│
├── app_mvc/                    # יישום MVC ראשי
│   ├── controllers/
│   │   ├── news_controller.py
│   │   └── api_controller.py
│   ├── models/
│   │   ├── article_model.py
│   │   ├── business_logic.py
│   │   └── news_service.py
│   └── views/
│       └── json_response.py
│
├── mvc_view/                   # עיבוד תמונות
│   ├── models/
│   │   ├── image_service.py
│   │   ├── consumer_pipeline.py
│   │   └── kafka_utils.py
│   ├── views/
│   │   └── gradio_ui.py
│   └── templates/
│       ├── index.html
│       └── news.html
```

---

## 🛠️ הפעלה ופיתוח

### הפעלה מקומית

```bash
python app.py
```

### הפעלה עם Gunicorn (ייצור)

```bash
pip install gunicorn
gunicorn app:app --bind 0.0.0.0:5000 --workers 4
```

### הפעלה עם Docker

```bash
docker build -t news-app .
docker run -p 5000:5000 --env-file .env news-app
```

### Heroku

```bash
heroku create your-app-name
heroku config:set NEWSAPI_KEY=your-key
git push heroku main
```

---

## 📊 נושאים מתוך תמיכה

המערכת תומכת בסיווג לנושאים הבאים:

- 📰 ידיעות כלליות (General)
- ⚽ ספורט (Sports)
- 💻 טכנולוגיה (Technology)
- 💰 כלכלה (Economy)
- 🛡️ ביטחון (Defense)
- ☀️ מזג אוויר (Weather)
- 🌍 חדשות עולם (World)
- 🏛️ פוליטיקה (Politics)

---

## ⚙️ הגדרות מתקדמות

### Kafka Consumer/Producer
אם אתה משתמש בשירותים ברקע:

```bash
# התקן Kafka
docker run -d -p 9092:9092 -p 2181:2181 confluentinc/cp-kafka:latest

# הפעל צרכנים
python mvc_view/models/consumer_pipeline.py
python mvc_view/models/image_final_consumer.py
```

### שירות תמונות (FastAPI)

```bash
python mvc_view/models/image_service.py
```

יופעל על Port 8004

### Gradio UI

```bash
python -c "from mvc_view.views.gradio_ui import run_gradio; run_gradio()"
```

יופעל על Port 7860

---

## 🐛 פתרון בעיות

### "NEWSAPI_KEY not found"
```bash
# ודא שה-.env יש לך:
NEWSAPI_KEY=your-actual-key
```

### "Kafka connection refused"
```bash
# וודא ש-Kafka פעיל:
docker ps | grep kafka
```

### "Supabase connection error"
```bash
# בדוק את:
SUPABASE_URL=...
SUPABASE_SERVICE_ROLE_KEY=...
```

---

## 📖 תיעוד מפורט

- 📘 [תיעוד בעברית](./PROJECT_DOCUMENTATION_HEBREW.md) - מלא ומפורט בעברית
- 📗 [תיעוד באנגלית](./PROJECT_DOCUMENTATION_ENGLISH.md) - מלא ומפורט באנגלית
- 📋 [סיכום תיעוד](./DOCUMENTATION_SUMMARY.md) - סקירה של מה תומך

---

## 🤝 תרומה

רוצה להתרום? בטוח!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 רישיון

פרויקט זה תחת רישיון MIT - ראה את `LICENSE` קובץ לפרטים.

---

## 👨‍💻 מנהלים

- **AdiToubin** - מייסד ומפתח ראשי

---

## 💬 תמיכה

יש בעיות? שאלות?

- 🐛 [GitHub Issues](https://github.com/AdiToubin/project/issues)
- 📧 Email: support@example.com
- 💬 Discussions: [GitHub Discussions](https://github.com/AdiToubin/project/discussions)

---

## 🔗 קישורים שימושיים

- [NewsAPI Documentation](https://newsapi.org/docs)
- [Supabase Docs](https://supabase.com/docs)
- [Flask Tutorial](https://flask.palletsprojects.com/)
- [Hugging Face](https://huggingface.co/)
- [Kafka Tutorial](https://kafka.apache.org/documentation/)

---

## 📊 סטטיסטיקות

- **שפות:** Python 3.11+
- **תלויויות:** 20+
- **נקודות קצה API:** 6
- **מודלים:** 4
- **בקרים:** 2
- **תיעוד:** 3000+ שורות

---

**יצור ב-2024 עם ❤️**

```
   ___     _ _ _____           _
  / _ \   | | |  ___| ___  ___| |
 / (_) \  | | | |_   / _ \/ _ \ |
 \___  /  | | |  _|  |  __/ (__| |
    |_/  /|\| |_|    \___|\___|_|
         /_/ \
```

**[⬆ חזור לעמוד ראשי](#)**
