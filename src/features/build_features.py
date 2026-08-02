from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "configs" / "config.yaml"


def load_config() -> dict:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["is_rush_hour"] = (
        ((out["pickup_hour"] >= 8) & (out["pickup_hour"] <= 10))
        | ((out["pickup_hour"] >= 17) & (out["pickup_hour"] <= 20))
    ).astype(int)
    out["is_night"] = ((out["pickup_hour"] >= 22) | (out["pickup_hour"] <= 5)).astype(int)
    out["same_zone"] = (out["pickup_zone"] == out["dropoff_zone"]).astype(int)
    out["weather_rainy"] = (out["weather"] == "Rainy").astype(int)
    out["traffic_high"] = (out["traffic_level"] == "High").astype(int)
    out["traffic_medium"] = (out["traffic_level"] == "Medium").astype(int)
    return out


def main() -> None:
    cfg = load_config()
    raw_path = ROOT / cfg["data"]["raw_path"]
    processed_path = ROOT / cfg["data"]["processed_path"]
    processed_path.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(raw_path)
    featured = build_features(df)
    featured.to_csv(processed_path, index=False)
    print(f"Wrote features -> {processed_path} ({featured.shape[0]} rows, {featured.shape[1]} cols)")


if __name__ == "__main__":
    main()
