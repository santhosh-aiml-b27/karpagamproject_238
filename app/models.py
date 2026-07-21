"""
models.py - SQLAlchemy ORM Database Models
==========================================
This module defines the three database tables for EcoRoute AI using
SQLAlchemy's ORM (Object-Relational Mapper).

WHY use an ORM instead of raw SQL?
  - We write Python classes → SQLAlchemy automatically creates CREATE TABLE statements.
  - Reading/writing records becomes Python object manipulation, not SQL string building.
  - Prevents SQL injection attacks by design.

TABLES:
  1. SensitiveZone  — Schools, hospitals, and other areas to avoid for health reasons.
  2. AQIReading     — Simulated sensor readings (AQI values) stored over time.
  3. RouteLog       — History of every route that was calculated via the API.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db import Base   # Import the declarative base from db.py


class SensitiveZone(Base):
    """
    Represents a location that should be avoided or penalised during routing.

    Examples: schools, hospitals, playgrounds.
    These zones influence the cost function — roads near them get a higher penalty
    so the routing algorithm tries to route around them.

    Columns:
        id    : Auto-incremented primary key.
        name  : Human-readable name (e.g., "Madurai Government Hospital").
        lat   : Latitude coordinate of the zone centre.
        lng   : Longitude coordinate of the zone centre.
        type  : Category — "school", "hospital", etc.
    """
    __tablename__ = "sensitive_zones"

    id   = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    lat  = Column(Float,  nullable=False)
    lng  = Column(Float,  nullable=False)
    type = Column(String, nullable=False)   # e.g. "school" | "hospital"

    # One zone can have MANY AQI readings over time (one-to-many relationship)
    aqi_readings = relationship("AQIReading", back_populates="zone")


class AQIReading(Base):
    """
    Stores a single Air Quality Index (AQI) measurement for a sensitive zone.

    WHY store readings in a separate table?
      - A zone's AQI changes over time (simulated here, but real in production).
      - Storing them separately lets us query history, spot trends, and average values.
      - The `zone_id` foreign key links each reading back to its zone.

    AQI Scale Reference:
        0–50   : Good
        51–100 : Moderate
        101–150: Unhealthy for sensitive groups
        151–200: Unhealthy
        201–300: Very Unhealthy
        300+   : Hazardous

    Columns:
        id        : Auto-incremented primary key.
        zone_id   : FK → sensitive_zones.id
        aqi_value : The measured/simulated AQI value (float for precision).
        timestamp : When the reading was recorded (defaults to NOW).
    """
    __tablename__ = "aqi_readings"

    id        = Column(Integer,  primary_key=True, index=True)
    zone_id   = Column(Integer,  ForeignKey("sensitive_zones.id"), nullable=False)
    aqi_value = Column(Float,    nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Back-reference: from a reading, access its zone via reading.zone
    zone = relationship("SensitiveZone", back_populates="aqi_readings")


class RouteLog(Base):
    """
    Stores the history of every route calculation made through the API.

    WHY log routes?
      - Audit trail: know who requested what route and when.
      - Analytics: identify which source/destination pairs are most common.
      - Demo/viva: show that the system has real history data.

    Columns:
        id         : Auto-incremented primary key.
        source     : Human-readable source description (e.g., "9.9252, 78.1198").
        dest       : Human-readable destination description.
        route_json : The full route as a JSON string (list of [lat, lng] pairs).
        avg_aqi    : Average AQI exposure along the route (float).
        timestamp  : When the route was calculated (defaults to NOW).
    """
    __tablename__ = "route_logs"

    id         = Column(Integer,  primary_key=True, index=True)
    source     = Column(String,   nullable=False)
    dest       = Column(String,   nullable=False)
    route_json = Column(Text,     nullable=False)   # JSON string of coordinate list
    avg_aqi    = Column(Float,    nullable=True)
    timestamp  = Column(DateTime, default=datetime.utcnow)
