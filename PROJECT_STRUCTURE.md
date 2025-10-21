# Project Structure - MVC Architecture

## Overview
This project has been reorganized following the MVC (Model-View-Controller) design pattern.

## Directory Structure

```
project/
├── app.py                          # Main Flask application (entry point)
├── models/                         # MODEL layer - Business logic and data
│   ├── __init__.py
│   ├── article_model.py           # Article database operations
│   ├── business_logic.py          # Core business logic
│   └── news_service.py            # News API service
├── views/                         # VIEW layer - Response formatting
│   ├── __init__.py
│   └── json_response.py           # JSON response utilities
├── controllers/                   # CONTROLLER layer - Request handling
│   ├── __init__.py
│   ├── api_controller.py          # General API endpoints
│   └── news_controller.py         # News-related endpoints
├── templates/                     # HTML templates
│   └── index.html
├── static/                        # Static assets (CSS, JS)
│   ├── style.css
│   └── app.js
└── x/                             # Deprecated/unused files
    ├── ingest_articles.py
    ├── run_ingest.py
    ├── test_supabase.py
    ├── model/
    └── services/
```

## MVC Components

### Models (Data Layer)
- **article_model.py**: Handles article data operations with Supabase
  - `ArticleModel.transform_article()` - Transform raw article data
  - `ArticleModel.batch_insert()` - Insert articles into database
  - `ArticleModel.guess_topic()` - Determine article topic

- **business_logic.py**: Core business logic operations
  - `BusinessLogic.process_data()` - Process incoming data
  - `BusinessLogic.calculate()` - Perform calculations

- **news_service.py**: External API integration
  - `NewsFetcher.fetch_top_headlines()` - Fetch news from NewsAPI

### Views (Presentation Layer)
- **json_response.py**: Standardized JSON response formatting
  - `JsonResponse.success()` - Success responses
  - `JsonResponse.error()` - Error responses
  - `JsonResponse.created()` - Resource created responses

### Controllers (Logic Layer)
- **api_controller.py**: General API endpoint handlers
  - `/api/process` - Process data
  - `/api/calculate` - Perform calculations
  - `/health` - Health check

- **news_controller.py**: News-related endpoint handlers
  - `/fetch-news` - Fetch news from API
  - Handles article ingestion and Kafka integration

## Key Features

1. **Clean Separation of Concerns**: Each layer has distinct responsibilities
2. **Modular Design**: Easy to extend and maintain
3. **Reusability**: Models and controllers can be reused across different routes
4. **Testability**: Each component can be tested independently

## Running the Application

```bash
python app.py
```

The application will:
1. Load environment variables
2. Fetch and ingest news articles on startup
3. Start Flask server on port 5000 (or PORT env variable)

## Endpoints

- `GET /` - Main page
- `POST /api/process` - Process data
- `POST /api/calculate` - Perform calculations
- `GET /health` - Health check
- `GET /fetch-news` - Fetch latest news
