# EcoRoute AI – Dynamic Eco-Health Traffic Signal & Routing System

EcoRoute AI is a machine learning system designed to predict Air Quality Index (AQI) 15 to 30 minutes in advance using historical time-series air quality and traffic data.

## Project Structure

```text
EcoRouteAI/
│
├── data/
│   ├── raw/           # Raw downloaded dataset files
│   └── processed/     # Cleaned and processed feature datasets
├── notebooks/         # Jupyter notebooks for EDA and experimentation
├── models/            # Saved model architectures and training scripts
├── api/               # FastAPI endpoint logic and schemas
├── utils/             # Utility modules (data loading, evaluation metrics)
├── saved_model/       # Trained model artifacts and scalers
├── requirements.txt   # Python dependencies
├── main.py            # FastAPI entry point
└── README.md          # Documentation
```

## Setup & Execution

1. Create a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run API:
   ```bash
   uvicorn main:app --reload
   ```
