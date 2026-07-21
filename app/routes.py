"""
routes.py - API Endpoint Definitions
=====================================
This module defines all HTTP endpoints for the EcoRoute AI backend.

ORGANISATION:
  All routes are registered on a single APIRouter which is then included
  in the main FastAPI app (main.py). This keeps routes.py focused purely
  on endpoint logic and keeps main.py clean.

DEPENDENCY INJECTION:
  FastAPI's `Depends(get_db)` pattern injects a fresh database session into
  each endpoint. This session is automatically closed after the request
  finishes (see db.py:get_db).

ENDPOINTS SUMMARY:
  POST /get-route       → Calculate an eco-optimised route
  GET  /aqi/{zone_id}  → Get current AQI for a zone
  GET  /zones           → List all sensitive zones
  POST /sensor-data     → Accept & store a simulated sensor reading
  GET  /route-history   → Return last 10 calculated routes
"""

import json
import logging
from datetime import datetime

import networkx as nx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import graph_engine
from app.aqi_simulator import (
    get_zone_aqi,
    get_aqi_category,
    SENSITIVE_ZONES,
)
from app.db import get_db
from app.models import AQIReading, RouteLog, SensitiveZone
from app.schemas import (
    AQIResponse,
    RouteLogResponse,
    RouteRequest,
    RouteResponse,
    SensorDataRequest,
    SensorDataResponse,
    ZoneResponse,
)

logger = logging.getLogger("routes")

# Create a router — all endpoints below will be prefixed/grouped by this router
router = APIRouter()


# ═══════════════════════════════════════════════════════════════════════════════
#  ENDPOINT 1: POST /get-route
# ═══════════════════════════════════════════════════════════════════════════════

@router.post(
    "/get-route",
    response_model=RouteResponse,
    summary="Calculate an eco-optimised route",
    description=(
        "Given source and destination coordinates, returns the route that minimises "
        "a weighted combination of travel time, AQI pollution exposure, and "
        "sensitive zone proximity."
    ),
)
def get_route(request: RouteRequest, db: Session = Depends(get_db)):
    """
    Main routing endpoint — the core feature of EcoRoute AI.

    FLOW:
      1. Extract weights from request (use defaults if not provided).
      2. Call graph_engine.calculate_route() which runs Dijkstra's algorithm
         with the custom eco_cost edge weights.
      3. Log the result to the route_logs table in the database.
      4. Return the route as a JSON response.

    POSSIBLE ERRORS:
      - 503: Graph not yet loaded (server still starting up).
      - 404: No path exists between the two coordinates.
      - 500: Unexpected internal error.
    """
    # ── Extract custom weights (fall back to defaults if not provided) ─────────
    w1 = request.w1 if request.w1 is not None else 0.5
    w2 = request.w2 if request.w2 is not None else 0.3
    w3 = request.w3 if request.w3 is not None else 0.2

    # ── Check that the graph engine is ready ──────────────────────────────────
    if graph_engine.GRAPH is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Graph engine is still loading. Please retry in a moment.",
        )

    # ── Calculate route ───────────────────────────────────────────────────────
    try:
        result = graph_engine.calculate_route(
            source_lat=request.source_lat,
            source_lng=request.source_lng,
            dest_lat=request.dest_lat,
            dest_lng=request.dest_lng,
            w1=w1, w2=w2, w3=w3,
        )
    except nx.NetworkXNoPath as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )
    except Exception as e:
        logger.exception("Unexpected error during route calculation.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Route calculation failed: {str(e)}",
        )

    # ── Persist route to database ──────────────────────────────────────────────
    route_log = RouteLog(
        source=f"{request.source_lat}, {request.source_lng}",
        dest=f"{request.dest_lat}, {request.dest_lng}",
        route_json=json.dumps(result["route"]),   # Store list as JSON string
        avg_aqi=result["avg_aqi_exposure"],
        timestamp=datetime.utcnow(),
    )
    db.add(route_log)
    db.commit()
    logger.info(f"Route logged to DB (id={route_log.id}).")

    return RouteResponse(**result)


# ═══════════════════════════════════════════════════════════════════════════════
#  ENDPOINT 2: GET /aqi/{zone_id}
# ═══════════════════════════════════════════════════════════════════════════════

@router.get(
    "/aqi/{zone_id}",
    response_model=AQIResponse,
    summary="Get current AQI for a sensitive zone",
    description="Returns a freshly simulated AQI reading for the specified zone.",
)
def get_aqi(zone_id: int):
    """
    Returns the current (simulated) AQI for a given sensitive zone.

    Each call generates a slightly different value (with jitter) to simulate
    a live IoT sensor. In production, this would query a real sensor database
    or the ML team's LSTM prediction service.

    Path parameter:
        zone_id: Integer ID of the zone (1 to 4 in the predefined list).
    """
    # Find the zone metadata (name, type) from the predefined list
    zone_meta = next((z for z in SENSITIVE_ZONES if z["id"] == zone_id), None)
    if zone_meta is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Zone with ID {zone_id} not found. Valid IDs are 1–4.",
        )

    try:
        aqi_value, timestamp = get_zone_aqi(zone_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    return AQIResponse(
        zone_id=zone_id,
        zone_name=zone_meta["name"],
        aqi_value=round(aqi_value, 2),
        category=get_aqi_category(aqi_value),
        timestamp=timestamp,
    )


# ═══════════════════════════════════════════════════════════════════════════════
#  ENDPOINT 3: GET /zones
# ═══════════════════════════════════════════════════════════════════════════════

@router.get(
    "/zones",
    response_model=list[ZoneResponse],
    summary="List all sensitive zones",
    description=(
        "Returns all predefined sensitive zones (schools and hospitals) with their "
        "coordinates and type. Use these coordinates to display zones on a map."
    ),
)
def get_zones(db: Session = Depends(get_db)):
    """
    Returns all sensitive zones stored in the database.

    WHY query the DB instead of returning SENSITIVE_ZONES directly?
      The DB is the single source of truth. If an admin adds a new zone via
      another tool, this endpoint reflects it immediately.
      On startup (main.py), the SENSITIVE_ZONES list is seeded into the DB.
    """
    zones = db.query(SensitiveZone).all()
    if not zones:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No zones found. Database may not have been seeded yet.",
        )
    return zones


# ═══════════════════════════════════════════════════════════════════════════════
#  ENDPOINT 4: POST /sensor-data
# ═══════════════════════════════════════════════════════════════════════════════

@router.post(
    "/sensor-data",
    response_model=SensorDataResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit simulated IoT sensor data",
    description=(
        "Accepts an AQI reading from a (simulated) IoT sensor and stores it "
        "in the aqi_readings table. In production, physical sensors would POST here."
    ),
)
def submit_sensor_data(request: SensorDataRequest, db: Session = Depends(get_db)):
    """
    Stores an incoming AQI sensor reading in the database.

    SIMULATION NOTE:
      This endpoint is designed for real IoT sensors but works equally well
      with the Python simulation scripts (see test_api.py). The data format
      is identical either way.

    VALIDATION:
      - zone_id must correspond to an existing zone in the DB.
      - aqi_value must be ≥ 0 (enforced by Pydantic schema).
    """
    # Verify the zone exists in the database
    zone = db.query(SensitiveZone).filter(SensitiveZone.id == request.zone_id).first()
    if zone is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Zone ID {request.zone_id} not found in database.",
        )

    # Create and store the AQI reading record
    reading = AQIReading(
        zone_id=request.zone_id,
        aqi_value=request.aqi_value,
        timestamp=datetime.utcnow(),
    )
    db.add(reading)
    db.commit()
    db.refresh(reading)  # Refresh to populate auto-generated fields (id, timestamp)

    logger.info(
        f"Sensor data stored: zone_id={request.zone_id}, aqi={request.aqi_value}"
    )

    return SensorDataResponse(
        message="Sensor data accepted and stored successfully.",
        zone_id=reading.zone_id,
        aqi_value=reading.aqi_value,
        timestamp=reading.timestamp,
    )


# ═══════════════════════════════════════════════════════════════════════════════
#  ENDPOINT 5: GET /route-history
# ═══════════════════════════════════════════════════════════════════════════════

@router.get(
    "/route-history",
    response_model=list[RouteLogResponse],
    summary="Get the last 10 calculated routes",
    description="Returns the 10 most recent route calculation records from the database.",
)
def get_route_history(db: Session = Depends(get_db)):
    """
    Returns the last 10 routes that were calculated by the system.

    WHY only 10?
      This endpoint is for quick review and demo purposes. Returning all routes
      could be thousands of records for a production system. A paginated
      endpoint with `limit` and `offset` parameters would be appropriate in production.

    Sorted by: timestamp descending (most recent first).
    """
    logs = (
        db.query(RouteLog)
        .order_by(RouteLog.timestamp.desc())
        .limit(10)
        .all()
    )
    return logs
