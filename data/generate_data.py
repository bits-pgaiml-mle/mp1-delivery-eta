from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "trips.csv"
N = 2000
SEED = 42


def generate_trips(n: int = N, seed: int = SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    distance_km = np.round(rng.uniform(0.5, 25.0, n), 2)
    pickup_hour = rng.integers(0, 24, n)
    is_weekend = rng.integers(0, 2, n)
    passenger_count = rng.integers(1, 5, n)
    weather = rng.choice(["Clear", "Rainy", "Cloudy"], n, p=[0.60, 0.20, 0.20])
    traffic_level = rng.choice(["Low", "Medium", "High"], n, p=[0.35, 0.40, 0.25])
    pickup_zone = rng.choice([f"Z{i:02d}" for i in range(1, 11)], n)
    dropoff_zone = rng.choice([f"Z{i:02d}" for i in range(1, 11)], n)

    traffic_factor = np.where(
        traffic_level == "High", 1.35, np.where(traffic_level == "Medium", 1.15, 1.0)
    )
    weather_factor = np.where(weather == "Rainy", 1.25, np.where(weather == "Cloudy", 1.08, 1.0))
    rush_factor = np.where(
        ((pickup_hour >= 8) & (pickup_hour <= 10)) | ((pickup_hour >= 17) & (pickup_hour <= 20)),
        1.20,
        1.0,
    )
    weekend_factor = np.where(is_weekend == 1, 1.10, 1.0)

    base_minutes = 5.0 + 2.8 * distance_km
    eta_minutes = (
        base_minutes * traffic_factor * weather_factor * rush_factor * weekend_factor
        + rng.normal(0, 3.0, n)
    )
    eta_minutes = np.clip(np.round(eta_minutes, 1), 3.0, 120.0)

    return pd.DataFrame(
        {
            "trip_id": [f"T{i:06d}" for i in range(n)],
            "distance_km": distance_km,
            "pickup_hour": pickup_hour,
            "is_weekend": is_weekend,
            "passenger_count": passenger_count,
            "weather": weather,
            "traffic_level": traffic_level,
            "pickup_zone": pickup_zone,
            "dropoff_zone": dropoff_zone,
            "eta_minutes": eta_minutes,
        }
    )


def main() -> None:
    RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
    df = generate_trips()
    df.to_csv(RAW_PATH, index=False)
    print(f"Wrote {len(df)} trips -> {RAW_PATH}")
    print(f"ETA mean={df['eta_minutes'].mean():.1f} std={df['eta_minutes'].std():.1f}")


if __name__ == "__main__":
    main()
