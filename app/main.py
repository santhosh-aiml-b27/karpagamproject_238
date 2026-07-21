"""
main.py - FastAPI Application Entry Point
==========================================
This is the TOP-LEVEL file that wires everything together and starts the server.

RESPONSIBILITIES:
  1. Create the FastAPI app instance with metadata (title, description, version).
  2. Manage application LIFESPAN events:
       - On STARTUP  : Create DB tables, seed initial data, load the road graph.
       - On SHUTDOWN : Log graceful shutdown (future: close external connections).
  3. Include the API router from routes.py.
  4. Provide a root health-check endpoint.

HOW TO RUN:
  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

HOW LIFESPAN WORKS (FastAPI >= 0.93):
  The @asynccontextmanager lifespan function replaces the older @app.on_event
  pattern. Everything BEFORE `yield` runs at startup; everything AFTER runs
  at shutdown. FastAPI handles calling this automatically.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import engine, SessionLocal
from app import models, graph_engine
from app.routes import router
from app.aqi_simulator import SENSITIVE_ZONES

# ─── Logging Configuration ────────────────────────────────────────────────────
# Configure Python's built-in logger to display timestamps and module names.
# This makes it much easier to trace what's happening during startup and requests.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(name)s]  %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("main")


# ─── Lifespan Event Handler ───────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.

    STARTUP SEQUENCE (runs before the server accepts requests):
      1. Create all database tables (if they don't already exist).
      2. Seed the sensitive_zones table with predefined zones.
      3. Initialise the graph engine (downloads/loads the road network,
         generates AQI map, annotates edge weights).

    SHUTDOWN SEQUENCE (runs after the last request):
      - Currently just logs a shutdown message.
      - In production: close DB connections, flush caches, etc.
    """
    # ── STARTUP ───────────────────────────────────────────────────────────────
    logger.info("=" * 60)
    logger.info("  EcoRoute AI Backend - Starting Up")
    logger.info("=" * 60)

    # Step 1: Create all database tables defined in models.py
    logger.info("Creating database tables (if not exist)...")
    models.Base.metadata.create_all(bind=engine)
    logger.info("Database tables ready.")

    # Step 2: Seed sensitive zones into the database
    # We check first to avoid duplicate entries on every restart.
    logger.info("Seeding sensitive zones into database...")
    _seed_sensitive_zones()

    # Step 3: Load the road network graph (this is the slow step)
    logger.info("Initialising graph engine (this may take a minute)...")
    try:
        graph_engine.initialise_engine()
    except Exception as e:
        # If the graph fails to load (e.g., no internet), log the error but
        # keep the server running — other endpoints (zones, sensor-data, history)
        # will still work fine. Only route calculation will be unavailable.
        logger.error(f"Graph engine failed to initialise: {e}")
        logger.warning("Route calculation will be unavailable until graph loads.")

    logger.info("=" * 60)
    logger.info("  EcoRoute AI is ready. Visit http://localhost:8000/docs")
    logger.info("=" * 60)

    # Hand control back to FastAPI — server now accepts requests
    yield

    # ── SHUTDOWN ──────────────────────────────────────────────────────────────
    logger.info("EcoRoute AI Backend shutting down gracefully.")


# ─── FastAPI Application Instance ────────────────────────────────────────────

app = FastAPI(
    title="EcoRoute AI",
    description=(
        "A smart traffic routing system that finds routes balancing "
        "travel time, air quality (AQI), and sensitive zone avoidance "
        "(schools/hospitals). Built with FastAPI, OSMnx, and NetworkX."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",       # Swagger UI at http://localhost:8000/docs
    redoc_url="/redoc",     # ReDoc UI at http://localhost:8000/redoc
)

# ─── CORS Middleware ──────────────────────────────────────────────────────────
# Allows web browser clients (e.g., a React frontend map) to call this API.
# In production, replace allow_origins=["*"] with your specific frontend domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # Allow all origins for dev/demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Include Routes ───────────────────────────────────────────────────────────
# All routes defined in routes.py are mounted here without a prefix,
# so they appear as /get-route, /zones, /aqi/{zone_id}, etc.
app.include_router(router)


# ─── Root Health Check ────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
def root():
    """
    Root endpoint — simple health check.
    Returns a welcome message and confirms the API is running.
    Useful for load balancer health checks and quick testing.
    """
    return {
        "message": "EcoRoute AI Backend is running!",
        "docs":    "http://localhost:8000/docs",
        "status":  "healthy",
        "graph_loaded": graph_engine.GRAPH is not None,
    }


# ─── Database Seeder ─────────────────────────────────────────────────────────

def _seed_sensitive_zones():
    """
    Seeds the sensitive_zones table with predefined Madurai landmarks.

    WHY seed on every startup?
      We check if zones already exist (count > 0) and skip seeding if so.
      This makes the function idempotent — safe to call multiple times.

    The seeded zones are the same as SENSITIVE_ZONES in aqi_simulator.py,
    ensuring the simulator and the database stay in sync.
    """
    db = SessionLocal()
    try:
        existing_count = db.query(models.SensitiveZone).count()
        if existing_count > 0:
            logger.info(f"Zones already seeded ({existing_count} zones in DB). Skipping.")
            return

        for zone_data in SENSITIVE_ZONES:
            zone = models.SensitiveZone(
                id=zone_data["id"],
                name=zone_data["name"],
                lat=zone_data["lat"],
                lng=zone_data["lng"],
                type=zone_data["type"],
            )
            db.add(zone)

        db.commit()
        logger.info(f"Seeded {len(SENSITIVE_ZONES)} sensitive zones into database.")
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to seed zones: {e}")
    finally:
        db.close()
