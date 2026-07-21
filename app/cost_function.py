"""
cost_function.py - Multi-Objective Route Cost Calculator
=========================================================
This is the HEART of the EcoRoute AI system.

PROBLEM STATEMENT:
  Standard GPS routing only optimises for travel TIME (or distance).
  EcoRoute AI also wants to minimise AIR POLLUTION EXPOSURE and avoid
  SENSITIVE ZONES (schools/hospitals). These are conflicting objectives —
  the fastest road might pass through a high-AQI zone.

SOLUTION — Weighted Sum Multi-Objective Function:
  We combine all three objectives into a SINGLE cost value for each edge
  (road segment) in the graph. NetworkX's shortest_path() algorithm then
  finds the path with the LOWEST TOTAL COST.

THE COST FORMULA:
  ┌─────────────────────────────────────────────────────────────────────┐
  │  cost = w1 × travel_time  +  w2 × aqi_norm  +  w3 × zone_penalty  │
  └─────────────────────────────────────────────────────────────────────┘

  Where:
    w1 = Weight for travel time        (default: 0.5 → 50% importance)
    w2 = Weight for AQI exposure       (default: 0.3 → 30% importance)
    w3 = Weight for zone sensitivity   (default: 0.2 → 20% importance)

  IMPORTANT: w1 + w2 + w3 SHOULD equal 1.0 to keep costs interpretable.

NORMALISATION — WHY IS IT NECESSARY?
  travel_time is in SECONDS (could be 0–600+).
  AQI is on a 0–350 scale.
  zone_penalty is a discrete 0 or 1.
  
  If we add these raw numbers, AQI would dominate purely because its scale
  is larger. Normalisation brings each value into the [0, 1] range so the
  weights w1, w2, w3 have their intended meaning.
"""

import math
from typing import Dict, Optional

# Import the list of sensitive zones from the simulator
from app.aqi_simulator import SENSITIVE_ZONES, SENSITIVE_RADIUS_DEG


# ─── Default Cost Function Weights ───────────────────────────────────────────
# These can be overridden per-request via the RouteRequest schema.
DEFAULT_W1 = 0.5   # Travel time is the most important factor
DEFAULT_W2 = 0.3   # AQI pollution exposure is second most important
DEFAULT_W3 = 0.2   # Zone proximity penalty is least important but still significant

# ─── Normalisation Constants ─────────────────────────────────────────────────
# MAX_TRAVEL_TIME_S: Approximate upper bound for any single edge's travel time (seconds).
#   A 2 km urban road at 30 km/h takes ~240 s. We use 300 s as a safe upper bound.
MAX_TRAVEL_TIME_S = 300.0

# MAX_AQI: Upper bound for AQI normalisation. We use 350 (exceeds "Hazardous" threshold).
MAX_AQI = 350.0


# ─── Zone Sensitivity Check ──────────────────────────────────────────────────

def _is_near_sensitive_zone(lat: float, lng: float) -> bool:
    """
    Returns True if the coordinate (lat, lng) is within the sensitive radius
    of ANY predefined sensitive zone (school/hospital).

    WHY a binary check instead of a graded penalty?
      A binary penalty is simpler to explain and tune. The AQI term already
      provides a graded penalty near zones (since simulate_aqi_for_node()
      assigns higher AQI near zones). The zone_penalty term adds an extra
      hard incentive to avoid the zone boundary, complementing the AQI term.

    Args:
        lat: Latitude of the node to check.
        lng: Longitude of the node to check.

    Returns:
        True if within SENSITIVE_RADIUS_DEG of any zone; False otherwise.
    """
    for zone in SENSITIVE_ZONES:
        dist = math.sqrt((lat - zone["lat"]) ** 2 + (lng - zone["lng"]) ** 2)
        if dist < SENSITIVE_RADIUS_DEG:
            return True
    return False


# ─── Core Edge Cost Calculator ───────────────────────────────────────────────

def compute_edge_cost(
    u_data: dict,
    v_data: dict,
    edge_data: dict,
    aqi_map: Dict[int, float],
    node_u_id: int,
    node_v_id: int,
    w1: float = DEFAULT_W1,
    w2: float = DEFAULT_W2,
    w3: float = DEFAULT_W3,
) -> float:
    """
    Computes the multi-objective cost for a SINGLE EDGE (road segment) in the graph.

    This function is called for every edge during route calculation.
    NetworkX sums these edge costs along a path to find the minimum-cost route.

    HOW EACH TERM IS CALCULATED:
    ─────────────────────────────

    TERM 1 — Travel Time (w1):
      travel_time_s = edge_data["length"] / speed_m_per_s
        - length is in metres (from OSMnx).
        - speed defaults to 13.9 m/s (50 km/h) if not specified in the graph.
      travel_time_norm = travel_time_s / MAX_TRAVEL_TIME_S
        - Dividing by 300 s maps this into [0, ~2] range (capped at 1 in practice).

    TERM 2 — AQI Exposure (w2):
      aqi_avg = average of AQI at node u and node v (both endpoints of the edge).
        - Averaging endpoints approximates the AQI experienced while traversing the edge.
      aqi_norm = aqi_avg / MAX_AQI
        - Maps AQI from [0, 350] to [0, 1].

    TERM 3 — Zone Sensitivity Penalty (w3):
      zone_penalty = 1.0 if EITHER endpoint is near a sensitive zone, else 0.0
        - This is a binary "flag" that fires whenever the road is near a school/hospital.
        - When multiplied by w3, it adds exactly w3 to the cost (e.g., +0.2).

    FINAL COMBINATION:
      cost = (w1 × travel_time_norm) + (w2 × aqi_norm) + (w3 × zone_penalty)

      Since all three normalised terms are in [0, 1] and weights sum to ~1.0,
      the total cost is bounded approximately in [0, 1].
      Lower cost = better route.

    Args:
        u_data:     OSMnx node attributes for the start of the edge.
        v_data:     OSMnx node attributes for the end of the edge.
        edge_data:  OSMnx edge attributes (length, maxspeed, etc.).
        aqi_map:    Dict mapping node_id → simulated AQI value.
        node_u_id:  Integer ID of node u (used to look up AQI).
        node_v_id:  Integer ID of node v (used to look up AQI).
        w1:         Weight for travel time (default 0.5).
        w2:         Weight for AQI exposure (default 0.3).
        w3:         Weight for zone penalty (default 0.2).

    Returns:
        A single float representing the combined cost of traversing this edge.
        LOWER is BETTER (NetworkX minimises this).
    """

    # ── TERM 1: Travel Time ───────────────────────────────────────────────────
    length_m = edge_data.get("length", 50.0)       # metres; default 50 m if missing

    # Parse speed from graph: OSMnx may store speed as a string "50" or list ["50","60"]
    raw_speed = edge_data.get("maxspeed", "50")
    if isinstance(raw_speed, list):
        raw_speed = raw_speed[0]                    # Take the first value if it's a list
    try:
        speed_kmh = float(str(raw_speed).replace(" mph", "").strip())
    except (ValueError, AttributeError):
        speed_kmh = 50.0                            # Sensible urban default

    speed_mps = speed_kmh / 3.6                    # Convert km/h → m/s  (1 km/h = 1/3.6 m/s)
    travel_time_s = length_m / speed_mps           # time = distance / speed

    # Normalise: divide by max expected edge travel time, then cap at 1.0
    travel_time_norm = min(travel_time_s / MAX_TRAVEL_TIME_S, 1.0)

    # ── TERM 2: AQI Exposure ──────────────────────────────────────────────────
    aqi_u = aqi_map.get(node_u_id, 100.0)          # AQI at start node (default 100 if missing)
    aqi_v = aqi_map.get(node_v_id, 100.0)          # AQI at end node
    aqi_avg = (aqi_u + aqi_v) / 2.0                # Average AQI across the edge

    # Normalise: divide by max AQI scale value
    aqi_norm = aqi_avg / MAX_AQI

    # ── TERM 3: Zone Sensitivity Penalty ──────────────────────────────────────
    lat_u = u_data.get("y", 0.0)
    lng_u = u_data.get("x", 0.0)
    lat_v = v_data.get("y", 0.0)
    lng_v = v_data.get("x", 0.0)

    # Check if EITHER endpoint of this road segment is near a sensitive zone
    near_zone = _is_near_sensitive_zone(lat_u, lng_u) or \
                _is_near_sensitive_zone(lat_v, lng_v)

    zone_penalty = 1.0 if near_zone else 0.0       # Binary: 1 = near zone, 0 = safe

    # ── FINAL WEIGHTED SUM ────────────────────────────────────────────────────
    #
    #   cost = w1 × travel_time_norm  +  w2 × aqi_norm  +  w3 × zone_penalty
    #
    # INTUITION:
    #   If w1=0.5, w2=0.3, w3=0.2 and an edge has:
    #     - travel_time_norm = 0.4  (moderately slow road)
    #     - aqi_norm         = 0.6  (fairly polluted)
    #     - zone_penalty     = 1.0  (passes near a hospital)
    #
    #   cost = 0.5×0.4 + 0.3×0.6 + 0.2×1.0
    #        = 0.20    + 0.18    + 0.20
    #        = 0.58
    #
    #   A cleaner, faster route with no zone penalty would score lower,
    #   so the algorithm would prefer it.
    #
    cost = (w1 * travel_time_norm) + (w2 * aqi_norm) + (w3 * zone_penalty)

    return cost


def build_weighted_graph(graph, aqi_map: Dict[int, float],
                         w1: float = DEFAULT_W1,
                         w2: float = DEFAULT_W2,
                         w3: float = DEFAULT_W3):
    """
    Annotates every edge in the NetworkX graph with a 'eco_cost' attribute
    computed by compute_edge_cost().

    WHY pre-compute and store costs on edges?
      NetworkX's dijkstra_path() accepts a `weight` parameter that can be
      a string (attribute name) OR a callable. Pre-storing costs as edge
      attributes is more efficient for repeated route queries because the
      cost is computed ONCE during startup rather than on every shortest-path call.

    Args:
        graph:   An OSMnx/NetworkX MultiDiGraph.
        aqi_map: Dict of node_id → AQI value from aqi_simulator.py.
        w1, w2, w3: Cost function weights.

    Returns:
        The SAME graph object with 'eco_cost' added to each edge's attributes.
    """
    for u, v, key, edge_data in graph.edges(keys=True, data=True):
        u_data = graph.nodes[u]
        v_data = graph.nodes[v]

        edge_data["eco_cost"] = compute_edge_cost(
            u_data=u_data,
            v_data=v_data,
            edge_data=edge_data,
            aqi_map=aqi_map,
            node_u_id=u,
            node_v_id=v,
            w1=w1,
            w2=w2,
            w3=w3,
        )

    return graph
