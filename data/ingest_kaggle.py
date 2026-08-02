import math
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "data" / "external" / "kaggle"
OUT_PATH = EXTERNAL / "trips_from_kaggle.csv"
DEFAULT_INPUT = EXTERNAL / "nyc_taxi_sample.csv"


def haversine_km(lon1, lat1, lon2, lat2):
    r = 6371.0
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0) ** 2
    return 2 * r * np.arcsin(np.sqrt(a))


def zone_from_coords(lat, lon) -> str:
    return f"Z{int((abs(lat) * 10 + abs(lon) * 10) % 10) + 1:02d}"


def adapt_nyc_taxi(df: pd.DataFrame, max_rows: int, seed: int = 42) -> pd.DataFrame:
    need = [
        "pickup_datetime",
        "passenger_count",
        "pickup_longitude",
        "pickup_latitude",
        "dropoff_longitude",
        "dropoff_latitude",
        "trip_duration",
    ]
    missing = [c for c in need if c not in df.columns]
    if missing:
        raise ValueError(f"NYC taxi CSV missing columns: {missing}")

    df = df.dropna(subset=need).copy()
    if len(df) > max_rows:
        df = df.sample(n=max_rows, random_state=seed)

    pickup = pd.to_datetime(df["pickup_datetime"], errors="coerce")
    df = df.loc[pickup.notna()].copy()
    pickup = pickup.loc[df.index]

    distance_km = haversine_km(
        df["pickup_longitude"].to_numpy(),
        df["pickup_latitude"].to_numpy(),
        df["dropoff_longitude"].to_numpy(),
        df["dropoff_latitude"].to_numpy(),
    )
    distance_km = np.clip(np.round(distance_km, 2), 0.1, 100.0)

    pickup_hour = pickup.dt.hour.to_numpy()
    is_weekend = (pickup.dt.dayofweek >= 5).astype(int).to_numpy()
    passenger_count = df["passenger_count"].clip(1, 8).astype(int).to_numpy()
    eta_minutes = np.clip(np.round(df["trip_duration"].to_numpy() / 60.0, 1), 1.0, 180.0)

    rng = np.random.default_rng(seed)
    weather = rng.choice(["Clear", "Rainy", "Cloudy"], len(df), p=[0.6, 0.2, 0.2])
    traffic_level = np.where(
        ((pickup_hour >= 7) & (pickup_hour <= 10)) | ((pickup_hour >= 16) & (pickup_hour <= 19)),
        "High",
        np.where((pickup_hour >= 11) & (pickup_hour <= 15), "Medium", "Low"),
    )

    pickup_zone = [
        zone_from_coords(a, b)
        for a, b in zip(df["pickup_latitude"].to_numpy(), df["pickup_longitude"].to_numpy())
    ]
    dropoff_zone = [
        zone_from_coords(a, b)
        for a, b in zip(df["dropoff_latitude"].to_numpy(), df["dropoff_longitude"].to_numpy())
    ]

    out = pd.DataFrame(
        {
            "trip_id": [f"K{i:06d}" for i in range(len(df))],
            "distance_km": distance_km,
            "pickup_hour": pickup_hour,
            "is_weekend": is_weekend,
            "passenger_count": passenger_count,
            "weather": weather,
            "traffic_level": traffic_level,
            "pickup_zone": pickup_zone,
            "dropoff_zone": dropoff_zone,
            "eta_minutes": eta_minutes,
            "data_source": "kaggle",
        }
    )
    return out.reset_index(drop=True)


def load_or_create_sample(path: Path) -> pd.DataFrame:
    if path.exists():
        return pd.read_csv(path)

    EXTERNAL.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(7)
    n = 200
    pickup_lon = rng.uniform(-74.05, -73.75, n)
    pickup_lat = rng.uniform(40.60, 40.90, n)
    drop_lon = pickup_lon + rng.uniform(-0.05, 0.05, n)
    drop_lat = pickup_lat + rng.uniform(-0.05, 0.05, n)
    duration = rng.integers(120, 3600, n)
    days = pd.to_datetime("2016-01-01") + pd.to_timedelta(rng.integers(0, 60, n), unit="D")
    hours = rng.integers(0, 24, n)
    pickup_dt = days + pd.to_timedelta(hours, unit="h")

    sample = pd.DataFrame(
        {
            "id": [f"id{i}" for i in range(n)],
            "vendor_id": 1,
            "pickup_datetime": pickup_dt.astype(str),
            "dropoff_datetime": (pickup_dt + pd.to_timedelta(duration, unit="s")).astype(str),
            "passenger_count": rng.integers(1, 5, n),
            "pickup_longitude": pickup_lon,
            "pickup_latitude": pickup_lat,
            "dropoff_longitude": drop_lon,
            "dropoff_latitude": drop_lat,
            "store_and_fwd_flag": "N",
            "trip_duration": duration,
        }
    )
    sample.to_csv(path, index=False)
    print(f"Created demo NYC-like sample at {path} (replace with real Kaggle train.csv for production use)")
    return sample


def main(max_rows: int = 5000, input_csv: Path | None = None) -> Path:
    input_csv = input_csv or DEFAULT_INPUT
    EXTERNAL.mkdir(parents=True, exist_ok=True)
    raw = load_or_create_sample(input_csv)
    adapted = adapt_nyc_taxi(raw, max_rows=max_rows)
    adapted.to_csv(OUT_PATH, index=False)
    print(f"Wrote Kaggle-adapted trips -> {OUT_PATH} ({len(adapted)} rows)")
    return OUT_PATH


if __name__ == "__main__":
    main()
