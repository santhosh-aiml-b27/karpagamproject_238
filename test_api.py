"""
test_api.py - API Test Script
===============================
Run this script AFTER starting the server to verify all endpoints work correctly.

PRE-REQUISITES:
  1. Server must be running:
       uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
  2. Install requests if not already installed:
       pip install requests

USAGE:
  python test_api.py

This script tests all 5 endpoints and prints the results.
Each test includes both the Python requests call and the equivalent curl command
so you can reference either style in your presentation.
"""

import json
import time
import requests

BASE_URL = "http://localhost:8000"

# ANSI colour codes for terminal output
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
RESET  = "\033[0m"
BOLD   = "\033[1m"


def separator(title: str):
    print(f"\n{CYAN}{'═' * 60}{RESET}")
    print(f"{BOLD}{CYAN}  {title}{RESET}")
    print(f"{CYAN}{'═' * 60}{RESET}")


def print_result(response, label: str):
    if response.status_code in (200, 201):
        print(f"{GREEN}✓ {label} — HTTP {response.status_code}{RESET}")
    else:
        print(f"{RED}✗ {label} — HTTP {response.status_code}{RESET}")
    print(json.dumps(response.json(), indent=2, default=str)[:800])   # Truncate long output


# ─────────────────────────────────────────────────────────────────────────────
#  TEST 0: Health Check
# ─────────────────────────────────────────────────────────────────────────────

def test_health_check():
    separator("TEST 0: Health Check  GET /")
    print(f"{YELLOW}curl command:{RESET}")
    print("  curl http://localhost:8000/\n")

    r = requests.get(f"{BASE_URL}/")
    print_result(r, "Health Check")

    graph_loaded = r.json().get("graph_loaded", False)
    if not graph_loaded:
        print(f"\n{YELLOW}⚠  Graph is still loading. Route tests may fail.{RESET}")
        print(f"{YELLOW}   Wait 60–120 seconds after server start and re-run.{RESET}")
    return graph_loaded


# ─────────────────────────────────────────────────────────────────────────────
#  TEST 1: GET /zones
# ─────────────────────────────────────────────────────────────────────────────

def test_get_zones():
    separator("TEST 1: Get All Sensitive Zones  GET /zones")
    print(f"{YELLOW}curl command:{RESET}")
    print("  curl http://localhost:8000/zones\n")

    r = requests.get(f"{BASE_URL}/zones")
    print_result(r, "Get Zones")


# ─────────────────────────────────────────────────────────────────────────────
#  TEST 2: GET /aqi/{zone_id}
# ─────────────────────────────────────────────────────────────────────────────

def test_get_aqi():
    separator("TEST 2: Get AQI for Zone 1  GET /aqi/1")
    print(f"{YELLOW}curl command:{RESET}")
    print("  curl http://localhost:8000/aqi/1\n")

    r = requests.get(f"{BASE_URL}/aqi/1")
    print_result(r, "Get AQI Zone 1")

    # Also test an invalid zone ID
    print(f"\n{YELLOW}Testing invalid zone ID (should return 404):{RESET}")
    print("  curl http://localhost:8000/aqi/99\n")
    r_invalid = requests.get(f"{BASE_URL}/aqi/99")
    print_result(r_invalid, "Get AQI Zone 99 (invalid)")


# ─────────────────────────────────────────────────────────────────────────────
#  TEST 3: POST /sensor-data
# ─────────────────────────────────────────────────────────────────────────────

def test_sensor_data():
    separator("TEST 3: Submit Sensor Data  POST /sensor-data")
    payload = {"zone_id": 2, "aqi_value": 145.7}

    print(f"{YELLOW}curl command:{RESET}")
    print(
        "  curl -X POST http://localhost:8000/sensor-data \\\n"
        '       -H "Content-Type: application/json" \\\n'
        f"       -d '{json.dumps(payload)}'\n"
    )

    r = requests.post(f"{BASE_URL}/sensor-data", json=payload)
    print_result(r, "Submit Sensor Data")

    # Test with a different zone
    payload2 = {"zone_id": 3, "aqi_value": 212.3}
    r2 = requests.post(f"{BASE_URL}/sensor-data", json=payload2)
    print(f"\n{YELLOW}Submitting a second reading (zone 3):{RESET}")
    print_result(r2, "Submit Sensor Data Zone 3")


# ─────────────────────────────────────────────────────────────────────────────
#  TEST 4: POST /get-route (with default weights)
# ─────────────────────────────────────────────────────────────────────────────

def test_get_route_default(graph_loaded: bool):
    separator("TEST 4: Get Eco Route (Default Weights)  POST /get-route")

    payload = {
        "source_lat":   9.9252,
        "source_lng":   78.1198,
        "dest_lat":     9.9510,
        "dest_lng":     78.0820,
        "vehicle_type": "car",
    }

    print(f"{YELLOW}curl command:{RESET}")
    print(
        "  curl -X POST http://localhost:8000/get-route \\\n"
        '       -H "Content-Type: application/json" \\\n'
        f"       -d '{json.dumps(payload)}'\n"
    )

    if not graph_loaded:
        print(f"{YELLOW}⚠  Skipping route test — graph not loaded yet.{RESET}")
        return

    r = requests.post(f"{BASE_URL}/get-route", json=payload)
    data = r.json()

    if r.status_code == 200:
        print(f"{GREEN}✓ Get Route — HTTP 200{RESET}")
        print(f"  • Route nodes     : {len(data['route'])} coordinate pairs")
        print(f"  • Total distance  : {data['total_distance']} m")
        print(f"  • Estimated time  : {data['estimated_time']} min")
        print(f"  • Avg AQI exposure: {data['avg_aqi_exposure']}")
        print(f"  • Zones avoided   : {data['zones_avoided']}")
        print(f"\n  First 3 coordinates: {data['route'][:3]}")
    else:
        print_result(r, "Get Route")


# ─────────────────────────────────────────────────────────────────────────────
#  TEST 5: POST /get-route (with custom weights — prioritise AQI)
# ─────────────────────────────────────────────────────────────────────────────

def test_get_route_custom_weights(graph_loaded: bool):
    separator("TEST 5: Get Eco Route (AQI-Priority Weights)  POST /get-route")

    payload = {
        "source_lat":   9.9252,
        "source_lng":   78.1198,
        "dest_lat":     9.9510,
        "dest_lng":     78.0820,
        "vehicle_type": "car",
        "w1": 0.2,   # Less weight on travel time
        "w2": 0.6,   # High weight on AQI (prioritise clean air)
        "w3": 0.2,   # Normal weight on zone avoidance
    }

    print(f"{YELLOW}curl command:{RESET}")
    print(
        "  curl -X POST http://localhost:8000/get-route \\\n"
        '       -H "Content-Type: application/json" \\\n'
        f"       -d '{json.dumps(payload)}'\n"
    )

    if not graph_loaded:
        print(f"{YELLOW}⚠  Skipping route test — graph not loaded yet.{RESET}")
        return

    r = requests.post(f"{BASE_URL}/get-route", json=payload)
    data = r.json()

    if r.status_code == 200:
        print(f"{GREEN}✓ Get Route (AQI Priority) — HTTP 200{RESET}")
        print(f"  • Total distance  : {data['total_distance']} m")
        print(f"  • Avg AQI exposure: {data['avg_aqi_exposure']}  (should be lower than default route)")
        print(f"  • Zones avoided   : {data['zones_avoided']}")
    else:
        print_result(r, "Get Route Custom Weights")


# ─────────────────────────────────────────────────────────────────────────────
#  TEST 6: GET /route-history
# ─────────────────────────────────────────────────────────────────────────────

def test_route_history():
    separator("TEST 6: Get Route History  GET /route-history")
    print(f"{YELLOW}curl command:{RESET}")
    print("  curl http://localhost:8000/route-history\n")

    r = requests.get(f"{BASE_URL}/route-history")
    data = r.json()

    if r.status_code == 200:
        print(f"{GREEN}✓ Route History — HTTP 200{RESET}")
        print(f"  • Returned {len(data)} route log(s).")
        if data:
            print(f"  • Most recent: {data[0]}")
    else:
        print_result(r, "Route History")


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"\n{BOLD}EcoRoute AI — API Test Suite{RESET}")
    print(f"Testing server at: {BASE_URL}")
    print("Make sure the server is running before executing this script.\n")

    # Wait briefly to give the server a moment to respond
    time.sleep(1)

    try:
        graph_loaded = test_health_check()
        test_get_zones()
        test_get_aqi()
        test_sensor_data()
        test_get_route_default(graph_loaded)
        test_get_route_custom_weights(graph_loaded)
        test_route_history()

        separator("ALL TESTS COMPLETE")
        print(f"{GREEN}Test suite finished. Check output above for any errors.{RESET}\n")

    except requests.exceptions.ConnectionError:
        print(f"\n{RED}ERROR: Could not connect to {BASE_URL}{RESET}")
        print("Make sure the server is running:")
        print("  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000\n")
