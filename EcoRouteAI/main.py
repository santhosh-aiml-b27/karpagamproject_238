"""
EcoRoute AI - Main FastAPI Entry Point
"""

from fastapi import FastAPI

app = FastAPI(
    title="EcoRoute AI API",
    description="Dynamic Eco-Health Traffic Signal & AQI Prediction API",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "Welcome to EcoRoute AI API. Model status: Initialized."}
