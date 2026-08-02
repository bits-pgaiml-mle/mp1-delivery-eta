import shutil
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
VERSIONS = ROOT / "data" / "versions"
SOURCES = ("synthetic", "kaggle", "both")


def run_prepare(source: str) -> None:
    result = subprocess.run(
        [sys.executable, "data/prepare_dataset.py", "--source", source],
        cwd=ROOT,
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def snapshot_one(source: str) -> None:
    run_prepare(source)
    dest = VERSIONS / source
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / "data" / "raw" / "trips.csv", dest / "trips.csv")
    print(f"Snapshot -> {dest / 'trips.csv'}")


def main() -> None:
    VERSIONS.mkdir(parents=True, exist_ok=True)
    for source in SOURCES:
        snapshot_one(source)
    with open(ROOT / "configs" / "data_source.yaml", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    active = (cfg.get("data_source") or "synthetic").lower().strip()
    if active not in SOURCES:
        active = "synthetic"
    run_prepare(active)
    print(f"Active data/raw restored from source={active}")
    print(f"All version snapshots under {VERSIONS}")


if __name__ == "__main__":
    main()
