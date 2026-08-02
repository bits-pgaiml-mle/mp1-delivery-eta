import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TRAIN_DB = ROOT / "feature_store" / "feature_store.db"
PROD_DB = ROOT / "monitoring" / "predictions.db"
REPORT = ROOT / "reports" / "drift_report.md"
SHIFT_THRESHOLD = 0.8


def main() -> None:
    train = pd.read_sql("SELECT * FROM trip_features", sqlite3.connect(TRAIN_DB))
    if not PROD_DB.exists():
        print("No production predictions yet. Call /predict first.")
        return
    prod = pd.read_sql("SELECT * FROM predictions", sqlite3.connect(PROD_DB))
    if prod.empty:
        print("Prediction log is empty.")
        return

    print(f"Training: {len(train)} trips | Production: {len(prod)} predictions")
    lines = [
        "# Drift Simulation Report",
        "",
        f"Training rows: {len(train)}",
        f"Production predictions: {len(prod)}",
        "",
        "| Feature | Train mean | Prod mean | Shift (σ) | Status |",
        "|---------|------------|-----------|-----------|--------|",
    ]

    for feat in ["distance_km", "pickup_hour", "passenger_count"]:
        if feat not in prod.columns or feat not in train.columns:
            continue
        t_mean, t_std = train[feat].mean(), train[feat].std()
        p_mean = prod[feat].mean()
        shift = abs(p_mean - t_mean) / (t_std + 1e-9)
        flag = "DRIFTED" if shift > SHIFT_THRESHOLD else "OK"
        print(f"{feat:22s} train={t_mean:6.2f} prod={p_mean:6.2f} shift={shift:.2f} sigma  {flag}")
        lines.append(f"| {feat} | {t_mean:.2f} | {p_mean:.2f} | {shift:.2f} | {flag} |")

    rainy_train = (train.filter(like="weather_Rainy").sum(axis=1) > 0).mean() if any(
        c.startswith("weather_") for c in train.columns
    ) else float("nan")
    rainy_prod = (prod["weather"] == "Rainy").mean()
    print(f"{'weather_Rainy_share':22s} train={rainy_train:6.2f} prod={rainy_prod:6.2f}")
    lines.extend(
        [
            "",
            f"Rainy share train≈{rainy_train:.2%} prod={rainy_prod:.2%}",
            "",
            "## Retraining trigger (design)",
            f"- Retrain when any numeric feature shift > {SHIFT_THRESHOLD}σ **and** ≥200 production labels are available.",
            "- Also retrain when rolling MAE vs actual ETA exceeds threshold in config/selection review.",
        ]
    )
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {REPORT}")


if __name__ == "__main__":
    main()
