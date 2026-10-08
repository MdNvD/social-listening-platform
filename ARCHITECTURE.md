System Architecture
1. Overview
The Open-Source Social Listening Platform is a full-stack application designed to collect, process, analyze, and visualize online mentions related to a user-defined keyword.
The platform follows a layered architecture consisting of:
React frontend
FastAPI backend
Data collection layer
Processing and NLP services
PostgreSQL database
Scheduled monitoring
Analytics and AI insight services
Docker-based deployment
---
2. High-Level Architecture
```text
                         USER
                           │
                           ▼
                ┌─────────────────────┐
                │   React Frontend    │
                │     + Vite          │
                └──────────┬──────────┘
                           │
                           │ REST API
                           ▼
                ┌─────────────────────┐
                │   FastAPI Backend   │
                └──────────┬──────────┘
                           │
          ┌────────────────┼─────────────────┐
          │                │                 │
          ▼                ▼                 ▼
   Search APIs       Monitoring APIs    Analytics APIs
          │                │                 │
          └────────────────┼─────────────────┘
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
                │ NLP Processing      │
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
            ┌──────────────┼───────────────┐
            │              │               │
            ▼              ▼               ▼
       Analytics      AI Insights     Competitors
            │              │               │
            └──────────────┼───────────────┘
                           │
                           ▼
                   React Dashboard
```
---
3. Frontend Architecture
The frontend is built using React and Vite.
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
└── vite.config.js
```
Frontend Responsibilities
The frontend is responsible for:
Accepting search keywords
Displaying search results
Displaying mentions
Showing sentiment information
Showing topic classification
Displaying analytics
Displaying AI insights
Comparing competitors
Displaying alerts
Managing scheduled monitoring
Displaying search history
The frontend communicates with the backend through REST APIs.
The API base URL is configured using:
```text
VITE_API_BASE_URL
```
---
4. Backend Architecture
The backend is built using FastAPI.
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
│   │   ├── rss.py
│   │   ├── stackexchange.py
│   │   └── models.py
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
5. API Layer
The API layer exposes REST endpoints to the frontend.
Main API modules:
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
Responsibilities include:
Request validation
Calling backend services
Returning structured API responses
Handling HTTP errors
Connecting frontend operations with business logic
---
6. Data Collection Layer
The collector layer retrieves data from external public sources.
```text
collectors/
├── rss.py
├── hackernews.py
├── stackexchange.py
└── base.py
```
RSS Collector
The RSS collector retrieves articles from configured RSS feeds.
Configured sources include:
TechCrunch
The Verge
Ars Technica
Android Authority
The collected information can include:
Source
URL
Title
Content
Author
Published date
Keyword
Engagement
Hacker News Collector
Collects technology-related discussions from Hacker News.
The collector extracts information such as:
Title
URL
Content
Author
Timestamp
Engagement
Stack Exchange Collector
Collects relevant questions and discussions from Stack Exchange.
The system uses the collected content for:
Relevance analysis
Sentiment analysis
Topic classification
Analytics
---
7. Data Processing Pipeline
After data collection, mentions pass through several processing stages.
```text
Raw Data
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
8. Normalization
The normalization service standardizes collected data from different sources.
Different sources may provide different field names and formats.
The normalization layer converts them into a common mention structure.
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
This allows the rest of the system to process mentions consistently regardless of their source.
---
9. Relevance Filtering
Not every collected item is relevant to the user's search.
The relevance service determines whether a collected item is related to the searched keyword.
Example:
```text
Keyword:
Samsung Galaxy S26

Relevant:
"Samsung Galaxy S26 review and specifications"

Not relevant:
"Samsung washing machine review"
```
Only relevant mentions continue through the processing pipeline.
---
10. Deduplication
The deduplication service prevents duplicate mentions from being stored.
Duplicate detection can use:
URL comparison
Content similarity
Product/model context
Existing database records
Example:
```text
Article A
https://example.com/article

Article B
https://example.com/article

        ↓

Duplicate detected

        ↓

Store once
```
---
11. Sentiment Analysis
The sentiment service determines the overall sentiment of each mention.
Possible classifications:
```text
Positive
Neutral
Negative
```
The system also stores a confidence score.
Example:
```text
Sentiment:
Positive

Confidence:
0.91
```
The sentiment results are later used by:
Analytics
Alerts
AI Insights
Competitor comparison
---
12. Topic Classification
The topic service classifies mentions into predefined categories.
Example topics include:
```text
Pricing
Features
Competitors
Security
Other
```
Example:
```text
"Galaxy S26 is cheaper than expected"

        ↓

Topic: Pricing
```
The system also stores topic confidence.
---
13. Database Architecture
PostgreSQL is used as the primary persistent database.
Main tables include:
```text
searches
    │
    ├── Search information
    ├── Keyword
    ├── Status
    └── Timestamps


mentions
    │
    ├── Source
    ├── URL
    ├── Title
    ├── Content
    ├── Author
    ├── Published date
    ├── Keyword
    └── Engagement


mention_analysis
    │
    ├── Sentiment
    ├── Sentiment confidence
    ├── Topic
    └── Topic confidence
```
Relationships allow mentions and their analysis to be associated with searches.
---
14. Analytics Architecture
The analytics service aggregates processed mentions.
It calculates:
```text
Total mentions
        │
        ├── Sentiment distribution
        │
        ├── Topic distribution
        │
        ├── Source distribution
        │
        ├── Mentions over time
        │
        ├── First mention
        │
        └── Latest mention
```
The frontend converts these results into dashboard visualizations.
---
15. AI Insights Architecture
The AI insights service creates higher-level observations from processed data.
The process is:
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
AI / LLM Processing
        │
        ▼
Structured Insights
        │
        ▼
Frontend
```
Generated insights can include:
Overall summary
Positive observations
Negative observations
Pain points
Opportunities
Recommended actions
If the local LLM does not provide usable structured output, the system can use deterministic evidence-based fallback logic.
---
16. Competitor Comparison
The competitor service allows multiple keywords to be compared.
Example:
```text
Samsung Galaxy S26
        VS
Google Pixel
```
Comparison metrics include:
Total mentions
Sentiment distribution
Topic distribution
Source distribution
Engagement
Negative mentions
The backend collects or retrieves the corresponding search data and returns a comparison response to the frontend.
---
17. Alerts
The alert service analyzes recent mention activity.
The system compares recent data with an earlier period.
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
Compare With Previous Period
      │
      ▼
Alert Evaluation
```
The system can identify changes in negative sentiment and mention activity.
---
18. Scheduled Monitoring
The monitoring service allows users to configure recurring keyword searches.
Example:
```text
Keyword:
Samsung Galaxy S26

Interval:
1440 minutes

        ↓

Run search periodically
        ↓
Collect new mentions
        ↓
Process mentions
        ↓
Update database
```
Monitoring records contain information such as:
Keyword
Interval
Active status
Last run
Next run
---
19. Search Lifecycle
A typical search follows this lifecycle:
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
Filter Relevant Mentions
        │
        ▼
Remove Duplicates
        │
        ▼
Analyze Sentiment
        │
        ▼
Classify Topics
        │
        ▼
Persist Results
        │
        ▼
Calculate Analytics
        │
        ▼
Generate Insights
        │
        ▼
Display Results
```
---
20. Docker Architecture
The application can run using Docker Compose.
```text
┌─────────────────────────────────────┐
│           Docker Compose            │
│                                     │
│  ┌──────────────┐                   │
│  │   Frontend   │                   │
│  │ React + Nginx│                   │
│  │    :8090     │                   │
│  └───────┬──────┘                   │
│          │                          │
│          ▼                          │
│  ┌──────────────┐                   │
│  │   Backend    │                   │
│  │   FastAPI    │                   │
│  │    :8000     │                   │
│  └───────┬──────┘                   │
│          │                          │
│          ▼                          │
│  ┌──────────────┐                   │
│  │  PostgreSQL  │                   │
│  │    :5434     │                   │
│  └──────────────┘                   │
│                                     │
└─────────────────────────────────────┘
```
The PostgreSQL container is internally connected to the backend through the Docker network.
---
21. API Communication
The frontend communicates with FastAPI through HTTP requests.
Example:
```text
React
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
The frontend API base URL is configured using:
```text
VITE_API_BASE_URL
```
---
22. Error Handling
The backend uses FastAPI HTTP responses and validation to handle invalid requests.
Examples include:
Invalid search IDs
Invalid monitoring configuration
Missing resources
Invalid request bodies
Database errors
The frontend displays appropriate error states when API requests fail.
---
23. Testing Architecture
Automated backend tests are located in:
```text
backend/tests/
```
Current official test modules:
```text
test_deduplication.py
test_relevance.py
test_sentiment.py
test_topic.py
```
Additional development and evaluation scripts are stored separately:
```text
backend/evaluation/
```
This separation keeps the official automated test suite independent from experimental and evaluation scripts.
Current automated test result:
```text
24 passed
```
---
24. Development Evaluation
The project also contains evaluation scripts for testing specific components and real-source behavior.
Examples include:
RSS collection
Hacker News collection
Stack Exchange collection
Relevance evaluation
Sentiment evaluation
Topic evaluation
Deduplication evaluation
End-to-end pipeline evaluation
These scripts are stored under:
```text
backend/evaluation/
```
---
25. Deployment Flow
The intended deployment flow is:
```text
Developer
    │
    ▼
Git Repository
    │
    ▼
Docker Build
    │
    ├── Frontend Image
    │
    ├── Backend Image
    │
    └── PostgreSQL Container
    │
    ▼
Docker Compose
    │
    ▼
Running Application
```
---
26. Security and Configuration
Environment variables are used for configuration.
Sensitive values should never be committed to Git.
The repository uses:
```text
.env
```
for local configuration and:
```text
.env.example
```
as a safe configuration template.
The `.gitignore` file prevents local environment files, virtual environments, dependencies, caches, and build artifacts from being committed.
---
27. Current Architecture Status
The current implementation includes:
Multi-source ingestion
RSS collection
Hacker News collection
Stack Exchange collection
Normalization
Relevance filtering
Deduplication
Sentiment analysis
Topic classification
PostgreSQL persistence
Analytics
AI-assisted insights
Competitor comparison
Alerts
Scheduled monitoring
Search history
React dashboard
Docker Compose
Automated backend tests
The complete Dockerized application has been manually validated.
Current automated backend test status:
```text
24 / 24 tests passing
```
---
28. Future Architecture Improvements
Possible future improvements include:
Background job queues
Redis caching
Real-time ingestion
Additional social platforms
Advanced trend detection
User authentication
Role-based access control
API rate limiting
Distributed processing
Cloud deployment
Centralized logging
Application monitoring
CI/CD pipelines
Horizontal scaling