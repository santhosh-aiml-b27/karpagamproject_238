"""
schemas.py - Pydantic Request & Response Models
================================================
Pydantic models define the SHAPE of data coming INTO and going OUT OF the API.

WHY Pydantic?
  - FastAPI uses Pydantic under the hood for automatic request validation.
  - If a client sends wrong data types (e.g., a string where a float is expected),
    FastAPI returns a clear 422 error — no manual validation code needed.
  - Pydantic models also auto-generate the OpenAPI (Swagger) documentation.

SEPARATION OF CONCERNS:
  - SQLAlchemy models (models.py) = database table structure
  - Pydantic schemas (this file)  = what the API accepts and returns
  They look similar but serve completely different roles.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# ═══════════════════════════════════════════════════════════════════════════════
#  REQUEST SCHEMAS  (data the CLIENT sends TO the server)
# ═══════════════════════════════════════════════════════════════════════════════

class RouteRequest(BaseModel):
    """
    Input payload for POST /get-route.

    The client provides source and destination coordinates plus the vehicle type.
    Optional weight overrides let the caller tune the cost function on-the-fly.

    Example JSON body:
        {
            "source_lat": 9.9252,
            "source_lng": 78.1198,
            "dest_lat":   9.9510,
            "dest_lng":   78.0820,
            "vehicle_type": "car"
        }
    """
    source_lat:   float = Field(..., description="Latitude of the starting point")
    source_lng:   float = Field(..., description="Longitude of the starting point")
    dest_lat:     float = Field(..., description="Latitude of the destination")
    dest_lng:     float = Field(..., description="Longitude of the destination")
    vehicle_type: str   = Field(default="car", description="Vehicle type: car | bike | truck")

    # Optional cost-function weight overrides (if omitted, defaults from cost_function.py are used)
    w1: Optional[float] = Field(default=None, description="Weight for travel time (default 0.5)")
    w2: Optional[float] = Field(default=None, description="Weight for AQI exposure (default 0.3)")
    w3: Optional[float] = Field(default=None, description="Weight for zone sensitivity (default 0.2)")


class SensorDataRequest(BaseModel):
    """
    Input payload for POST /sensor-data.

    Simulates an IoT sensor pushing an AQI reading to the server.
    In a real system this would come from a physical air quality sensor.

    Example JSON body:
        {
            "zone_id": 2,
            "aqi_value": 142.7
        }
    """
    zone_id:   int   = Field(..., description="ID of the sensitive zone the sensor belongs to")
    aqi_value: float = Field(..., ge=0, description="AQI reading from the sensor (must be ≥ 0)")


# ═══════════════════════════════════════════════════════════════════════════════
#  RESPONSE SCHEMAS  (data the SERVER sends BACK to the client)
# ═══════════════════════════════════════════════════════════════════════════════

class RouteResponse(BaseModel):
    """
    Response body for POST /get-route.

    Contains the calculated route plus summary statistics that are useful
    for a driver or a front-end map display.
    """
    route:            List[List[float]]  # List of [latitude, longitude] coordinate pairs
    total_distance:   float              # Total route length in metres
    estimated_time:   float              # Estimated travel time in minutes
    avg_aqi_exposure: float              # Mean AQI value across all route nodes
    zones_avoided:    List[str]          # Names of sensitive zones the route avoided


class ZoneResponse(BaseModel):
    """
    Response schema for a single sensitive zone (used in GET /zones).
    """
    id:   int
    name: str
    lat:  float
    lng:  float
    type: str

    class Config:
        # from_attributes=True allows Pydantic to read data from SQLAlchemy ORM objects
        # (instead of plain dicts). Renamed from orm_mode in Pydantic V2.
        from_attributes = True


class AQIResponse(BaseModel):
    """
    Response schema for GET /aqi/{zone_id}.
    Returns the latest (or freshly simulated) AQI reading for a zone.
    """
    zone_id:   int
    zone_name: str
    aqi_value: float
    category:  str    # e.g., "Good", "Moderate", "Unhealthy", etc.
    timestamp: datetime


class SensorDataResponse(BaseModel):
    """
    Confirmation response for POST /sensor-data.
    Lets the client know the reading was accepted and stored.
    """
    message:   str
    zone_id:   int
    aqi_value: float
    timestamp: datetime


class RouteLogResponse(BaseModel):
    """
    Response schema for a single entry in GET /route-history.
    """
    id:        int
    source:    str
    dest:      str
    avg_aqi:   Optional[float]
    timestamp: datetime

    class Config:
        from_attributes = True   # Pydantic V2: replaces orm_mode = True
