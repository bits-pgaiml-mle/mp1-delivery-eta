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

## Usage (local + Colab)

Full instructions (Option A / Option B, local and Google Colab): **[USAGE.md](USAGE.md)**

### Local — Option A (quick)

```bash
python scripts/run_m2_pipeline.py
python scripts/run_train.py
uvicorn serving.api:app --reload --port 8000
python monitoring/simulate_drift_traffic.py
python monitoring/check_drift.py
```

### Local — Option B (step by step)

```bash
python data/generate_data.py
python validation/validate_data.py
python features/build_features.py
python training/train.py
uvicorn serving.api:app --reload --port 8000
```

Swagger: http://127.0.0.1:8000/docs

### Colab (CPU)

```python
!git clone https://github.com/bits-pgaiml-mle/mp1-delivery-eta.git
%cd mp1-delivery-eta
!pip install -q -r requirements.txt
!python scripts/run_m2_pipeline.py
!python scripts/run_train.py
```

Use `fastapi.testclient.TestClient` for `/predict` on Colab (details in USAGE.md). T4 GPU is not required for Flavor A.

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
