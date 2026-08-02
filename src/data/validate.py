import sys
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "configs" / "config.yaml"

REQUIRED_COLUMNS = [
    "trip_id",
    "distance_km",
    "pickup_hour",
    "is_weekend",
    "passenger_count",
    "weather",
    "traffic_level",
    "pickup_zone",
    "dropoff_zone",
    "eta_minutes",
]

ALLOWED_WEATHER = {"Clear", "Rainy", "Cloudy"}
ALLOWED_TRAFFIC = {"Low", "Medium", "High"}


def load_config() -> dict:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def validate(df: pd.DataFrame) -> list[str]:
    errors: list[str] = []

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        errors.append(f"Missing columns: {missing}")
        return errors

    if df["trip_id"].duplicated().any():
        errors.append("trip_id has duplicates")

    if df.isna().any().any():
        errors.append(f"Null values found: {df.isna().sum()[df.isna().sum() > 0].to_dict()}")

    if not df["distance_km"].between(0, 100).all():
        errors.append("distance_km outside [0, 100]")

    if not df["pickup_hour"].between(0, 23).all():
        errors.append("pickup_hour outside [0, 23]")

    if not df["is_weekend"].isin([0, 1]).all():
        errors.append("is_weekend must be 0 or 1")

    if not df["passenger_count"].between(1, 8).all():
        errors.append("passenger_count outside [1, 8]")

    bad_weather = set(df["weather"].unique()) - ALLOWED_WEATHER
    if bad_weather:
        errors.append(f"Unexpected weather values: {bad_weather}")

    bad_traffic = set(df["traffic_level"].unique()) - ALLOWED_TRAFFIC
    if bad_traffic:
        errors.append(f"Unexpected traffic_level values: {bad_traffic}")

    if not df["eta_minutes"].between(1, 180).all():
        errors.append("eta_minutes outside [1, 180]")

    if (df["pickup_zone"] == df["dropoff_zone"]).mean() > 0.95:
        errors.append("pickup_zone and dropoff_zone are nearly identical")

    return errors


def main() -> None:
    cfg = load_config()
    path = ROOT / cfg["data"]["raw_path"]
    if not path.exists():
        print(f"Raw data not found: {path}")
        print("Run: python -m src.data.generate")
        sys.exit(1)

    df = pd.read_csv(path)
    errors = validate(df)
    if errors:
        print("Validation FAILED:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    print(f"Validation PASSED: {len(df)} rows, {len(df.columns)} columns")
    print(df.describe(include="all").transpose().head(10).to_string())


if __name__ == "__main__":
    main()
