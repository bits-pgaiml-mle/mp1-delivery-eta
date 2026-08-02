from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(
    title="Delivery ETA Service",
    description="PCAM ZC412 Mini-Project-1 Flavor A — ETA prediction API",
    version="0.1.0",
)


class TripRequest(BaseModel):
    distance_km: float = Field(..., gt=0, le=100)
    pickup_hour: int = Field(..., ge=0, le=23)
    is_weekend: int = Field(..., ge=0, le=1)
    passenger_count: int = Field(..., ge=1, le=8)
    weather: str
    traffic_level: str
    pickup_zone: str
    dropoff_zone: str


class TripResponse(BaseModel):
    eta_minutes: float
    model_version: str


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "delivery-eta", "model_loaded": False}


@app.post("/predict", response_model=TripResponse)
def predict(payload: TripRequest) -> TripResponse:
    raise NotImplementedError("Week 3: load best_model.joblib and return predicted ETA")
