# mp1-delivery-eta

**BITS Pilani WILP · PGAIML · PCAM ZC412 Machine Learning Engineering**  
**Mini-Project-1 · Flavor A — Delivery / Ride ETA Prediction**

End-to-end ML pipeline: raw trip data → validation & features → tracked experiments → REST API → monitoring / drift / retraining design.

## Architecture

```text
raw trips.csv
      |
      v
  validate  ----->  features  ----->  trips_features.csv (DVC)
                         |
                         v
                   train + MLflow  ----->  models/best_model.joblib
                         |
                         v
                      FastAPI  ----->  POST /predict (eta_minutes)
                         |
                         v
                    monitoring  ----->  logs + drift report + retrain trigger
```

## Repository layout

```text
mp1-delivery-eta/
├── configs/config.yaml          # paths, target, thresholds
├── data/
│   ├── raw/                     # generated or downloaded trips
│   └── processed/               # feature tables
├── src/
│   ├── data/                    # generate + validate (Week 1 / M2)
│   ├── features/                # feature engineering (Week 1 / M2)
│   ├── training/                # MLflow experiments (Week 2 / M3)
│   ├── serving/                 # FastAPI app (Week 3 / M4)
│   └── monitoring/              # drift + retraining (Week 4 / M5)
├── models/                      # serialized model artifacts
├── monitoring/logs/             # prediction logs
├── reports/                     # model comparison + drift write-ups
├── notebooks/                   # optional exploration
├── docker/Dockerfile
├── scripts/run_week1.py
└── requirements.txt
```

## Setup

```bash
cd mp1-delivery-eta
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
# source .venv/bin/activate

pip install -r requirements.txt
```

## Week 1 — data pipeline (ready)

```bash
python scripts/run_week1.py
```

Or step by step:

```bash
python -m src.data.generate
python -m src.data.validate
python -m src.features.build_features
```

## Later weeks (stubs in place)

| Week | Module | Command / artifact |
|------|--------|--------------------|
| 2 | M3 | `python -m src.training.train` → MLflow runs + `reports/model_comparison.md` |
| 3 | M4 | `uvicorn src.serving.app:app --reload` → `/health`, `/predict` |
| 4 | M5 | `python -m src.monitoring.drift` → `reports/drift_report.md` |

## Dataset

Starter uses a **synthetic trip dataset** (distance, hour, weekend, weather, traffic, zones → `eta_minutes`) so the pipeline runs without external downloads.  
Optional upgrade: replace `data/raw/trips.csv` with [NYC Taxi Trip Duration](https://www.kaggle.com/c/nyc-taxi-trip-duration) and adapt schema validation.

## Tools

| Concern | Tool |
|---------|------|
| Tracking | MLflow |
| Data versioning | DVC |
| Serving | FastAPI + Uvicorn |
| Packaging | Docker |
| VCS | Git (weekly commits) |

## Team

- Org: [bits-pgaiml-mle](https://github.com/bits-pgaiml-mle)
- Repo: [mp1-delivery-eta](https://github.com/bits-pgaiml-mle/mp1-delivery-eta)

Add member names and roles here before submission.

## Submission checklist (from brief)

1. Versioned dataset + pipeline code (Git history by week)
2. Experiment tracking logs + model comparison report
3. Deployed API + sample curl/Postman calls
4. Monitoring log, drift simulation, retraining trigger design
5. README (this file) + architecture + 5–7 min demo
