from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.searches import router as searches_router
from app.api.analytics import router as analytics_router
from app.api.mentions import router as mentions_router
from app.api.insights import router as insights_router
from app.api.competitors import router as competitors_router
from app.api.alerts import router as alerts_router
from app.api.monitorings import router as monitorings_router

from app.database.connection import engine
from app.services.scheduler_service import scheduler_service
from app.services.search_recovery_service import (
    recover_stale_searches,
)


# =========================================================
# APPLICATION LIFESPAN
# =========================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Start background services when FastAPI starts
    and shut them down cleanly when FastAPI stops.

    Startup flow:

        Start application
            ↓
        Recover stale searches
            ↓
        Start scheduled monitoring
            ↓
        Application ready

    Shutdown flow:

        Stop scheduler
            ↓
        Application shutdown
    """

    print("\n" + "=" * 70)
    print("STARTING APPLICATION")
    print("=" * 70)

    # ---------------------------------------------------------
    # Recover stale searches
    # ---------------------------------------------------------

    recover_stale_searches()

    # ---------------------------------------------------------
    # Start scheduled monitoring service
    # ---------------------------------------------------------

    scheduler_service.start()

    print("Application startup completed.")
    print("=" * 70 + "\n")

    yield

    # =========================================================
    # APPLICATION SHUTDOWN
    # =========================================================

    print("\n" + "=" * 70)
    print("SHUTTING DOWN APPLICATION")
    print("=" * 70)

    # ---------------------------------------------------------
    # Stop scheduled monitoring service
    # ---------------------------------------------------------

    scheduler_service.shutdown()

    print("Application shutdown completed.")
    print("=" * 70 + "\n")


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="Social Listening Platform",
    description="Open-source social listening and analytics platform",
    version="1.0.0",
    lifespan=lifespan,
)


# =========================================================
# CORS
# =========================================================
#
# Frontend may run through:
#   - Vite development server
#   - Docker/Nginx
#
# Current Docker frontend:
#   http://127.0.0.1:8090
#
# Backend:
#   http://127.0.0.1:8000
#
# Therefore 8090 must be explicitly allowed.
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        # Vite development server
        "http://localhost:5173",
        "http://127.0.0.1:5173",

        # Docker/Nginx frontend
        "http://localhost:8080",
        "http://127.0.0.1:8080",

        # Current frontend port
        "http://localhost:8090",
        "http://127.0.0.1:8090",

        # Optional local frontend ports
        "http://localhost:3000",
        "http://127.0.0.1:3000",

        "https://social-listening-platform-five.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# API ROUTERS
# =========================================================

app.include_router(
    searches_router
)

app.include_router(
    analytics_router
)

app.include_router(
    mentions_router
)

app.include_router(
    insights_router
)

app.include_router(
    competitors_router
)

app.include_router(
    alerts_router
)

app.include_router(
    monitorings_router
)


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():
    return {
        "message": "Social Listening Platform API",
        "status": "running",
    }


# =========================================================
# APPLICATION HEALTH
# =========================================================

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy"
    }


# =========================================================
# DATABASE HEALTH
# =========================================================

@app.get("/api/health/database")
def database_health_check():

    with engine.connect() as connection:

        result = connection.execute(
            text("SELECT version();")
        )

        version = result.scalar()

    return {
        "database": "connected",
        "version": version,
    }