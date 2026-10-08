# 🏗️ System Architecture

# 📌 Project Overview

The **Open-Source Social Listening Platform** is a full-stack application that collects online mentions for user-defined keywords, processes the collected content using lightweight NLP techniques, stores structured results in PostgreSQL, and presents analytics and insights through a React dashboard.

The system is designed using a modular architecture so that data collectors, processing services, analytics, AI insights, alerts, and scheduled monitoring can evolve independently.

The current **v1.1.0** architecture uses lightweight NLP components to reduce memory requirements and support low-memory cloud deployment.

---

# 🧩 High-Level Architecture

```text
                         👤 USER
                           │
                           ▼
                ┌─────────────────────┐
                │   React Frontend    │
                │       + Vite        │
                └──────────┬──────────┘
                           │
                           │ REST API
                           ▼
                ┌─────────────────────┐
                │   FastAPI Backend   │
                │      + Uvicorn      │
                └──────────┬──────────┘
                           │
             ┌─────────────┼─────────────┐
             │             │             │
             ▼             ▼             ▼
        Search APIs   Monitoring APIs  Analytics APIs
             │             │             │
             └─────────────┼─────────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │  Ingestion Service  │
                └──────────┬──────────┘
                           │
             ┌─────────────┼─────────────┐
             │             │             │
             ▼             ▼             ▼
           RSS        Hacker News   Stack Exchange
             │             │             │
             └─────────────┼─────────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │ Normalization       │
                │ Service             │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │ Relevance Filtering │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │ Deduplication       │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │ Lightweight NLP     │
                │                     │
                │ Sentiment           │
                │ Topic Classification│
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │     PostgreSQL      │
                └──────────┬──────────┘
                           │
             ┌─────────────┼─────────────┐
             │             │             │
             ▼             ▼             ▼
         Analytics     AI Insights   Competitors
             │             │             │
             └─────────────┼─────────────┘
                           │
                           ▼
                    React Dashboard
```

---

# 🖥️ Frontend Architecture

The frontend is built using **React + Vite** and is served through Nginx in the Docker production image.

```text
frontend/

│
├── public/
│
├── src/
│   ├── components/
│   │   └── layout/
│   │       ├── Layout.jsx
│   │       └── Sidebar.jsx
│   │
│   ├── context/
│   │   ├── SearchContext.jsx
│   │   ├── SearchContextValue.js
│   │   └── useSearch.js
│   │
│   ├── pages/
│   │   ├── Dashboard.jsx
│   │   ├── Mentions.jsx
│   │   ├── Insights.jsx
│   │   ├── Competitors.jsx
│   │   ├── Alerts.jsx
│   │   ├── Monitoring.jsx
│   │   └── SearchHistory.jsx
│   │
│   ├── services/
│   │   └── api.js
│   │
│   ├── App.jsx
│   ├── App.css
│   ├── index.css
│   └── main.jsx
│
├── Dockerfile
├── nginx.conf
├── package.json
├── vercel.json
└── vite.config.js
```

## Frontend Responsibilities

The frontend handles:

- Search input
- Search history
- Dashboard
- Mention browsing
- Sentiment visualization
- Topic visualization
- Analytics
- AI insights
- Competitor comparison
- Alerts
- Scheduled monitoring
- Navigation and application state

The frontend communicates with the backend using REST APIs.

The backend URL is configured using:

```text
VITE_API_BASE_URL
```

For Vercel deployment, the production value points to the deployed Render backend.

---

# ⚙️ Backend Architecture

The backend is implemented using **Python, FastAPI, and Uvicorn**.

```text
backend/

│
├── app/
│   │
│   ├── api/
│   │   ├── alerts.py
│   │   ├── analytics.py
│   │   ├── competitors.py
│   │   ├── insights.py
│   │   ├── mentions.py
│   │   ├── monitorings.py
│   │   └── searches.py
│   │
│   ├── collectors/
│   │   ├── base.py
│   │   ├── hackernews.py
│   │   ├── models.py
│   │   ├── rss.py
│   │   └── stackexchange.py
│   │
│   ├── database/
│   │   ├── connection.py
│   │   └── models.py
│   │
│   ├── schemas/
│   │
│   └── services/
│       ├── ai_insights_service.py
│       ├── alert_service.py
│       ├── analytics_service.py
│       ├── competitor_service.py
│       ├── deduplication_service.py
│       ├── ingestion_service.py
│       ├── llm_service.py
│       ├── mention_service.py
│       ├── normalization_service.py
│       ├── processing_service.py
│       ├── relevance_service.py
│       ├── scheduler_service.py
│       ├── search_persistence_service.py
│       ├── search_recovery_service.py
│       ├── search_service.py
│       ├── sentiment_service.py
│       └── topic_service.py
│
├── alembic/
├── evaluation/
├── tests/
├── create_tables.py
├── pytest.ini
├── requirements.txt
└── Dockerfile
```

---

# 🔌 API Layer

The API layer provides REST endpoints for the frontend.

```text
api/

├── searches.py
├── mentions.py
├── analytics.py
├── insights.py
├── competitors.py
├── monitorings.py
└── alerts.py
```

## Responsibilities

- Receive frontend requests
- Validate request data
- Call appropriate services
- Return structured responses
- Handle HTTP errors
- Connect frontend operations to business logic

---

# 📡 Data Collection Architecture

The collector layer retrieves data from supported public sources.

```text
                    Search Keyword
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
        RSS          Hacker News    Stack Exchange
          │               │               │
          └───────────────┼───────────────┘
                          │
                          ▼
                  Collected Mentions
```

## RSS Collector

The RSS collector retrieves articles from configured feeds.

Configured sources include:

- TechCrunch
- The Verge
- Ars Technica
- Android Authority

## Hacker News Collector

Retrieves technology-related discussions and posts from Hacker News.

## Stack Exchange Collector

Retrieves relevant questions and community discussions from Stack Exchange.

---

# 🔄 Data Processing Architecture

Every collected mention passes through the processing pipeline.

```text
                 Raw Collected Data
                         │
                         ▼
                    Normalization
                         │
                         ▼
                Relevance Filtering
                         │
                         ▼
                   Deduplication
                         │
                         ▼
                 Sentiment Analysis
                         │
                         ▼
                 Topic Classification
                         │
                         ▼
                Database Persistence
```

---

# 1️⃣ Normalization Layer

Different sources provide different data formats.

The normalization service converts source-specific records into a common internal representation.

Example:

```text
source
source_id
url
title
content
author
published_at
keyword
engagement
```

This allows the processing layer to work consistently across all collectors.

---

# 2️⃣ Relevance Layer

The relevance service determines whether a collected item is related to the user's keyword.

Example:

```text
Keyword:

Samsung Galaxy S26

Relevant:

"Samsung Galaxy S26 review and specifications"

Not Relevant:

"Samsung washing machine review"
```

Only relevant content proceeds to further processing.

---

# 3️⃣ Deduplication Layer

The deduplication service prevents duplicate mentions.

It considers:

- URL normalization
- Content normalization
- Product/model context
- TF-IDF similarity
- Existing mentions

The current implementation uses **TF-IDF vectorization and cosine similarity** rather than a transformer embedding model. This reduces memory usage while providing lightweight content-similarity detection.

```text
Article A
      │
      ├──── Same URL ────┐
      │                  │
Article B                ▼
                   Duplicate
                       │
                       ▼
                   Store Once
```

---

# 4️⃣ Sentiment Analysis Layer

The sentiment service classifies processed mentions into:

```text
Positive
Neutral
Negative
```

The service also produces confidence information.

The current implementation uses a lightweight **rule-based sentiment approach** based on positive and negative linguistic signals.

The results are used by:

- Analytics
- Alerts
- Competitor comparison
- AI insights

---

# 5️⃣ Topic Classification Layer

The topic service classifies mentions into categories such as:

```text
Product
Pricing
Customer Service
Quality
Competitors
Complaints
Features
Security
Other
```

Topic confidence is stored with the analysis result.

The current implementation uses:

- TF-IDF vectorization
- Topic prototype similarity
- Domain-specific signals
- Confidence thresholds
- Priority rules for strong topic signals

---

# 🗄️ Database Architecture

The platform uses **PostgreSQL** for persistent storage.

Main entities:

```text
┌──────────────────┐
│     searches     │
├──────────────────┤
│ id               │
│ keyword          │
│ status           │
│ created_at       │
└────────┬─────────┘
         │
         │
         ▼
┌──────────────────┐
│     mentions     │
├──────────────────┤
│ id               │
│ search_id        │
│ source           │
│ source_id        │
│ url              │
│ title            │
│ content          │
│ author           │
│ published_at     │
│ keyword          │
│ engagement       │
└────────┬─────────┘
         │
         ▼
┌──────────────────────┐
│  mention_analysis    │
├──────────────────────┤
│ sentiment            │
│ sentiment_confidence │
│ topic                │
│ topic_confidence     │
└──────────────────────┘
```

Database migrations are managed using **Alembic**.

The Docker backend also initializes the required tables during startup.

---

# 📊 Analytics Architecture

The analytics service aggregates processed mention data.

```text
Processed Mentions
        │
        ▼
┌───────────────────────┐
│ Analytics Service     │
└───────────┬───────────┘
            │
     ┌──────┼──────────────┐
     │      │              │
     ▼      ▼              ▼
 Sentiment Topics        Sources
     │      │              │
     └──────┼──────────────┘
            │
            ▼
      Mentions Over Time
            │
            ▼
       Dashboard Data
```

Analytics include:

- Total mentions
- Sentiment distribution
- Topic distribution
- Source distribution
- Mentions over time
- First mention
- Latest mention

---

# 🤖 AI Insights Architecture

The AI Insights service creates higher-level observations from processed mention data.

```text
Processed Mentions
        │
        ▼
Evidence Collection
        │
        ▼
Statistical Summary
        │
        ▼
AI / Local LLM
        │
        ▼
Structured Insights
        │
        ▼
React Dashboard
```

Generated information can include:

- Overall summary
- Positive observations
- Negative observations
- Pain points
- Opportunities
- Recommended actions
- Evidence

If structured LLM output is unavailable or unusable, deterministic evidence-based fallback logic can be used.

---

# ⚔️ Competitor Comparison Architecture

The competitor service allows multiple keywords to be compared.

```text
Keyword A

   │
   ▼
Search Data
   │
   ├─────────────┐
   │             │
   ▼             ▼
Sentiment      Topics
   │             │
   └──────┬──────┘
          │
          ▼
    Comparison Data
          ▲
          │
   ┌──────┴──────┐
   │             │
Keyword B     Search Data
```

Comparison metrics include:

- Mention volume
- Sentiment
- Topics
- Sources
- Engagement
- Negative mentions

---

# 🔔 Alert Architecture

The alert service evaluates recent activity.

```text
Recent Mentions
       │
       ▼
Recent Negative Rate
       │
       ▼
Previous Period
       │
       ▼
Compare Metrics
       │
       ▼
Alert Evaluation
       │
       ▼
Frontend Alerts
```

The system can evaluate changes in:

- Mention volume
- Negative mention count
- Negative sentiment rate
- Recent vs previous periods

The alert logic also considers whether sufficient recent and historical data exists before generating an alert.

---

# ⏰ Scheduled Monitoring Architecture

The scheduler allows recurring searches.

```text
Monitoring Configuration
          │
          ▼
      Scheduler
          │
          ▼
   Scheduled Search
          │
          ▼
    Data Collection
          │
          ▼
       Processing
          │
          ▼
       PostgreSQL
```

Monitoring records can contain:

- Keyword
- Interval
- Active status
- Last run
- Next run

Supported operations:

- Create
- Retrieve
- Update
- Activate / deactivate
- Delete

The scheduler uses **APScheduler** to execute monitoring jobs.

---

# 🔎 Search Lifecycle

A complete search follows this sequence:

```text
User enters keyword
        │
        ▼
POST /api/searches
        │
        ▼
Create Search
        │
        ▼
Collect Sources
        │
        ├── RSS
        ├── Hacker News
        └── Stack Exchange
        │
        ▼
Normalize
        │
        ▼
Filter Relevant Content
        │
        ▼
Deduplicate
        │
        ▼
Sentiment Analysis
        │
        ▼
Topic Classification
        │
        ▼
Persist Results
        │
        ▼
Analytics
        │
        ▼
AI Insights
        │
        ▼
Frontend Dashboard
```

---

# 🌐 API Communication

The frontend communicates with the backend through REST APIs.

Example:

```text
React Dashboard

       │
       │ GET /api/searches/21/analytics
       ▼

FastAPI

       │
       ▼

Analytics Service

       │
       ▼

PostgreSQL

       │
       ▼

Analytics Response

       │
       ▼

React Dashboard
```

---

# 🐳 Docker Architecture

The complete application can be run with Docker Compose.

```text
┌─────────────────────────────────────────────┐
│              Docker Compose                 │
│                                             │
│  ┌─────────────────────────────────────┐    │
│  │ Frontend                            │    │
│  │ React + Vite + Nginx                │    │
│  │ Port: 8090                          │    │
│  └─────────────────┬───────────────────┘    │
│                    │                        │
│                    ▼                        │
│  ┌─────────────────────────────────────┐    │
│  │ Backend                             │    │
│  │ FastAPI + Uvicorn                   │    │
│  │ Port: 8000                          │    │
│  └─────────────────┬───────────────────┘    │
│                    │                        │
│                    ▼                        │
│  ┌─────────────────────────────────────┐    │
│  │ PostgreSQL                          │    │
│  │ PostgreSQL 17                       │    │
│  │ Port: 5434                          │    │
│  └─────────────────────────────────────┘    │
│                                             │
└─────────────────────────────────────────────┘
```

The Docker backend startup sequence initializes the database tables before starting Uvicorn.

The frontend Docker image builds the Vite application and serves the production assets through Nginx.

---

# ☁️ Production Deployment Architecture

The current production deployment uses Vercel for the frontend and Render for the backend and PostgreSQL database.

```text
                         GitHub
                           │
             ┌─────────────┴─────────────┐
             │                           │
             ▼                           ▼
          Vercel                      Render
             │                           │
             ▼                           ├──────────────┐
       React Frontend                    │              │
                                         ▼              ▼
                                  FastAPI Backend   PostgreSQL
                                         │
                                         │
                                         ▼
                                  Public Data Sources
```

Production frontend:

```text
https://social-listening-platform-five.vercel.app
```

Production backend:

```text
https://social-listening-backend-kqxu.onrender.com
```

Production API documentation:

```text
https://social-listening-backend-kqxu.onrender.com/docs
```

Production health endpoint:

```text
https://social-listening-backend-kqxu.onrender.com/api/health
```

The production deployment has been validated for:

- Frontend-to-backend API communication
- Keyword searches
- Mention collection
- Search history
- Competitor comparison
- Mentions explorer
- AI insights
- Alerts
- Scheduled monitoring
- PostgreSQL persistence

---

# 🧪 Testing Architecture

Official automated tests are located in:

```text
backend/tests/
```

Current test modules:

```text
test_deduplication.py
test_relevance.py
test_sentiment.py
test_topic.py
```

The final test suite currently reports:

```text
25 passed
```

The test suite covers:

- Deduplication
- Relevance filtering
- Sentiment analysis
- Topic classification

Additional development and evaluation scripts are located in:

```text
backend/evaluation/
```

These include tests and evaluation scripts for:

- RSS
- Hacker News
- Stack Exchange
- Relevance
- Sentiment
- Topic classification
- Deduplication
- Normalization
- End-to-end processing
- Search services

---

# 🔐 Security and Configuration

Environment-specific configuration is stored locally or in deployment platform environment settings.

The repository contains:

```text
.env.example
```

while actual `.env` files are excluded from Git.

Ignored local resources include:

```text
.env
venv/
node_modules/
dist/
__pycache__/
.pytest_cache/
```

Production configuration uses deployment-platform environment variables for database credentials and other sensitive values.

Recommended production security improvements include:

- HTTPS
- Secure secret management
- Authentication
- Authorization
- Rate limiting
- Restricted database access
- Production CORS configuration
- Container hardening

---

# 🚀 Deployment Architecture

The development and deployment flow is:

```text
Developer
    │
    ▼
GitHub Repository
    │
    ├───────────────────────┐
    │                       │
    ▼                       ▼
Local Docker           Cloud Deployment
    │                       │
    ├── Frontend            ├── Vercel
    ├── Backend             ├── Render Backend
    └── PostgreSQL          └── Render PostgreSQL
    │                       │
    └───────────┬───────────┘
                ▼
          Running Application
```

---

# 📈 Current System Status

The architecture currently supports:

- ✅ Multi-source ingestion
- ✅ RSS
- ✅ Hacker News
- ✅ Stack Exchange
- ✅ Normalization
- ✅ Relevance filtering
- ✅ TF-IDF-based deduplication
- ✅ Lightweight rule-based sentiment analysis
- ✅ TF-IDF-based topic classification
- ✅ PostgreSQL persistence
- ✅ Analytics
- ✅ AI-assisted insights
- ✅ Competitor comparison
- ✅ Alerts
- ✅ Scheduled monitoring
- ✅ Search history
- ✅ React dashboard
- ✅ FastAPI REST API
- ✅ Docker Compose
- ✅ Vercel deployment
- ✅ Render deployment
- ✅ Production PostgreSQL
- ✅ Automated testing

Current backend test status:

```text
25 / 25 tests passing
```

Current release:

```text
v1.1.0
```

---

# 🔮 Future Architecture Improvements

Possible improvements include:

- Real-time ingestion
- More social/community sources
- Background task queues
- Redis caching
- Advanced trend detection
- Historical sentiment tracking
- User authentication
- Role-based access control
- API rate limiting
- Distributed processing
- Centralized logging
- Application monitoring
- CI/CD pipelines
- Horizontal scaling
- More advanced LLM insight generation
- Improved frontend code splitting and performance optimization
