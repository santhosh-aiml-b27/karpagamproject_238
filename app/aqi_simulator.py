"""
aqi_simulator.py - Simulated AQI Data Generator
================================================
Since we don't have physical IoT sensors, this module SIMULATES Air Quality Index
(AQI) readings in a way that is realistic enough for demos and testing.

KEY DESIGN DECISIONS:
  1. AQI values are random within a base range (50–300).
  2. Nodes/edges near predefined "sensitive zones" (schools, hospitals) receive
     HIGHER simulated AQI — this mimics real-world pollution hotspots near
     busy intersections around such facilities.
  3. We add a small random "jitter" each time a value is requested so successive
     readings for the same zone look realistic (not stuck at one number).

AQI SCALE (US EPA Standard):
    0–50   : Good           (green)
    51–100 : Moderate       (yellow)
    101–150: Unhealthy for Sensitive Groups (orange)
    151–200: Unhealthy      (red)
    201–300: Very Unhealthy (purple)
    300+   : Hazardous      (maroon)
"""

import random
import math
from datetime import datetime
from typing import Dict, Tuple


# ─── Predefined Sensitive Zones in Madurai ────────────────────────────────────
# These are REAL landmarks in Madurai, Tamil Nadu, India.
# Each entry: (zone_id, name, latitude, longitude, zone_type)
#
# WHY hardcode these?
#   In a production system, zones would come from the database.
#   Here we hardcode them so the simulator can work independently of the DB,
#   and they are also seeded INTO the DB on startup (see main.py).
SENSITIVE_ZONES = [
    {
        "id":   1,
        "name": "Madurai Government Rajaji Hospital",
        "lat":  9.9191,
        "lng":  78.1167,
        "type": "hospital",
    },
    {
        "id":   2,
        "name": "Lady Doak College (School Zone)",
        "lat":  9.9312,
        "lng":  78.1268,
        "type": "school",
    },
    {
        "id":   3,
        "name": "Meenakshi Mission Hospital",
        "lat":  9.9089,
        "lng":  78.1337,
        "type": "hospital",
    },
    {
        "id":   4,
        "name": "St. Mary's School, Madurai",
        "lat":  9.9402,
        "lng":  78.1080,
        "type": "school",
    },
]

# Radius (in degrees ~= km at this latitude) within which a node is considered
# "near" a sensitive zone for AQI elevation purposes.
SENSITIVE_RADIUS_DEG = 0.008   # ≈ 0.8 km


# ─── AQI Category Helper ──────────────────────────────────────────────────────

def get_aqi_category(aqi_value: float) -> str:
    """
    Converts a numeric AQI value to its human-readable health category.

    This follows the US EPA AQI breakpoints which are widely used
    even for Indian air quality reporting.

    Args:
        aqi_value: The numeric AQI (0–500+).

    Returns:
        A string category label.
    """
    if aqi_value <= 50:
        return "Good"
    elif aqi_value <= 100:
        return "Moderate"
    elif aqi_value <= 150:
        return "Unhealthy for Sensitive Groups"
    elif aqi_value <= 200:
        return "Unhealthy"
    elif aqi_value <= 300:
        return "Very Unhealthy"
    else:
        return "Hazardous"


# ─── Distance Helper ─────────────────────────────────────────────────────────

def _haversine_deg(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Returns approximate distance between two coordinates in degrees.

    WHY degrees and not metres?
      For the proximity check we just need a quick scalar comparison.
      Converting to full metres (Haversine formula) would be more accurate
      but is unnecessary overhead when we only need a rough radius check.

    Args:
        lat1, lng1: First point coordinates.
        lat2, lng2: Second point coordinates.

    Returns:
        Euclidean distance in degrees (approximate).
    """
    return math.sqrt((lat1 - lat2) ** 2 + (lng1 - lng2) ** 2)


# ─── Core AQI Simulation ─────────────────────────────────────────────────────

def simulate_aqi_for_node(node_lat: float, node_lng: float) -> float:
    """
    Generates a simulated AQI reading for a graph node at the given coordinates.

    ALGORITHM:
      1. Start with a random BASE AQI in the range [50, 150] — typical urban air.
      2. For each sensitive zone, compute the distance from this node to that zone.
      3. If the node is within SENSITIVE_RADIUS_DEG of a zone, add a PROXIMITY BOOST
         that is inversely proportional to the distance (closer = higher penalty).
      4. Add a small random jitter (±10) to simulate natural variation.
      5. Clamp the result to the range [0, 350].

    WHY higher AQI near sensitive zones?
      In the real world, busy roads around schools and hospitals carry more traffic
      → more emissions → higher pollution. This simulates that effect.

    Args:
        node_lat: Latitude of the road network node.
        node_lng: Longitude of the road network node.

    Returns:
        Simulated AQI value (float) for this node.
    """
    # Step 1: Random base AQI for general urban pollution
    base_aqi = random.uniform(50, 150)

    # Step 2 & 3: Check proximity to each sensitive zone and add a boost if close
    proximity_boost = 0.0
    for zone in SENSITIVE_ZONES:
        dist = _haversine_deg(node_lat, node_lng, zone["lat"], zone["lng"])
        if dist < SENSITIVE_RADIUS_DEG:
            # The closer the node is to the zone, the larger the boost.
            # We use (SENSITIVE_RADIUS_DEG - dist) so that being AT the zone
            # centre gives max boost, and being at the edge gives near-zero boost.
            # The scaling factor (150 / SENSITIVE_RADIUS_DEG) maps this to a
            # maximum additional AQI of ~150 (pushing into "Very Unhealthy").
            closeness = (SENSITIVE_RADIUS_DEG - dist) / SENSITIVE_RADIUS_DEG
            proximity_boost += closeness * 150

    # Step 4: Add random jitter for realism
    jitter = random.uniform(-10, 10)

    # Step 5: Combine and clamp
    aqi = base_aqi + proximity_boost + jitter
    return max(0.0, min(350.0, aqi))


def generate_aqi_map(graph_nodes) -> Dict[int, float]:
    """
    Generates a simulated AQI value for every node in the road network graph.

    This is called ONCE at startup and the resulting dictionary is cached in
    graph_engine.py. This avoids recalculating AQI on every route request.

    Args:
        graph_nodes: The node data from a NetworkX/OSMnx graph
                     (graph.nodes(data=True)).

    Returns:
        A dict mapping  node_id (int) → aqi_value (float).

    Example:
        {
            123456789: 87.3,
            987654321: 210.5,
            ...
        }
    """
    aqi_map: Dict[int, float] = {}

    for node_id, node_data in graph_nodes:
        lat = node_data.get("y", 0.0)   # OSMnx stores latitude as 'y'
        lng = node_data.get("x", 0.0)   # OSMnx stores longitude as 'x'
        aqi_map[node_id] = simulate_aqi_for_node(lat, lng)

    return aqi_map


def get_zone_aqi(zone_id: int) -> Tuple[float, datetime]:
    """
    Returns a fresh simulated AQI reading for a specific sensitive zone.

    Called by GET /aqi/{zone_id}. Each call generates a slightly different
    value (±jitter) to simulate a live sensor.

    Args:
        zone_id: The ID of the sensitive zone (1–4 in our predefined list).

    Returns:
        Tuple of (aqi_value, timestamp).
        Raises ValueError if zone_id is not found.
    """
    zone = next((z for z in SENSITIVE_ZONES if z["id"] == zone_id), None)
    if zone is None:
        raise ValueError(f"Zone ID {zone_id} not found in predefined zones.")

    aqi = simulate_aqi_for_node(zone["lat"], zone["lng"])
    return aqi, datetime.utcnow()


def get_predicted_aqi(zone_id: int) -> float:
    """
    Returns a PREDICTED AQI value for the given zone.

    TODO: Replace this function's body with the LSTM model output from the ML team.
          The ML team should pass in historical AQI readings and receive a
          time-series prediction. For now, this returns freshly simulated data
          as a placeholder so the rest of the system can be tested end-to-end.

    Args:
        zone_id: ID of the sensitive zone to predict AQI for.

    Returns:
        Predicted AQI value (float). Currently returns a simulated value.
    """
    # ─── PLACEHOLDER ──────────────────────────────────────────────────────────
    # In production: call the ML service's prediction API here.
    # e.g.: return ml_service.predict(zone_id=zone_id, horizon_minutes=30)
    aqi, _ = get_zone_aqi(zone_id)
    return aqi
