# EcoRoute AI 🌿🗺️

> **A smart traffic routing system that balances travel time, air quality (AQI), and sensitive zone avoidance.**

Built with **FastAPI** · **OSMnx** · **NetworkX** · **SQLite**

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Project Structure](#project-structure)
3. [How to Run](#how-to-run)
4. [How the Routing Algorithm Works](#how-the-routing-algorithm-works)
5. [API Endpoints](#api-endpoints)
6. [Example API Calls (curl)](#example-api-calls-curl)
7. [Database Schema](#database-schema)
8. [Configuration & Customisation](#configuration--customisation)

---

## Project Overview

Standard GPS apps find the **fastest** route. EcoRoute AI finds the **healthiest** route.

It considers three factors simultaneously:

| Factor | What It Means |
|--------|--------------|
| 🕐 Travel Time | How long will the journey take? |
| 💨 AQI Exposure | How much air pollution will you breathe? |
| 🏥 Zone Sensitivity | Does the route pass near schools or hospitals? |

These three factors are combined into a single **cost score** per road segment. The routing algorithm finds the path with the lowest total cost.

---

## Project Structure

```
karpagamproject_238/
│
├── app/
│   ├── __init__.py       ← Makes `app` a Python package
│   ├── main.py           ← FastAPI app entry point & startup logic
│   ├── routes.py         ← All API endpoint definitions
│   ├── graph_engine.py   ← Road network graph loading & route calculation
│   ├── aqi_simulator.py  ← Simulated AQI data generator
│   ├── cost_function.py  ← Multi-objective route cost calculator
│   ├── models.py         ← SQLAlchemy database table definitions
│   ├── db.py             ← Database connection & session setup
│   └── schemas.py        ← Pydantic request/response validation models
│
├── test_api.py           ← Test script for all API endpoints
├── requirements.txt      ← Python package dependencies
├── ecoroute.db           ← SQLite database (auto-created on first run)
└── README.md             ← This file
```

---

## How to Run

### Step 1 — Create a virtual environment (recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### Step 2 — Install dependencies

```bash
pip install -r requirements.txt
```

> ⚠️ **Note:** `osmnx` installs several geospatial packages automatically (shapely, pyproj, geopandas). This may take a few minutes.

### Step 3 — Start the server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 4 — Wait for the graph to load

When the server starts, it downloads the real road network for **Madurai, India** from OpenStreetMap. This takes **30–120 seconds** on the first run. After that, OSMnx caches the data locally and subsequent starts are fast.

You'll see this in the logs when ready:
```
EcoRoute AI is ready. Visit http://localhost:8000/docs
```

### Step 5 — Open the API documentation

Visit **http://localhost:8000/docs** for the interactive Swagger UI where you can test all endpoints in your browser.

### Step 6 — Run the test script

In a second terminal:
```bash
python test_api.py
```

---

## How the Routing Algorithm Works

### 1. The Road Network Graph

We use **OSMnx** to download the real drivable road network for Madurai from OpenStreetMap. The result is a **directed graph** (NetworkX `MultiDiGraph`) where:
- **Nodes** = road intersections (each has a latitude and longitude)
- **Edges** = road segments between intersections (each has a length in metres, speed limit, road type)

### 2. Simulated AQI Values

Since we don't have physical IoT sensors, we **simulate** Air Quality Index values for every node in the graph:

- All nodes start with a **random base AQI** between 50–150 (typical urban pollution).
- Nodes within **~800 metres** of a school or hospital get a **proximity boost** — the closer to the sensitive zone, the higher the AQI boost (up to +150 extra AQI).
- A small **random jitter** (±10) is added to simulate real-world variation.

### 3. The Multi-Objective Cost Function

This is the **core innovation**. For every road segment (edge) in the graph, we calculate a single cost number:

```
cost = (w1 × travel_time_norm) + (w2 × aqi_norm) + (w3 × zone_penalty)
```

**Breaking this down:**

| Term | Formula | What it represents |
|------|---------|-------------------|
| `travel_time_norm` | `travel_time_seconds / 300` | How slow is this road? (0 = instant, 1 = very slow) |
| `aqi_norm` | `aqi_value / 350` | How polluted is this road? (0 = clean, 1 = hazardous) |
| `zone_penalty` | `1.0` if near school/hospital, else `0.0` | Is this road near a sensitive zone? |

**Default weights:**
- `w1 = 0.5` → Travel time accounts for **50%** of the cost
- `w2 = 0.3` → AQI accounts for **30%** of the cost  
- `w3 = 0.2` → Zone proximity accounts for **20%** of the cost

**Why normalise?**  
Travel time is in seconds (0–300+) and AQI is on a 0–350 scale. If we added them raw, AQI would dominate just because its numbers are bigger. Dividing each term by its maximum value brings everything to the **[0, 1] range**, so the weights w1, w2, w3 have their intended meaning.

**Example calculation for one road segment:**
```
travel_time = 120s  → travel_time_norm = 120/300 = 0.40
aqi_value   = 180   → aqi_norm         = 180/350 = 0.51
near zone?  = Yes   → zone_penalty     = 1.0

cost = 0.5×0.40 + 0.3×0.51 + 0.2×1.0
     = 0.20    + 0.153   + 0.20
     = 0.553
```

A cleaner, faster road with no zone proximity would score much lower (e.g., 0.25), so the algorithm prefers it.

### 4. Dijkstra's Shortest Path

NetworkX's `shortest_path()` with `weight="eco_cost"` runs **Dijkstra's algorithm** — it explores paths from source to destination, always expanding the currently cheapest path first, until it reaches the destination.

The result is the sequence of road intersections (nodes) that, when traversed, produce the **minimum total eco_cost** from source to destination.

### 5. Customisable Weights

You can override weights per request:
```json
{ "w1": 0.2, "w2": 0.6, "w3": 0.2 }
```
This tells the system: *"I care much more about air quality than speed."*  
The route will likely be longer but expose you to less pollution.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/get-route` | Calculate eco-optimised route |
| `GET` | `/aqi/{zone_id}` | Get current AQI for a zone |
| `GET` | `/zones` | List all sensitive zones |
| `POST` | `/sensor-data` | Submit simulated IoT sensor data |
| `GET` | `/route-history` | Get last 10 calculated routes |

---

## Example API Calls (curl)

### Health Check
```bash
curl http://localhost:8000/
```

### Get All Sensitive Zones
```bash
curl http://localhost:8000/zones
```

### Get AQI for Zone 1
```bash
curl http://localhost:8000/aqi/1
```

### Calculate an Eco Route (default weights)
```bash
curl -X POST http://localhost:8000/get-route \
     -H "Content-Type: application/json" \
     -d '{
           "source_lat": 9.9252,
           "source_lng": 78.1198,
           "dest_lat":   9.9510,
           "dest_lng":   78.0820,
           "vehicle_type": "car"
         }'
```

### Calculate a Route Prioritising Clean Air (custom weights)
```bash
curl -X POST http://localhost:8000/get-route \
     -H "Content-Type: application/json" \
     -d '{
           "source_lat": 9.9252,
           "source_lng": 78.1198,
           "dest_lat":   9.9510,
           "dest_lng":   78.0820,
           "vehicle_type": "car",
           "w1": 0.2,
           "w2": 0.6,
           "w3": 0.2
         }'
```

### Submit Simulated Sensor Data
```bash
curl -X POST http://localhost:8000/sensor-data \
     -H "Content-Type: application/json" \
     -d '{
           "zone_id":   2,
           "aqi_value": 145.7
         }'
```

### Get Route History (last 10 routes)
```bash
curl http://localhost:8000/route-history
```

---

## Database Schema

```
sensitive_zones
  id        INTEGER  PRIMARY KEY
  name      TEXT     e.g. "Madurai Government Rajaji Hospital"
  lat       FLOAT    latitude
  lng       FLOAT    longitude
  type      TEXT     "school" | "hospital"

aqi_readings
  id        INTEGER  PRIMARY KEY
  zone_id   INTEGER  FOREIGN KEY → sensitive_zones.id
  aqi_value FLOAT    AQI measurement
  timestamp DATETIME when recorded

route_logs
  id         INTEGER  PRIMARY KEY
  source     TEXT     "lat, lng" of start point
  dest       TEXT     "lat, lng" of destination
  route_json TEXT     JSON array of [lat, lng] coordinate pairs
  avg_aqi    FLOAT    average AQI exposure along route
  timestamp  DATETIME when route was calculated
```

---

## Configuration & Customisation

### Change the city
In `app/graph_engine.py`, edit:
```python
CITY_NAME = "Madurai, India"
# Change to: "Chennai, India" or "Coimbatore, India" etc.
```

### Change default cost weights
In `app/cost_function.py`, edit:
```python
DEFAULT_W1 = 0.5   # Travel time weight
DEFAULT_W2 = 0.3   # AQI weight
DEFAULT_W3 = 0.2   # Zone penalty weight
```

### Add more sensitive zones
In `app/aqi_simulator.py`, add entries to `SENSITIVE_ZONES`:
```python
{
    "id":   5,
    "name": "My New Zone",
    "lat":  9.9300,
    "lng":  78.1100,
    "type": "school",
}
```

### Integrate the ML team's LSTM model
In `app/aqi_simulator.py`, find `get_predicted_aqi()` and replace the placeholder body with the ML service call.

---

## Technologies Used

| Technology | Version | Purpose |
|-----------|---------|---------|
| FastAPI | 0.111.0 | Web framework & API |
| Uvicorn | 0.29.0 | ASGI server |
| SQLAlchemy | 2.0.30 | Database ORM |
| OSMnx | 1.9.3 | OpenStreetMap road network download |
| NetworkX | 3.3 | Graph algorithms (Dijkstra) |
| Pydantic | 2.7.1 | Request/response validation |
| SQLite | built-in | Database storage |