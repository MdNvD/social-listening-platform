Open-Source Social Listening Platform
An open-source social listening platform that collects online mentions from multiple public sources and transforms them into actionable insights using relevance filtering, deduplication, sentiment analysis, topic classification, analytics, competitor comparison, alerts, and AI-assisted insights.
---
Overview
Businesses and developers often need to understand what people are saying about a product, brand, or technology across the internet.
This project provides a centralized platform where users can search for a keyword such as:
```text
Samsung Galaxy S26
```
The platform collects relevant mentions from multiple sources, processes the collected content, stores the results in PostgreSQL, and presents the findings through an interactive React dashboard.
Main workflow
```text
                    User Search
                         │
                         ▼
                ┌─────────────────┐
                │  Search Keyword  │
                └────────┬────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │   Data Collection   │
              │                     │
              │ RSS                 │
              │ Hacker News         │
              │ Stack Exchange      │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │ Data Normalization  │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │ Relevance Filtering │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │    Deduplication    │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │   NLP Processing    │
              │                     │
              │ Sentiment           │
              │ Topic Classification│
              └──────────┬──────────┘
                         │
                         ▼
                ┌─────────────────┐
                │   PostgreSQL    │
                └────────┬────────┘
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
      Analytics     AI Insights    Competitors
          │              │              │
          └──────────────┼──────────────┘
                         ▼
                 React Dashboard
```
---
Features
🔎 Social Listening
Search for keywords and collect relevant mentions from multiple public sources.
📰 Multi-Source Data Collection
Currently supports:
RSS feeds
Hacker News
Stack Exchange
Configured RSS sources include:
TechCrunch
The Verge
Ars Technica
Android Authority
🎯 Relevance Filtering
Filters out unrelated content so that only mentions relevant to the searched keyword are processed.
♻️ Deduplication
Prevents duplicate mentions from being stored multiple times.
The system considers factors such as:
URL similarity
Content similarity
Product/model context
😊 Sentiment Analysis
Classifies mentions into:
Positive
Neutral
Negative
The system also stores sentiment confidence scores.
🏷️ Topic Classification
Automatically classifies mentions into topics such as:
Pricing
Features
Competitors
Security
Other
📊 Analytics
Provides:
Total mentions
Sentiment distribution
Topic distribution
Source distribution
Mentions over time
First and latest mention timestamps
🤖 AI-Assisted Insights
Generates evidence-based insights from collected mentions, including:
Summary
Key themes
Pain points
Opportunities
Recommended actions
Supporting evidence
The system also includes deterministic fallback logic when structured AI output is unavailable.
⚔️ Competitor Comparison
Compare multiple keywords/products using:
Mention volume
Sentiment
Topics
Sources
Engagement
Negative mentions
Example:
```text
Samsung Galaxy S26
        VS
Google Pixel
```
🔔 Alerts
Analyzes recent mention activity and detects changes in negative sentiment and mention patterns.
⏰ Scheduled Monitoring
Users can create scheduled keyword monitoring jobs with configurable intervals.
Monitoring supports:
Create
Retrieve
Update
Pause
Delete
🔍 Mention Explorer
Browse collected mentions with their:
Source
Title
URL
Sentiment
Topic
Confidence
Engagement
📚 Search History
Previously performed searches can be retrieved and reviewed.
🐳 Docker Support
The complete application can run using Docker Compose.
---
Technology Stack
Frontend
Technology	Purpose
React	User interface
Vite	Frontend development/build
JavaScript	Application logic
CSS	Styling
ESLint	Code quality
Backend
Technology	Purpose
Python	Backend language
FastAPI	REST API framework
Uvicorn	ASGI server
SQLAlchemy	Database ORM
Pydantic	Data validation
Alembic	Database migrations
Database
Technology	Purpose
PostgreSQL	Persistent data storage
Data Collection
Source	Purpose
RSS	News/article collection
Hacker News	Technology discussions
Stack Exchange	Community questions/discussions
NLP / AI
Sentence Transformers
Hugging Face Transformers
Sentiment classification
Embedding-based topic classification
Local LLM / AI-assisted insight generation
DevOps
Docker
Docker Compose
Nginx
Testing
Pytest
---
System Architecture
```text
┌─────────────────────────────────────────────────────────────┐
│                         React Frontend                       │
│                         Vite + JS                           │
│                                                             │
│ Dashboard | Mentions | Insights | Competitors | Alerts     │
│ Monitoring | Search History                                │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ REST API
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                         FastAPI Backend                      │
│                                                             │
│ API Layer                                                   │
│ ├── Searches                                                │
│ ├── Mentions                                                │
│ ├── Analytics                                               │
│ ├── Insights                                                │
│ ├── Competitors                                             │
│ ├── Monitoring                                              │
│ └── Alerts                                                  │
│                                                             │
│ Service Layer                                               │
│ ├── Ingestion                                               │
│ ├── Relevance                                               │
│ ├── Deduplication                                           │
│ ├── Sentiment                                               │
│ ├── Topic Classification                                    │
│ ├── Analytics                                               │
│ ├── AI Insights                                             │
│ └── Scheduler                                               │
│                                                             │
│ Collector Layer                                             │
│ ├── RSS                                                     │
│ ├── Hacker News                                             │
│ └── Stack Exchange                                          │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
                  ┌────────────────────┐
                  │     PostgreSQL     │
                  │                    │
                  │ searches           │
                  │ mentions           │
                  │ mention_analysis   │
                  └────────────────────┘
```
For a detailed architecture description, see `ARCHITECTURE.md`.
---
Project Structure
```text
social-listening-platform/
│
├── backend/
│   │
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
│   │   │   ├── hackernews.py
│   │   │   ├── rss.py
│   │   │   ├── stackexchange.py
│   │   │   └── models.py
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
│   │       ├── search_service.py
│   │       ├── sentiment_service.py
│   │       └── topic_service.py
│   │
│   ├── alembic/
│   ├── evaluation/
│   ├── tests/
│   │   ├── test_deduplication.py
│   │   ├── test_relevance.py
│   │   ├── test_sentiment.py
│   │   └── test_topic.py
│   │
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
│   ├── package.json
│   ├── Dockerfile
│   └── nginx.conf
│
├── docker-compose.yml
├── .env.example
├── .gitignore
├── ARCHITECTURE.md
└── README.md
```
---
API
The backend exposes REST APIs for the major platform features.
Health
```http
GET /api/health
```
Searches
```http
POST /api/searches
GET /api/searches/{search_id}
```
Mentions
```http
GET /api/searches/{search_id}/mentions
```
Analytics
```http
GET /api/searches/{search_id}/analytics
```
AI Insights
```http
GET /api/searches/{search_id}/insights
```
Competitors
```http
POST /api/competitors/compare
```
Monitoring
```http
GET    /api/monitorings
POST   /api/monitorings
GET    /api/monitorings/{monitoring_id}
PATCH  /api/monitorings/{monitoring_id}
DELETE /api/monitorings/{monitoring_id}
```
Alerts
```http
GET /api/searches/{search_id}/alerts
```
Interactive API documentation is available through FastAPI Swagger UI:
```text
http://127.0.0.1:8000/docs
```
---
Running the Project
Prerequisites
Install:
Python 3.13+
Node.js
npm
PostgreSQL
Docker Desktop (optional, for containerized deployment)
---
Option 1 — Run with Docker
This is the recommended way to run the complete application.
From the project root:
```bash
docker compose up -d --build
```
Check running containers:
```bash
docker compose ps
```
Stop the application:
```bash
docker compose down
```
Application URLs
Frontend:
```text
http://localhost:8090
```
Backend:
```text
http://127.0.0.1:8000
```
Swagger API documentation:
```text
http://127.0.0.1:8000/docs
```
---
Option 2 — Run Manually
Backend
Navigate to the backend:
```powershell
cd backend
```
Create a virtual environment:
```powershell
python -m venv venv
```
Activate it:
```powershell
venv\Scripts\Activate.ps1
```
Install dependencies:
```powershell
pip install -r requirements.txt
```
Configure the environment variables using `.env.example`.
Start FastAPI:
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
Frontend
Open another terminal:
```powershell
cd frontend
```
Install dependencies:
```powershell
npm install
```
Start the development server:
```powershell
npm run dev
```
Frontend:
```text
http://localhost:5173
```
---
Environment Configuration
Environment-specific configuration should be stored in `.env` files.
Do not commit secrets or local environment configuration.
Use:
```text
.env.example
```
as the configuration template.
The repository ignores:
```text
.env
*.env
venv/
.venv/
node_modules/
dist/
__pycache__/
.pytest_cache/
```
---
Database
The application uses PostgreSQL.
The main database entities include:
```text
searches
mentions
mention_analysis
```
Database schema changes are managed using Alembic migrations.
Example:
```bash
alembic upgrade head
```
---
Testing
The official automated backend tests are located in:
```text
backend/tests/
```
Run the complete test suite:
```powershell
cd backend
pytest -v
```
Current test result:
```text
24 passed
```
The tests cover:
Deduplication
Same URL detection
Same content detection
Product/model distinction
Galaxy model extraction
Empty existing mentions
Relevance
Relevant product titles
Google Pixel relevance
Wrong model detection
Incidental mentions
Empty keyword/content handling
Sentiment
Positive classification
Negative classification
Neutral classification
Signal-based correction
Confidence-based predictions
Topic Classification
Security
Pricing
Competitor comparison
Complaints
General/Other classification
Additional development and evaluation scripts are stored in:
```text
backend/evaluation/
```
---
Example Search
Example keyword:
```text
Samsung Galaxy S26
```
Example data sources:
```text
RSS
Hacker News
Stack Exchange
```
Example development/test analysis:
```text
Total mentions: 8

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
These values are example development/test results and can change as new data is collected.
---
Security Considerations
The project follows basic security practices:
Environment variables are excluded from Git
Secrets are not stored in source code
`.env.example` is provided as a configuration template
Database credentials are configured through environment variables
Docker services are isolated through Docker Compose networking
Before production deployment, additional production security measures should be applied, including:
HTTPS
Secure secret management
Authentication/authorization
API rate limiting
Database access restrictions
Production CORS configuration
Container hardening
---
Current Project Status
Completed
[x] Multi-source data collection
[x] RSS ingestion
[x] Hacker News ingestion
[x] Stack Exchange ingestion
[x] Data normalization
[x] Relevance filtering
[x] Deduplication
[x] Sentiment analysis
[x] Topic classification
[x] PostgreSQL persistence
[x] Analytics
[x] AI-assisted insights
[x] Competitor comparison
[x] Alerts
[x] Scheduled monitoring
[x] Search history
[x] React dashboard
[x] Docker Compose deployment
[x] Backend API validation
[x] Automated testing
Test Status
```text
Backend tests: 24 / 24 passing
```
The complete Dockerized application has also been manually validated.
---
Future Improvements
Potential future enhancements include:
Additional social media and community sources
More advanced trend detection
Historical sentiment tracking
Real-time streaming ingestion
Advanced alert rules
User authentication and role management
Background task queues
Production monitoring and observability
Improved LLM-based insight generation
Cloud deployment
API rate limiting and caching
---
Screenshots
Add screenshots of the main application pages here.
Recommended screenshots:
Dashboard
Mentions Explorer
Analytics
AI Insights
Competitor Comparison
Alerts
Scheduled Monitoring
Example:
```markdown
## Dashboard

![Dashboard](docs/screenshots/dashboard.png)
```
---
Author
Mohamed Navith
B.Tech Computer Science and Engineering
Interested in:
Full Stack Development
Python
AI/ML
Cloud Computing
DevOps
---
License
This project is developed as an open-source internship project.