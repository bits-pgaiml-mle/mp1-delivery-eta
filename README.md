# mp1-delivery-eta

**BITS Pilani WILP · PGAIML · PCAM ZC412 Machine Learning Engineering**  
**Mini-Project-1 · Flavor A — Delivery / Ride ETA Prediction**

Aligned with Taxila **QuickBite** tutorial + **M2 ELS Reliable Data Pipelines** patterns, adapted for ETA regression (Flavor A brief).

## Progress

See **[reports/PROGRESS.md](reports/PROGRESS.md)** for:

- What is completed till now
- What is **pending for Week 1 / M2** (dataset DVC versioning + team/spreadsheet items)
- Later-week and submission leftovers (report + video)

## Architecture (Taxila-style)

```text
data/raw/trips.csv  (immutable raw)
        |
        v
validation/validate_data.py   (Pandera schema + statistical checks)
        |
        v
features/build_features.py    (shared encoding -> SQLite feature store)
        |                         + data/feature_schema.json contract
        v
training/train.py             (MLflow: LinearRegression vs HistGradientBoosting)
        |
        v
serving/api.py                (FastAPI + Pydantic + shared transform)
        |
        v
monitoring/logger.py          (prediction SQLite log)
monitoring/check_drift.py     (train vs prod shift in σ)
```

## Layout

```text
mp1-delivery-eta/
├── data/generate_data.py
├── data/raw/
├── validation/validate_data.py
├── features/build_features.py
├── feature_store/feature_store.db
├── training/train.py
├── serving/api.py
├── monitoring/logger.py
├── monitoring/check_drift.py
├── monitoring/simulate_drift_traffic.py
├── model_store/
├── scripts/run_m2_pipeline.py
├── scripts/run_train.py
├── reports/
└── docker/Dockerfile
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run (matches course weekly flow)

### Option A — easiest (recommended)

```bash
python scripts/run_m2_pipeline.py
python scripts/run_train.py
uvicorn serving.api:app --reload --port 8000
python monitoring/simulate_drift_traffic.py
python monitoring/check_drift.py
```

### Option B — step by step

### M2 — data pipeline

```bash
python data/generate_data.py
python validation/validate_data.py
python features/build_features.py
```

Or:

```bash
python scripts/run_m2_pipeline.py
```

### M3 — experiment tracking

```bash
python training/train.py
mlflow ui
```

### M4 — serve

```bash
uvicorn serving.api:app --reload --port 8000
```

Swagger: http://127.0.0.1:8000/docs

```bash
python -c "import requests; print(requests.post('http://127.0.0.1:8000/predict', json={'distance_km':12.5,'pickup_hour':20,'is_weekend':1,'passenger_count':3,'weather':'Rainy','traffic_level':'High','pickup_zone':'Z01','dropoff_zone':'Z09'}).json())"
```

### M5 — drift

```bash
python monitoring/simulate_drift_traffic.py
python monitoring/check_drift.py
```

## Dataset versioning (DVC)

```bash
dvc init
dvc add data/raw/trips.csv
git add data/raw/trips.csv.dvc .gitignore
git commit -m "Version raw trips dataset with DVC"
```

## Governance checklist

- [x] Raw schema validated before training (Pandera)
- [x] Feature logic centralized (features/build_features.py shared with serving)
- [x] Experiments logged in MLflow
- [x] Winning run reproducible (random_state=42)
- [x] Inference API has Pydantic validation
- [x] Model artifact frozen in model_store/
- [x] Predictions logged with inputs/outputs/version
- [x] Drift detection script produces actionable output
- [ ] Automated retraining pipeline — manual trigger design documented
- [ ] Unit tests — deferred

## Model selection

See `model_store/selection.json` after training and fill `reports/model_comparison.md`.

## Team

- Org: https://github.com/bits-pgaiml-mle
- Repo: https://github.com/bits-pgaiml-mle/mp1-delivery-eta
