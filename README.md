# 🤖 Open-Source Social Listening Platform

An open-source **social listening and mention analysis platform** that collects online mentions from multiple public sources and transforms them into structured insights using **relevance filtering, deduplication, sentiment analysis, topic classification, analytics, competitor comparison, alerts, scheduled monitoring, and AI-assisted insights**.

The platform provides a modern **React dashboard** backed by a **FastAPI REST API** and **PostgreSQL database**, with complete **Docker Compose** support.

The application is also deployed using **Vercel** for the frontend and **Render** for the backend and PostgreSQL database.

---

# 📌 Project Overview

The **Open-Source Social Listening Platform** is designed to help users understand what people are saying online about a product, brand, technology, or keyword.

A user enters a keyword such as:

```text
Samsung Galaxy S26
```

The platform collects relevant content from supported public sources such as:

- RSS feeds
- Hacker News
- Stack Exchange

The collected content then passes through a processing pipeline:

```text
Data Collection
      ↓
Normalization
      ↓
Relevance Filtering
      ↓
Deduplication
      ↓
Sentiment Analysis
      ↓
Topic Classification
      ↓
PostgreSQL
      ↓
Analytics / AI Insights / Competitor Analysis / Alerts
      ↓
React Dashboard
```

---

# ✨ Features

- 🔎 Keyword-based social listening
- 📰 Multi-source data collection
- 📡 RSS feed ingestion
- 🟠 Hacker News ingestion
- 💬 Stack Exchange ingestion
- 🎯 Relevance filtering
- ♻️ Mention deduplication
- 😊 Sentiment analysis
- 🏷️ Topic classification
- 📊 Analytics dashboard
- 🤖 AI-assisted insights
- ⚔️ Competitor comparison
- 🔔 Sentiment and activity alerts
- ⏰ Scheduled keyword monitoring
- 📋 Mention explorer
- 📚 Search history
- 🐘 PostgreSQL database
- ⚡ FastAPI REST API
- ⚛️ React + Vite frontend
- 🐳 Docker Compose deployment
- 🧪 Automated backend testing
- ☁️ Cloud deployment with Vercel and Render

---

# ⭐ Key Highlights

- Supports multiple public data sources.
- Normalizes different source formats into a common mention structure.
- Filters irrelevant content before deeper processing.
- Removes duplicate mentions.
- Performs sentiment classification with confidence scores.
- Classifies mentions into meaningful topics with confidence scores.
- Provides source, sentiment, topic, and time-based analytics.
- Provides competitor comparison for multiple keywords.
- Includes scheduled monitoring for recurring searches.
- Generates evidence-based AI-assisted insights.
- Uses deterministic fallback logic when structured local LLM output is unavailable.
- Uses lightweight NLP techniques to reduce memory requirements.
- Provides a complete Dockerized development environment.
- Includes automated backend tests.
- Deployed frontend and backend are available online.
- Current release: **v1.1.0**

---

# 🛠 Technology Stack

## Frontend

- React
- Vite
- JavaScript
- CSS
- Axios
- REST API integration
- ESLint
- Nginx

## Backend

- Python
- FastAPI
- Uvicorn
- SQLAlchemy
- Pydantic
- Alembic

## Database

- PostgreSQL 17

## Data Collection

- RSS
- Hacker News
- Stack Exchange

### Configured RSS Sources

- TechCrunch
- The Verge
- Ars Technica
- Android Authority

## NLP & AI

The current implementation uses lightweight NLP techniques designed to reduce memory usage during deployment.

### Deduplication

- URL normalization
- Content normalization
- Product/model conflict detection
- TF-IDF vectorization
- Cosine similarity

### Sentiment Analysis

- Rule-based sentiment classification
- Positive / Neutral / Negative classification
- Confidence scoring
- Positive and negative signal detection

### Topic Classification

- TF-IDF vectorization
- Topic prototype similarity
- Domain-specific signals
- Confidence thresholding
- Topics such as Pricing, Features, Competitors, Security, Complaints, Quality, Customer Service, and Other

### AI Insights

- Evidence-based statistical analysis
- Local LLM integration
- Structured insight generation
- Deterministic fallback logic when structured LLM output is unavailable

## DevOps & Deployment

- Docker
- Docker Compose
- Nginx
- Vercel
- Render

## Testing

- Pytest

---

# 📂 Project Structure

```text
social-listening-platform/

│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── alerts.py
│   │   │   ├── analytics.py
│   │   │   ├── competitors.py
│   │   │   ├── insights.py
│   │   │   ├── mentions.py
│   │   │   ├── monitorings.py
│   │   │   └── searches.py
│   │   │
│   │   ├── collectors/
│   │   │   ├── base.py
│   │   │   ├── hackernews.py
│   │   │   ├── models.py
│   │   │   ├── rss.py
│   │   │   └── stackexchange.py
│   │   │
│   │   ├── database/
│   │   │   ├── connection.py
│   │   │   └── models.py
│   │   │
│   │   ├── schemas/
│   │   │
│   │   └── services/
│   │       ├── ai_insights_service.py
│   │       ├── alert_service.py
│   │       ├── analytics_service.py
│   │       ├── competitor_service.py
│   │       ├── deduplication_service.py
│   │       ├── ingestion_service.py
│   │       ├── llm_service.py
│   │       ├── mention_service.py
│   │       ├── normalization_service.py
│   │       ├── processing_service.py
│   │       ├── relevance_service.py
│   │       ├── scheduler_service.py
│   │       ├── search_persistence_service.py
│   │       ├── search_recovery_service.py
│   │       ├── search_service.py
│   │       ├── sentiment_service.py
│   │       └── topic_service.py
│   │
│   ├── alembic/
│   ├── evaluation/
│   ├── tests/
│   ├── create_tables.py
│   ├── pytest.ini
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── context/
│   │   ├── pages/
│   │   └── services/
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   ├── vercel.json
│   └── vite.config.js
│
├── docs/
│   └── screenshots/
│       ├── alerts.png
│       ├── competitors.png
│       ├── dashboard.png
│       ├── history.png
│       ├── insights.png
│       ├── landing.png
│       ├── mentions.png
│       └── monitoring.png
│
├── .env.example
├── .gitattributes
├── .gitignore
├── ARCHITECTURE.md
├── docker-compose.yml
└── README.md
```

---

# 🚀 Installation

## Clone Repository

```bash
git clone https://github.com/MdNvD/social-listening-platform.git
```

```bash
cd social-listening-platform
```

---

# 🐳 Run with Docker

Docker Compose is the recommended way to run the complete application locally.

```bash
docker compose up -d --build
```

Check the running containers:

```bash
docker compose ps
```

Stop the application:

```bash
docker compose down
```

## Application URLs

### Frontend

```text
http://localhost:8090
```

### Backend

```text
http://127.0.0.1:8000
```

### FastAPI Swagger Documentation

```text
http://127.0.0.1:8000/docs
```

### PostgreSQL

PostgreSQL is exposed locally through:

```text
5434
```

---

# ☁️ Production Deployment

The application is deployed using:

```text
Frontend
   ↓
Vercel

Backend
   ↓
Render

Database
   ↓
Render PostgreSQL
```

## Production Frontend

https://social-listening-platform-five.vercel.app

## Production Backend

https://social-listening-backend-kqxu.onrender.com

## Production API Documentation

https://social-listening-backend-kqxu.onrender.com/docs

## Production Health Check

https://social-listening-backend-kqxu.onrender.com/api/health

The production deployment was tested with:

- Frontend → Backend API communication
- Keyword search
- Mention collection
- Search history
- Competitor comparison
- Mentions explorer
- AI insights
- Alerts
- Scheduled monitoring
- PostgreSQL persistence

---

# 💻 Manual Installation

## Backend Setup

```powershell
cd backend
```

Create a virtual environment:

```powershell
python -m venv venv
```

Activate it:

```powershell
venv\Scripts\activate
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Configure your environment using:

```text
.env.example
```

Run the backend:

```powershell
uvicorn app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

---

# 💻 Frontend Setup

Open another terminal:

```powershell
cd frontend
```

Install dependencies:

```powershell
npm install
```

Run the development server:

```powershell
npm run dev
```

Frontend:

```text
http://localhost:5173
```

---

# 🔄 Application Workflow

```text
                    User enters keyword
                           │
                           ▼
                     Create Search
                           │
                           ▼
                  Collect Online Mentions
                           │
             ┌─────────────┼─────────────┐
             │             │             │
             ▼             ▼             ▼
           RSS        Hacker News   Stack Exchange
             │             │             │
             └─────────────┼─────────────┘
                           │
                           ▼
                    Normalize Data
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
                      PostgreSQL
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

# 📡 Data Sources

## RSS

The RSS collector retrieves articles from configured feeds.

Current configured sources include:

- TechCrunch
- The Verge
- Ars Technica
- Android Authority

## Hacker News

The Hacker News collector retrieves technology-related discussions and processes them for relevance and analysis.

## Stack Exchange

The Stack Exchange collector retrieves relevant community questions and discussions.

---

# 🎯 Relevance Filtering

The relevance service determines whether collected content is actually related to the searched keyword.

Example:

```text
Keyword:

Samsung Galaxy S26
```

Relevant:

```text
"Samsung Galaxy S26 review and specifications"
```

Not Relevant:

```text
"Samsung washing machine review"
```

Only relevant mentions continue through the deeper processing pipeline.

---

# ♻️ Deduplication

The deduplication service prevents the same mention from being stored multiple times.

Duplicate detection considers:

- URL normalization
- Content normalization
- Product/model context
- TF-IDF similarity
- Existing mentions

Example:

```text
Article A

https://example.com/article


Article B

https://example.com/article

        ↓

Duplicate detected

        ↓

Stored once
```

The current implementation uses **TF-IDF + cosine similarity** rather than a large transformer embedding model. This reduces memory consumption and makes the application more suitable for low-memory deployment environments.

---

# 😊 Sentiment Analysis

Every processed mention can be classified as:

```text
Positive
Neutral
Negative
```

The platform also stores sentiment confidence.

Example:

```text
Sentiment:

Positive

Confidence:

0.91
```

The current sentiment implementation uses a lightweight rule-based approach based on positive and negative linguistic signals.

Sentiment data is used by:

- Analytics
- Alerts
- AI Insights
- Competitor Comparison

---

# 🏷️ Topic Classification

Mentions are classified into topics such as:

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

Example:

```text
"Galaxy S26 is cheaper than expected"

        ↓

Topic: Pricing
```

Topic confidence is also stored for analyzed mentions.

The current implementation uses:

- TF-IDF vectorization
- Topic prototype similarity
- Domain-specific keyword signals
- Confidence thresholds
- Priority rules for strong topic signals

---

# 📊 Analytics

The analytics system provides:

- Total mentions
- Sentiment distribution
- Topic distribution
- Source distribution
- Mentions over time
- First mention timestamp
- Latest mention timestamp

Example development/test result:

```text
Total Mentions: 8

Sentiment:

Positive: 6
Negative: 1
Neutral: 1

Topics:

Competitors: 4
Pricing: 2
Features: 1
Other: 1
```

These values are example development/test results and change as new data is collected.

---

# 🤖 AI Insights

The AI Insights module analyzes processed mention data and generates higher-level observations.

It can provide:

- Overall summary
- Positive observations
- Negative observations
- Pain points
- Opportunities
- Recommended actions
- Supporting evidence

Workflow:

```text
Processed Mentions
        │
        ▼
Evidence Collection
        │
        ▼
Statistical Analysis
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

The system is designed to remain usable even when a local LLM does not return valid structured JSON.

In that situation, deterministic evidence-based fallback logic is used to generate useful insights from the available mention data.

---

# ⚔️ Competitor Comparison

The platform can compare multiple keywords or products.

Example:

```text
Samsung Galaxy S26

        VS

Google Pixel
```

Comparison metrics include:

- Total mentions
- Sentiment
- Topics
- Sources
- Engagement
- Negative mentions

Example comparison data can be generated directly from the platform's collected and processed mentions.

---

# 🔔 Alerts

The alerts module analyzes recent mention activity.

It evaluates:

- Recent mention volume
- Recent negative mentions
- Negative sentiment rate
- Changes compared with a previous period

Example:

```text
Recent Period
      │
      ▼
Negative Mentions
      │
      ▼
Negative Rate
      │
      ▼
Previous Period Comparison
      │
      ▼
Alert Evaluation
```

The system can determine whether sufficient recent and historical data exists before generating an alert.

---

# ⏰ Scheduled Monitoring

Users can create recurring monitoring jobs for keywords.

Example:

```text
Keyword:

Samsung Galaxy S26

Interval:

1440 minutes

        ↓

Scheduled Search

        ↓

Collect Mentions

        ↓

Process Mentions

        ↓

Update Database
```

Monitoring supports:

- Create
- Retrieve
- Update
- Activate / deactivate
- Delete

The scheduler uses APScheduler to execute monitoring jobs.

---

# 🌐 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Check backend health |
| POST | `/api/searches` | Create a keyword search |
| GET | `/api/searches/{search_id}` | Get search information |
| GET | `/api/searches/{search_id}/mentions` | Get collected mentions |
| GET | `/api/searches/{search_id}/analytics` | Get analytics |
| GET | `/api/searches/{search_id}/insights` | Get AI-assisted insights |
| POST | `/api/competitors/compare` | Compare keywords/products |
| GET | `/api/searches/{search_id}/alerts` | Get alerts |
| GET | `/api/monitorings` | List monitoring jobs |
| POST | `/api/monitorings` | Create monitoring |
| GET | `/api/monitorings/{monitoring_id}` | Get monitoring |
| PATCH | `/api/monitorings/{monitoring_id}` | Update monitoring |
| DELETE | `/api/monitorings/{monitoring_id}` | Delete monitoring |

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

Production API documentation:

https://social-listening-backend-kqxu.onrender.com/docs

---

# 🗄️ Database

The application uses PostgreSQL for persistent storage.

Main database tables include:

```text
searches
mentions
mention_analysis
```

### searches

Stores keyword search information and search status.

### mentions

Stores collected and normalized online mentions.

### mention_analysis

Stores processed analysis such as:

- Relevance
- Sentiment
- Sentiment confidence
- Topic
- Topic confidence

Database migrations are managed using Alembic.

Example:

```bash
alembic upgrade head
```

The application also initializes required database tables during Docker backend startup.

---

# 🧪 Testing

The official automated backend tests are located in:

```text
backend/tests/
```

Run:

```powershell
pytest backend/tests -q
```

Current result:

```text
25 passed
```

The test suite covers:

- Deduplication
- Relevance filtering
- Sentiment analysis
- Topic classification

Additional development and evaluation scripts are stored in:

```text
backend/evaluation/
```

These scripts were used during development to evaluate:

- RSS collection
- Relevance
- Deduplication
- Sentiment
- Topic classification
- Hacker News collection
- Stack Exchange collection
- End-to-end processing
- Search services
- NLP behavior

---

# 🐳 Docker Architecture

```text
┌─────────────────────────────────────────────┐
│              Docker Compose                 │
│                                             │
│   ┌─────────────────────────────────────┐   │
│   │ Frontend                            │   │
│   │ React + Vite + Nginx                │   │
│   │ localhost:8090                      │   │
│   └─────────────────┬───────────────────┘   │
│                     │                       │
│                     ▼                       │
│   ┌─────────────────────────────────────┐   │
│   │ Backend                             │   │
│   │ FastAPI + Uvicorn                   │   │
│   │ localhost:8000                      │   │
│   └─────────────────┬───────────────────┘   │
│                     │                       │
│                     ▼                       │
│   ┌─────────────────────────────────────┐   │
│   │ PostgreSQL                          │   │
│   │ PostgreSQL 17                       │   │
│   │ localhost:5434                      │   │
│   └─────────────────────────────────────┘   │
│                                             │
└─────────────────────────────────────────────┘
```

The frontend Docker image uses:

```text
Node.js
   ↓
Vite production build
   ↓
Nginx
```

The backend uses:

```text
Python 3.13
   ↓
FastAPI
   ↓
Uvicorn
```

---

# 🔐 Environment Configuration

Sensitive environment files are not committed to Git.

Use:

```text
.env.example
```

as the configuration template.

Local files such as:

```text
.env
venv/
node_modules/
dist/
__pycache__/
.pytest_cache/
```

are excluded through `.gitignore`.

Production database credentials and other secrets are stored in the deployment platform environment configuration rather than committed to Git.

---

# 📸 Screenshots

## 🏠 Landing Page

![Landing Page](docs/screenshots/landing.png)

---

## 📊 Dashboard

![Dashboard](docs/screenshots/dashboard.png)

---

## 📋 Mentions Explorer

![Mentions Explorer](docs/screenshots/mentions.png)

---

## 🤖 AI Insights

![AI Insights](docs/screenshots/insights.png)

---

## ⚔️ Competitor Comparison

![Competitor Comparison](docs/screenshots/competitors.png)

---

## 🔔 Alerts

![Alerts](docs/screenshots/alerts.png)

---

## ⏰ Scheduled Monitoring

![Scheduled Monitoring](docs/screenshots/monitoring.png)

---

## 📚 Search History

![Search History](docs/screenshots/history.png)

---

# 🎯 Project Status

## Completed

- ✅ RSS data collection
- ✅ Hacker News collection
- ✅ Stack Exchange collection
- ✅ Data normalization
- ✅ Relevance filtering
- ✅ Deduplication
- ✅ Lightweight sentiment analysis
- ✅ Lightweight topic classification
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
- ✅ Nginx frontend serving
- ✅ Backend API validation
- ✅ Automated backend testing
- ✅ GitHub repository
- ✅ Vercel frontend deployment
- ✅ Render backend deployment
- ✅ Render PostgreSQL deployment
- ✅ Production API integration
- ✅ Production feature validation

### Test Status

```text
25 / 25 backend tests passing
```

### Current Release

```text
v1.1.0
```

---

# 🚀 Future Enhancements

- Additional social/community data sources
- Real-time data ingestion
- Advanced trend detection
- Historical sentiment tracking
- More advanced alert rules
- User authentication
- Role-based access control
- Background task queues
- Redis caching
- CI/CD pipeline
- Production monitoring
- Advanced LLM insights
- API rate limiting
- Horizontal scaling
- Improved frontend code splitting and performance optimization

---

# 👨‍💻 Author

**Mohamed Navith**

B.Tech – Computer Science and Engineering

Interested in:

- Full Stack Development
- Python
- Artificial Intelligence
- Machine Learning
- Cloud Computing
- DevOps

---

# 📜 License

This project is developed as an **open-source internship project**.

A separate open-source license can be added to the repository when the licensing terms are finalized.

---

# ⭐ Support

If you find this project useful, consider giving the repository a ⭐ on GitHub.

Repository:

https://github.com/MdNvD/social-listening-platform

---

# 📌 Release

Current stable release:

```text
v1.1.0
```

The `v1.1.0` release includes:

- Lightweight NLP implementation
- TF-IDF-based deduplication
- TF-IDF-based topic classification
- Rule-based sentiment analysis
- Low-memory deployment optimization
- Production frontend API configuration
- Vercel SPA routing
- Render backend deployment
- PostgreSQL production deployment
- Dockerized frontend/backend
- Automated testing
- Production validation
