import json
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "trips.csv"
FEATURE_DB = ROOT / "feature_store" / "feature_store.db"
SCHEMA_PATH = ROOT / "data" / "feature_schema.json"
TABLE = "trip_features"
TARGET = "eta_minutes"
DROP_COLS = ["trip_id"]
CATEGORICAL = ["weather", "traffic_level"]


def engineer(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["is_rush_hour"] = (
        ((out["pickup_hour"] >= 8) & (out["pickup_hour"] <= 10))
        | ((out["pickup_hour"] >= 17) & (out["pickup_hour"] <= 20))
    ).astype(int)
    out["same_zone"] = (out["pickup_zone"] == out["dropoff_zone"]).astype(int)
    out = out.drop(columns=["pickup_zone", "dropoff_zone"], errors="ignore")
    out = out.drop(columns=[c for c in DROP_COLS if c in out.columns], errors="ignore")
    return out


def encode_features(df: pd.DataFrame, schema: list[str] | None = None) -> pd.DataFrame:
    featured = engineer(df)
    has_target = TARGET in featured.columns
    y = featured[TARGET] if has_target else None
    x = featured.drop(columns=[TARGET]) if has_target else featured

    x_encoded = pd.get_dummies(x, columns=[c for c in CATEGORICAL if c in x.columns], drop_first=True)

    if schema is None:
        return (x_encoded, y) if has_target else x_encoded

    aligned = pd.DataFrame(0, index=x_encoded.index, columns=schema, dtype=float)
    for col in x_encoded.columns:
        if col in aligned.columns:
            aligned[col] = x_encoded[col].astype(float).values
    return (aligned, y) if has_target else aligned


def transform_raw_record(raw: dict, schema: list[str]) -> list[float]:
    frame = pd.DataFrame([raw])
    encoded = encode_features(frame, schema=schema)
    return encoded.iloc[0].tolist()


def main() -> None:
    df = pd.read_csv(RAW_PATH)
    x_encoded, y = encode_features(df)

    feature_df = x_encoded.copy()
    feature_df[TARGET] = y.values

    FEATURE_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(FEATURE_DB)
    feature_df.to_sql(TABLE, conn, if_exists="replace", index=False)
    conn.close()

    schema = list(x_encoded.columns)
    SCHEMA_PATH.parent.mkdir(parents=True, exist_ok=True)
    SCHEMA_PATH.write_text(json.dumps(schema, indent=2), encoding="utf-8")

    print(f"Feature store: {len(feature_df)} rows | {len(schema)} features")
    print(f"DB: {FEATURE_DB}")
    print(f"Schema: {schema}")


if __name__ == "__main__":
    main()
