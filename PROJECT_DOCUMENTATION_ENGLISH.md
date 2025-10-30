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
- 🖼️ Search and fetch relevant images from Pexels/Cloudinary
- 🌐 User interfaces: Flask templates + Gradio (optional)

### Technologies Stack
- **Framework:** Flask (Python 3.11)
- **Database:** Supabase (PostgreSQL)
- **Message Queue:** Apache Kafka 2.x
- **ML/NLP:** Hugging Face (xlm-roberta-large-xnli)
- **Image APIs:** Pexels, Cloudinary
- **UI:** Jinja2 Templates, Gradio
- **Deployment:** Heroku, Docker, Cloud Platforms
- **Production Server:** Gunicorn WSGI

---

## System Architecture

### High-Level Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                 FLASK APPLICATION (PORT 5000)               │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────┐     ┌──────────────────────┐ │
│  │    NewsController        │     │    ApiController     │ │
│  ├──────────────────────────┤     ├──────────────────────┤ │
│  │ • fetch_news()           │     │ • process()          │ │
│  │ • ingest_payload()       │     │ • calculate()        │ │
│  │ • fetch_and_ingest_once()│     │ • health()           │ │
│  └──────────────────────────┘     └──────────────────────┘ │
│           │                                  │               │
│           ▼                                  ▼               │
│  ┌──────────────────────────┐     ┌──────────────────────┐ │
│  │   ArticleModel           │     │  BusinessLogic       │ │
│  │ (Supabase Operations)    │     │  (Data Processing)   │ │
│  └──────────────────────────┘     └──────────────────────┘ │
│           │                                                  │
│           ▼                                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │    Supabase Database (PostgreSQL)                    │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │ articles table:                                │  │  │
│  │  │ • id (GUID), title, url, topic, image_url      │  │  │
│  │  │ • publishedAt, content, source, etc.           │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
│           │                                                  │
│           ▼                                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │       Kafka Message Queue (localhost:9092)           │  │
│  │  Topics:                                             │  │
│  │  • "news-articles" → ImageAgent Consumer            │  │
│  │  • "news.final" → FinalConsumer for DB update       │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                          │
         ┌────────────────┼────────────────┐
         ▼                ▼                ▼
    ┌─────────┐    ┌──────────────┐   ┌────────────┐
    │ Flask   │    │  Kafka       │   │  Gradio UI │
    │Templates│    │  Consumers   │   │ (Optional) │
    │(HTML)   │    │  & Agents    │   │ (Port 7860)│
    └─────────┘    └──────────────┘   └────────────┘
```

### Architectural Layers

#### 1. **Controller Layer** (Request Handling)
Routes HTTP requests to business logic
- `NewsController`: Article fetching and ingestion
- `ApiController`: General API operations

#### 2. **Model Layer** (Business Logic & Data)
Core business logic and database operations
- `ArticleModel`: Article operations in Supabase
- `BusinessLogic`: General business logic
- `NewsFetcher`: NewsAPI integration
- `KafkaUtils`: Kafka producer/consumer factory

#### 3. **View Layer** (Response Formatting)
Standardized response formats
- `json_response.py`: JSON response utilities
- `gradio_ui.py`: Interactive web interface (optional)

#### 4. **External Services** (Third-party APIs)
- **NewsAPI:** Article fetching
- **Supabase:** Data persistence
- **Hugging Face:** AI-based topic classification
- **Kafka:** Message distribution
- **Pexels/Cloudinary:** Image search and hosting

---

## Components & Responsibilities

### 📁 Directory Structure

```
c:\project/
├── app.py                          # Main entry point
├── requirements.txt                # Python dependencies
├── Procfile                        # Heroku deployment config
├── runtime.txt                     # Python version (3.11.0)
├── .env                            # Environment variables (secrets)
├── news.json                       # Local news cache
│
├── app_mvc/                        # Main MVC Application
│   ├── controllers/
│   │   ├── __init__.py
│   │   ├── api_controller.py       # General API endpoints
│   │   └── news_controller.py      # News endpoints
│   ├── models/
│   │   ├── __init__.py
│   │   ├── article_model.py        # Article operations
│   │   ├── business_logic.py       # Core business logic
│   │   └── news_service.py         # NewsAPI integration
│   └── views/
│       ├── __init__.py
│       └── json_response.py        # JSON response formatting
│
├── mvc_view/                       # Image Processing & Kafka Pipeline
│   ├── controllers/
│   │   └── image_agent.py          # Kafka image consumer
│   ├── models/
│   │   ├── kafka_utils.py          # Kafka factory functions
│   │   ├── image_service.py        # FastAPI image service
│   │   ├── image_final_consumer.py # Final image consumer
│   │   └── consumer_pipeline.py    # NER + Image pipeline
│   ├── views/
│   │   └── gradio_ui.py            # Gradio web interface
│   └── templates/
│       ├── index.html              # Homepage (Hebrew)
│       └── news.html               # News list (Hebrew)
│
└── x/                              # Optional services (disabled by default)
    └── __init__.py
```

---

## API Routes

### 1. **GET /** - Homepage
```
Route: GET /
Response: HTML (index.html)
Status Code: 200 OK
Content-Type: text/html; charset=utf-8
Purpose: Display welcome page with site information
```

### 2. **GET /news** - News List
```
Route: GET /news
Response: HTML (news.html) with article list
Status: 200 (success) | 404 (file not found) | 500 (error)
Purpose: Display cached news articles from local JSON file
```

### 3. **GET /fetch-news** - Fetch Fresh News
```
Route: GET /fetch-news
Response: JSON with latest articles
Status: 200 (success) | 500 (API error)
Purpose: Fetch fresh news from NewsAPI, classify, and return

Response Example:
{
  "status": "success",
  "data": {
    "articles": [
      {
        "title": "Breaking News Title",
        "description": "Article description",
        "url": "https://example.com/article",
        "urlToImage": "https://example.com/image.jpg",
        "topic": "Technology",
        "guid": "550e8400-e29b-41d4-a716-446655440000",
        "publishedAt": "2024-01-15T10:30:00Z"
      }
    ]
  }
}
```

### 4. **POST /api/process** - Process Data
```
Route: POST /api/process
Content-Type: application/json
Request Body: Any JSON object to process
Response: {"status": "success|error", "result": {...}}
Status: 200 (success) | 400 (error)
Purpose: Generic data processing endpoint
```

### 5. **POST /api/calculate** - Mathematics
```
Route: POST /api/calculate
Content-Type: application/json

Request Body:
{
  "num1": 10,               // First number
  "num2": 5,                // Second number
  "operation": "add"        // Operation: add|subtract|multiply|divide
}

Success Response (200):
{
  "status": "success",
  "result": 15,
  "operation": "add",
  "operands": [10, 5]
}

Error Response (400):
{
  "status": "error",
  "message": "division by zero"
}

Supported Operations:
• add: num1 + num2
• subtract: num1 - num2
• multiply: num1 * num2
• divide: num1 / num2 (fails if num2 == 0)
```

### 6. **GET /health** - Health Check
```
Route: GET /health
Response: {"status": "healthy"}
Status: Always 200 OK (if server is running)
Purpose: Health monitoring for Docker, Kubernetes, load balancers
Response Time: <1ms
Use Cases:
• Docker container health checks
• Kubernetes liveness probes
• Load balancer monitoring
• Uptime monitoring services (Datadog, Prometheus, etc.)
```

---

## Models & Classes

### ArticleModel (app_mvc/models/article_model.py)

**Responsibility:** Article operations in Supabase database

**Key Methods:**

1. **take_from_payload(payload: dict) → list**
   - Extract valid articles from API/file payload
   - Filter out articles missing title/subject
   - Return processed article list

2. **transform_article(raw_article: dict) → dict**
   - Convert from NewsAPI format to database format
   - Generate unique GUID (UUID v5 based on URL)
   - Add timestamp and metadata

3. **guess_topic(title: str, description: str) → str**
   - Classify article topic using Hugging Face NER
   - Available topics: Sports, Economy, Defense, Weather, Technology, Politics, World, General
   - Return classified topic string

4. **batch_insert(rows: list, table_name: str) → int**
   - Insert articles to Supabase in chunks of 500
   - Optimize for performance
   - Handle database errors gracefully

### NewsService (app_mvc/models/news_service.py)

**Responsibility:** NewsAPI integration

**Key Methods:**

1. **fetch_top_headlines(country: str) → dict**
   - Fetch top headlines from newsapi.org
   - Filter by country (default: "us")
   - Timeout: 20 seconds
   - Returns: {"data": {"articles": [...]}}

### BusinessLogic (app_mvc/models/business_logic.py)

**Responsibility:** General business logic operations

**Key Methods:**

1. **process_data(data: dict) → dict**
   - Generic data processing
   - Validation and transformation
   - Return: {"status": "success", "result": {...}}

2. **calculate(num1: float, num2: float, operation: str) → dict**
   - Arithmetic operations: add, subtract, multiply, divide
   - Error handling: division by zero, invalid operation
   - Return: {"result": value, "operation": op}

### KafkaUtils (mvc_view/models/kafka_utils.py)

**Responsibility:** Kafka producer/consumer factory

**Key Functions:**

1. **create_producer(bootstrap_servers: str)**
   - Create Kafka producer instance
   - Default broker: localhost:9092
   - Serializer: JSON

2. **create_consumer(topic: str, group_id: str)**
   - Create Kafka consumer instance
   - Join consumer group for offset management
   - Auto-commit offsets

---

## Data Flow

### Flow 1: News Fetch & Ingest (Startup)

```
Application Startup
        │
        ▼
fetch_and_ingest_once()
        │
    ┌───┴───────────┐
    │               │
    ▼               ▼
Check Local      (No Cache)
Cache (news.json)    │
    │                ▼
    │ (Cache Found)  Fetch from
    │ │              NewsAPI
    │ │                │
    │ └────────────────┤
    │                  ▼
    │            Save to JSON
    │            (for next restart)
    │                  │
    └──────┬───────────┘
           │
           ▼
    ingest_payload()
           │
    ┌──────┼──────┬────────┐
    │      │      │        │
    ▼      ▼      ▼        ▼
Validate Transform Classify Batch Insert
Articles  to DB   Topics   to Supabase
    │      │      │        │
    └──────┴──────┴────────┘
               │
               ▼
          Produce to Kafka
          Topic: "news-articles"
          Message: {"id": guid, "topic": topic}
               │
               ▼
          Response
          {"inserted": count}
```

### Flow 2: Image Processing Pipeline (Optional)

```
Kafka: "news-articles"
        │
        ▼
ImageAgent (Consumer)
        │
        ▼
Search Images
(Pexels API)
        │
        ▼
Upload to
Cloudinary
        │
        ▼
Kafka: "news.final"
        │
        ▼
FinalConsumer
        │
        ▼
Update Supabase
with Image URLs
```

---

## Environment Configuration

### Required Environment Variables

Create a `.env` file in the project root:

```bash
# ═══════════════════════════════════════════════════════════════
# DATABASE CONFIGURATION
# ═══════════════════════════════════════════════════════════════
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here

# ═══════════════════════════════════════════════════════════════
# NEWS API
# ═══════════════════════════════════════════════════════════════
NEWSAPI_KEY=your-newsapi-key-here

# ═══════════════════════════════════════════════════════════════
# IMAGE SERVICES
# ═══════════════════════════════════════════════════════════════
PEXELS_API_KEY=your-pexels-api-key-here
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-cloudinary-api-key
CLOUDINARY_API_SECRET=your-cloudinary-secret

# ═══════════════════════════════════════════════════════════════
# APPLICATION SETTINGS
# ═══════════════════════════════════════════════════════════════
SECRET_KEY=your-strong-secret-key-min-32-chars
PORT=5000

# ═══════════════════════════════════════════════════════════════
# FEATURE FLAGS
# ═══════════════════════════════════════════════════════════════
NO_AGENTS=1                              # 1 = disable background services
FEATURE_TOPICS=Technology,Defense,Sports # Featured topics in Gradio UI
IMAGE_TOPICS=Technology,World,Sports     # Topics to fetch images for

# ═══════════════════════════════════════════════════════════════
# KAFKA CONFIGURATION (if using background services)
# ═══════════════════════════════════════════════════════════════
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
```

### Optional Variables

```bash
DEBUG=False              # Flask debug mode (use False in production)
FLASK_ENV=production     # Flask environment
LOG_LEVEL=info          # Logging level: debug, info, warning, error
```

---

## Getting Started

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Local Setup

```bash
# 1. Clone the repository
git clone https://github.com/AdiToubin/project.git
cd project

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
cp .env.example .env
# Edit .env with your API keys

# 5. Run the application
python app.py
```

### Access the Application

```
Homepage:        http://localhost:5000/
News Page:       http://localhost:5000/news
Health Check:    http://localhost:5000/health
Fetch News API:  http://localhost:5000/fetch-news
```

### Production Deployment

#### Using Gunicorn

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn app:app --bind 0.0.0.0:5000 --workers 4 --threads 2
```

#### Using Heroku

```bash
# Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Login to Heroku
heroku login

# Create Heroku app
heroku create your-app-name

# Set environment variables
heroku config:set NEWSAPI_KEY=your-key
heroku config:set SUPABASE_URL=your-url
# ... set all required variables

# Deploy
git push heroku main

# View logs
heroku logs --tail
```

#### Using Docker

```bash
# Build Docker image
docker build -t news-app .

# Run container
docker run -p 5000:5000 \
  --env-file .env \
  --name news-app \
  news-app

# Check health
curl http://localhost:5000/health

# View logs
docker logs news-app
```

---

## Common Issues & Solutions

### 1. "NEWSAPI_KEY not found"
**Solution:** Add NEWSAPI_KEY to your .env file
```bash
NEWSAPI_KEY=your-actual-key-here
```

### 2. "Kafka connection refused"
**Solution:** Ensure Kafka broker is running on localhost:9092
```bash
# Check running containers
docker ps | grep kafka

# Start Kafka if not running
docker-compose up -d kafka
```

### 3. "Supabase connection error"
**Solution:** Verify SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in .env
```bash
# Test connection
python -c "from supabase import create_client; create_client(url, key)"
```

### 4. "SSL verification error in local development"
**Solution:** SSL verification is disabled by default for local development. For production, enable SSL verification.

### 5. "No module named 'kafka'"
**Solution:** Install Kafka client library
```bash
pip install kafka-python
```

---

## Additional Resources

### Official Documentation
- [Flask Documentation](https://flask.palletsprojects.com/)
- [NewsAPI Docs](https://newsapi.org/docs)
- [Supabase Documentation](https://supabase.com/docs)
- [Apache Kafka Docs](https://kafka.apache.org/documentation/)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers/)

### Related Guides
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)
- [Docker Getting Started](https://docs.docker.com/get-started/)
- [Heroku Python Deployment](https://devcenter.heroku.com/articles/getting-started-with-python)

### Support
- GitHub Issues: [GitHub Issues](https://github.com/AdiToubin/project/issues)
- Email: support@example.com

---

**Last Updated:** October 2024
**Version:** 1.0.0
**Status:** Active Development
**Author:** AdiToubin
