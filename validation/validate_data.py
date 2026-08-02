import sys
from pathlib import Path

import pandas as pd
import pandera.pandas as pa
from pandera.pandas import Check, Column, DataFrameSchema

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "trips.csv"

SCHEMA = DataFrameSchema(
    {
        "trip_id": Column(str, unique=True, nullable=False),
        "distance_km": Column(float, Check.in_range(0, 100), nullable=False),
        "pickup_hour": Column(int, Check.in_range(0, 23), nullable=False),
        "is_weekend": Column(int, Check.isin([0, 1]), nullable=False),
        "passenger_count": Column(int, Check.in_range(1, 8), nullable=False),
        "weather": Column(str, Check.isin(["Clear", "Rainy", "Cloudy"]), nullable=False),
        "traffic_level": Column(str, Check.isin(["Low", "Medium", "High"]), nullable=False),
        "pickup_zone": Column(str, nullable=False),
        "dropoff_zone": Column(str, nullable=False),
        "eta_minutes": Column(float, Check.in_range(1, 180), nullable=False),
    },
    coerce=True,
    strict=True,
)


def statistical_checks(df: pd.DataFrame) -> list[str]:
    errors: list[str] = []
    if df["eta_minutes"].mean() < 5 or df["eta_minutes"].mean() > 100:
        errors.append(f"eta_minutes mean out of expected band: {df['eta_minutes'].mean():.2f}")
    if df["distance_km"].std() < 0.5:
        errors.append("distance_km variance too low (possible constant column)")
    if (df["pickup_zone"] == df["dropoff_zone"]).mean() > 0.95:
        errors.append("pickup_zone and dropoff_zone nearly identical")
    rain_share = (df["weather"] == "Rainy").mean()
    if rain_share < 0.05 or rain_share > 0.60:
        errors.append(f"weather Rainy share unexpected: {rain_share:.2%}")
    return errors


def validate(df: pd.DataFrame) -> pd.DataFrame:
    validated = SCHEMA.validate(df, lazy=True)
    stats_errors = statistical_checks(validated)
    if stats_errors:
        raise ValueError("Statistical validation failed: " + "; ".join(stats_errors))
    return validated


def main() -> None:
    if not RAW_PATH.exists():
        print(f"Raw data missing: {RAW_PATH}")
        print("Run: python data/generate_data.py")
        sys.exit(1)

    df = pd.read_csv(RAW_PATH)
    try:
        validated = validate(df)
    except Exception as exc:
        print("Validation FAILED")
        print(exc)
        sys.exit(1)

    print(f"PASS: {len(validated)} trips validated — schema + statistical checks passed")


if __name__ == "__main__":
    main()
