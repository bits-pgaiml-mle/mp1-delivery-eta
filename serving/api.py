import json
from pathlib import Path
from typing import Literal

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, Field

from features.build_features import transform_raw_record
from monitoring.logger import init, log

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "model_store" / "best_model.joblib"
SCHEMA_PATH = ROOT / "data" / "feature_schema.json"
SELECTION_PATH = ROOT / "model_store" / "selection.json"

app = FastAPI(title="Delivery ETA Prediction API", version="1.0")

init()

model = joblib.load(MODEL_PATH) if MODEL_PATH.exists() else None
SCHEMA: list[str] = json.loads(SCHEMA_PATH.read_text(encoding="utf-8")) if SCHEMA_PATH.exists() else []
VERSION = "eta-v1"
if SELECTION_PATH.exists():
    VERSION = json.loads(SELECTION_PATH.read_text(encoding="utf-8")).get("model_version", VERSION)


class TripRequest(BaseModel):
    distance_km: float = Field(..., gt=0, le=100)
    pickup_hour: int = Field(..., ge=0, le=23)
    is_weekend: int = Field(..., ge=0, le=1)
    passenger_count: int = Field(..., ge=1, le=8)
    weather: Literal["Clear", "Rainy", "Cloudy"]
    traffic_level: Literal["Low", "Medium", "High"]
    pickup_zone: str = Field(..., min_length=1)
    dropoff_zone: str = Field(..., min_length=1)


class TripResponse(BaseModel):
    eta_minutes: float
    model_version: str


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "model_loaded": model is not None,
        "model_version": VERSION,
        "n_features": len(SCHEMA),
    }


@app.post("/predict", response_model=TripResponse)
def predict(data: TripRequest) -> TripResponse:
    if model is None or not SCHEMA:
        raise RuntimeError("Model/schema not loaded. Run training first.")

    raw = data.model_dump()
    vector = transform_raw_record(raw, SCHEMA)
    x_df = pd.DataFrame([vector], columns=SCHEMA)
    eta = round(float(model.predict(x_df)[0]), 2)
    result = {"eta_minutes": eta, "model_version": VERSION}
    log(raw, result)
    return TripResponse(**result)
