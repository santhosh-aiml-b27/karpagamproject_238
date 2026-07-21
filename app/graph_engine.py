"""
graph_engine.py - Road Network Graph Engine
============================================
This module is responsible for loading, caching, and querying the road network
graph for Madurai, India using OSMnx and NetworkX.

WHY OSMnx?
  OSMnx is a Python library that downloads real road network data from
  OpenStreetMap (OSM) — a free, crowd-sourced map database. It wraps NetworkX
  graphs with geographic metadata (coordinates, road names, speed limits, etc.).

WHY NetworkX?
  NetworkX is the most widely used Python graph library. It provides
  Dijkstra's algorithm (shortest_path) out-of-the-box, which we use with
  our custom 'eco_cost' edge weight to find the optimal eco-friendly route.

STARTUP FLOW:
  1. load_graph()          → Downloads/caches the Madurai road graph from OSM.
  2. generate_aqi_map()    → Simulates AQI for every node in the graph.
  3. build_weighted_graph()→ Annotates each edge with the 'eco_cost' weight.
  4. The ready graph is stored in module-level variables (GRAPH, AQI_MAP)
     and reused for all API requests.

IMPORTANT: The graph download may take 30–120 seconds on first run.
  On subsequent runs, OSMnx reads from a local disk cache automatically
  (when ox.settings.use_cache = True).
"""

import osmnx as ox
import networkx as nx
import logging
from typing import List, Tuple, Dict, Optional

from app.aqi_simulator import generate_aqi_map, SENSITIVE_ZONES, SENSITIVE_RADIUS_DEG
from app.cost_function import build_weighted_graph, DEFAULT_W1, DEFAULT_W2, DEFAULT_W3

import math

logger = logging.getLogger("graph_engine")

# ─── Module-Level Cache ───────────────────────────────────────────────────────
# These variables hold the loaded graph and AQI map in memory.
# They are initialised once at startup (see main.py lifespan event) and
# then READ by every route calculation — no need to reload per request.
GRAPH: Optional[nx.MultiDiGraph] = None
AQI_MAP: Optional[Dict[int, float]] = None

# The city to load the road network for.
CITY_NAME = "Madurai, India"


# ─── Graph Initialisation ────────────────────────────────────────────────────

def load_graph() -> nx.MultiDiGraph:
    """
    Downloads the real road network for Madurai, India from OpenStreetMap.

    WHAT IS network_type="drive"?
      It filters OSM data to only include roads that are usable by motor vehicles
      (excludes footpaths, cycle lanes, etc.). This keeps the graph manageable.

    WHAT DOES OSMnx ADD to the raw NetworkX graph?
      - Node attributes: 'y' (latitude), 'x' (longitude), 'osmid' (OSM node ID).
      - Edge attributes: 'length' (metres), 'name', 'maxspeed', 'highway' type.
      - It also adds travel speed and travel time to edges via `add_edge_speeds()`
        and `add_edge_travel_times()`.

    Returns:
        A NetworkX MultiDiGraph with real Madurai road data.

    Raises:
        Exception if the network cannot be downloaded (e.g., no internet).
    """
    logger.info(f"Loading road network graph for '{CITY_NAME}'...")
    logger.info("This may take 30–120 seconds on first run (downloading from OSM).")

    # Enable OSMnx disk caching so subsequent runs are instant
    ox.settings.use_cache = True
    ox.settings.log_console = False   # Suppress osmnx's own verbose output (we use our own logger)

    # Download the drivable road network
    G = ox.graph_from_place(CITY_NAME, network_type="drive")

    # Add realistic speed limits where missing (OSMnx uses road type heuristics)
    G = ox.add_edge_speeds(G)

    # Add travel time (seconds) to each edge: travel_time = length / speed
    G = ox.add_edge_travel_times(G)

    logger.info(f"Graph loaded: {len(G.nodes)} nodes, {len(G.edges)} edges.")
    return G


def initialise_engine():
    """
    Full startup sequence: load graph → generate AQI map → annotate edges.

    Called ONCE from main.py's lifespan context manager when the server starts.
    Populates the module-level GRAPH and AQI_MAP variables.

    WHY not do this on the first request?
      If we loaded the graph on-demand, the FIRST user to request a route would
      wait 30–120 seconds. Pre-loading at startup hides this latency behind
      the server start time, which is much better UX.
    """
    global GRAPH, AQI_MAP

    # Step 1: Load the real road graph
    GRAPH = load_graph()

    # Step 2: Simulate AQI for every node in the graph
    logger.info("Generating simulated AQI map for all graph nodes...")
    AQI_MAP = generate_aqi_map(GRAPH.nodes(data=True))
    logger.info(f"AQI map generated for {len(AQI_MAP)} nodes.")

    # Step 3: Annotate each edge with the 'eco_cost' weight (using default weights)
    logger.info("Building weighted graph with default cost weights...")
    GRAPH = build_weighted_graph(GRAPH, AQI_MAP, DEFAULT_W1, DEFAULT_W2, DEFAULT_W3)
    logger.info("Graph engine fully initialised and ready.")


# ─── Nearest Node Lookup ─────────────────────────────────────────────────────

def get_nearest_node(lat: float, lng: float) -> int:
    """
    Finds the closest graph node to the given latitude/longitude coordinate.

    WHY is this necessary?
      The user provides GPS coordinates (lat, lng) which may not exactly match
      any road intersection node in the graph. This function snaps the coordinate
      to the nearest node so we can start/end routing from a valid graph node.

    Args:
        lat: Latitude of the point (e.g., 9.9252).
        lng: Longitude of the point (e.g., 78.1198).

    Returns:
        The integer OSM node ID of the nearest graph node.

    Raises:
        RuntimeError if the graph has not been initialised yet.
    """
    if GRAPH is None:
        raise RuntimeError("Graph engine not initialised. Call initialise_engine() first.")

    # osmnx 2.x: nearest_nodes is available at top-level (ox.nearest_nodes)
    # osmnx 1.x: it was ox.distance.nearest_nodes — the top-level alias works for both
    node_id = ox.nearest_nodes(GRAPH, X=lng, Y=lat)
    return node_id


# ─── Route Calculation ───────────────────────────────────────────────────────

def calculate_route(
    source_lat: float, source_lng: float,
    dest_lat:   float, dest_lng:   float,
    w1: float = DEFAULT_W1,
    w2: float = DEFAULT_W2,
    w3: float = DEFAULT_W3,
) -> dict:
    """
    Calculates the optimal eco-route between two GPS coordinates.

    ALGORITHM WALKTHROUGH:
      1. Snap source and destination to the nearest graph nodes.
      2. If custom weights (w1, w2, w3) differ from defaults, rebuild edge costs.
         (Default-weight routes use the pre-computed 'eco_cost' attribute.)
      3. Run Dijkstra's shortest path algorithm using 'eco_cost' as the edge weight.
         NetworkX sums up eco_cost values along candidate paths and picks the path
         with the lowest TOTAL cost.
      4. Extract the ordered list of node IDs in the result path.
      5. Convert node IDs → (lat, lng) coordinates for the API response.
      6. Compute summary statistics: distance, travel time, average AQI.
      7. Identify which sensitive zones are NOT on the route (zones_avoided).

    Args:
        source_lat, source_lng: Starting GPS coordinates.
        dest_lat, dest_lng:     Destination GPS coordinates.
        w1, w2, w3:             Cost function weights (override defaults if needed).

    Returns:
        A dict with keys: route, total_distance, estimated_time,
                          avg_aqi_exposure, zones_avoided.

    Raises:
        nx.NetworkXNoPath if no route exists between source and destination.
        RuntimeError if the graph engine is not initialised.
    """
    if GRAPH is None or AQI_MAP is None:
        raise RuntimeError("Graph engine not initialised. Call initialise_engine() first.")

    # ── Step 1: Snap to nearest nodes ─────────────────────────────────────────
    source_node = get_nearest_node(source_lat, source_lng)
    dest_node   = get_nearest_node(dest_lat, dest_lng)
    logger.info(f"Routing from node {source_node} to node {dest_node}.")

    # ── Step 2: Rebuild costs if custom weights were provided ──────────────────
    use_custom_weights = (
        abs(w1 - DEFAULT_W1) > 1e-6 or
        abs(w2 - DEFAULT_W2) > 1e-6 or
        abs(w3 - DEFAULT_W3) > 1e-6
    )
    working_graph = GRAPH
    if use_custom_weights:
        logger.info(f"Custom weights detected (w1={w1}, w2={w2}, w3={w3}). Rebuilding edge costs.")
        working_graph = build_weighted_graph(
            GRAPH.copy(), AQI_MAP, w1=w1, w2=w2, w3=w3
        )

    # ── Step 3: Run Dijkstra's shortest-path algorithm ────────────────────────
    # NetworkX's shortest_path with weight='eco_cost' uses Dijkstra internally.
    # It returns the ordered list of node IDs forming the minimum-cost path.
    try:
        path_nodes = nx.shortest_path(
            working_graph,
            source=source_node,
            target=dest_node,
            weight="eco_cost",   # This tells NetworkX which edge attribute to minimise
        )
    except nx.NetworkXNoPath:
        raise nx.NetworkXNoPath(
            f"No drivable path found between ({source_lat},{source_lng}) "
            f"and ({dest_lat},{dest_lng})."
        )

    # ── Step 4 & 5: Convert node IDs to coordinates ───────────────────────────
    coordinates: List[List[float]] = []
    aqi_values_on_route: List[float] = []

    for node_id in path_nodes:
        node_data = GRAPH.nodes[node_id]
        lat = node_data["y"]   # OSMnx: 'y' = latitude
        lng = node_data["x"]   # OSMnx: 'x' = longitude
        coordinates.append([lat, lng])
        aqi_values_on_route.append(AQI_MAP.get(node_id, 100.0))

    # ── Step 6: Compute summary statistics ────────────────────────────────────
    # Total distance: sum of 'length' attribute on each consecutive edge in path
    total_distance_m = 0.0
    total_time_s = 0.0

    for i in range(len(path_nodes) - 1):
        u = path_nodes[i]
        v = path_nodes[i + 1]
        # OSMnx MultiDiGraph can have parallel edges; take the shortest-time one
        edge_data = min(
            GRAPH[u][v].values(),
            key=lambda e: e.get("travel_time", float("inf"))
        )
        total_distance_m += edge_data.get("length", 0.0)
        total_time_s     += edge_data.get("travel_time", 0.0)

    avg_aqi = sum(aqi_values_on_route) / len(aqi_values_on_route) if aqi_values_on_route else 0.0
    estimated_time_min = total_time_s / 60.0  # Convert seconds → minutes

    # ── Step 7: Determine zones avoided ───────────────────────────────────────
    # A zone is "avoided" if NONE of the route's nodes are within its radius.
    zones_avoided = _get_avoided_zones(path_nodes)

    return {
        "route":            coordinates,
        "total_distance":   round(total_distance_m, 2),
        "estimated_time":   round(estimated_time_min, 2),
        "avg_aqi_exposure": round(avg_aqi, 2),
        "zones_avoided":    zones_avoided,
    }


def _get_avoided_zones(path_nodes: List[int]) -> List[str]:
    """
    Returns the names of sensitive zones that the given route does NOT pass through.

    LOGIC:
      For each sensitive zone, scan every node in the route.
      If NO route node is within SENSITIVE_RADIUS_DEG of the zone → zone was avoided.

    Args:
        path_nodes: Ordered list of node IDs forming the route.

    Returns:
        List of zone names that were successfully avoided.
    """
    # Build a set of (lat, lng) tuples for all route nodes (faster lookup)
    route_coords = [
        (GRAPH.nodes[n]["y"], GRAPH.nodes[n]["x"])
        for n in path_nodes
    ]

    avoided = []
    for zone in SENSITIVE_ZONES:
        zone_avoided = True
        for (lat, lng) in route_coords:
            dist = math.sqrt((lat - zone["lat"]) ** 2 + (lng - zone["lng"]) ** 2)
            if dist < SENSITIVE_RADIUS_DEG:
                zone_avoided = False
                break
        if zone_avoided:
            avoided.append(zone["name"])

    return avoided
