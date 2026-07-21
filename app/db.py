"""
db.py - Database Connection Setup
==================================
This module handles the SQLite database connection using SQLAlchemy.

WHY SQLite?
  - No external server needed; the database is a single file on disk.
  - Perfect for demos, viva presentations, and local development.
  - SQLAlchemy's ORM layer means we never write raw SQL — safer and more readable.

HOW IT WORKS:
  1. We create an "engine" — think of it as the driver that talks to the database file.
  2. We create a "SessionLocal" factory — every API request gets its own short-lived
     database session (like a temporary connection) that is properly closed afterwards.
  3. `Base` is the declarative base class that all ORM models (in models.py) inherit from.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base  # declarative_base moved to orm in SQLAlchemy 2.0

# ─── Database File Location ───────────────────────────────────────────────────
# SQLite stores everything in a single file called "ecoroute.db" in the project root.
# "sqlite:///" is the connection string prefix; three slashes = relative path.
DATABASE_URL = "sqlite:///./ecoroute.db"

# ─── Engine ───────────────────────────────────────────────────────────────────
# check_same_thread=False is required for SQLite when used with FastAPI because
# FastAPI runs requests on multiple threads, and SQLite's default setting would
# raise an error if the same connection is accessed from different threads.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# ─── Session Factory ──────────────────────────────────────────────────────────
# autocommit=False : Changes won't be saved until we explicitly call session.commit()
# autoflush=False  : SQLAlchemy won't auto-send pending changes to the DB mid-request
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ─── Declarative Base ─────────────────────────────────────────────────────────
# All ORM model classes in models.py will inherit from this Base.
# SQLAlchemy uses it to track which Python classes map to which DB tables.
Base = declarative_base()


def get_db():
    """
    FastAPI dependency that provides a database session per request.

    USAGE (in routes.py):
        def my_endpoint(db: Session = Depends(get_db)):
            ...

    This is a Python generator (uses `yield`). FastAPI will:
      1. Call next() to get the `db` session and inject it into the endpoint.
      2. After the endpoint finishes (or throws an error), resume here and
         execute the `finally` block to close the session.

    WHY finally?
      Ensures the session is ALWAYS closed — even if an exception was raised.
      Prevents "connection leaks" that could slow down or crash the server.
    """
    db = SessionLocal()
    try:
        yield db        # Hand the session to the endpoint function
    finally:
        db.close()      # Always clean up, no matter what happened above
