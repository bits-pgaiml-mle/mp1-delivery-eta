import argparse
import shutil
from pathlib import Path

import pandas as pd
import yaml

from generate_data import generate_trips
from ingest_kaggle import main as ingest_kaggle_main

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "configs" / "data_source.yaml"
RAW_PATH = ROOT / "data" / "raw" / "trips.csv"
SYN_EXT = ROOT / "data" / "external" / "synthetic" / "trips.csv"
KAG_EXT = ROOT / "data" / "external" / "kaggle" / "trips_from_kaggle.csv"


def load_config() -> dict:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def write_synthetic(n: int, seed: int, path: Path) -> pd.DataFrame:
    df = generate_trips(n=n, seed=seed)
    df["data_source"] = "synthetic"
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return df


def prepare(source: str | None = None) -> Path:
    cfg = load_config()
    source = (source or cfg.get("data_source") or "synthetic").lower().strip()
    RAW_PATH.parent.mkdir(parents=True, exist_ok=True)

    if source == "synthetic":
        n = int(cfg.get("synthetic", {}).get("n_rows", 2000))
        seed = int(cfg.get("synthetic", {}).get("seed", 42))
        df = write_synthetic(n, seed, SYN_EXT)
        shutil.copy(SYN_EXT, RAW_PATH)

    elif source == "kaggle":
        max_rows = int(cfg.get("kaggle", {}).get("max_rows", 5000))
        local_csv = ROOT / cfg.get("kaggle", {}).get("local_csv", "data/external/kaggle/nyc_taxi_sample.csv")
        ingest_kaggle_main(max_rows=max_rows, input_csv=local_csv)
        df = pd.read_csv(KAG_EXT)
        df.to_csv(RAW_PATH, index=False)

    elif source == "both":
        syn_n = int(cfg.get("both", {}).get("synthetic_rows", 1000))
        kag_n = int(cfg.get("both", {}).get("kaggle_rows", 2000))
        seed = int(cfg.get("synthetic", {}).get("seed", 42))
        syn = write_synthetic(syn_n, seed, SYN_EXT)
        local_csv = ROOT / cfg.get("kaggle", {}).get("local_csv", "data/external/kaggle/nyc_taxi_sample.csv")
        ingest_kaggle_main(max_rows=kag_n, input_csv=local_csv)
        kag = pd.read_csv(KAG_EXT)
        df = pd.concat([syn, kag], ignore_index=True)
        df["trip_id"] = [f"M{i:06d}" for i in range(len(df))]
        df.to_csv(RAW_PATH, index=False)
        SYN_EXT.parent.mkdir(parents=True, exist_ok=True)
    else:
        raise ValueError("data_source must be one of: synthetic, kaggle, both")

    print(f"Prepared source={source} -> {RAW_PATH} ({len(df)} rows)")
    print(df["data_source"].value_counts().to_string())
    return RAW_PATH


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare Flavor A dataset from synthetic and/or Kaggle")
    parser.add_argument(
        "--source",
        choices=["synthetic", "kaggle", "both"],
        default=None,
        help="Override configs/data_source.yaml",
    )
    args = parser.parse_args()
    prepare(args.source)


if __name__ == "__main__":
    main()
