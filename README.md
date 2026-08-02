# mp1-delivery-eta

**BITS Pilani WILP · PGAIML · PCAM ZC412 Machine Learning Engineering**  
**Mini-Project-1 · Flavor A — Delivery / Ride ETA Prediction**

Aligned with Taxila **QuickBite** tutorial + **M2 ELS Reliable Data Pipelines** patterns, adapted for ETA regression (Flavor A brief).

## Progress

See **[reports/PROGRESS.md](reports/PROGRESS.md)** for:

- What is completed till now (M2 data + DVC done; M3–M5 code ahead of schedule)
- Remaining Week-1 process items (team names, spreadsheet, short design note)
- Later-week and submission leftovers (report + video)

## Architecture (Taxila-style)

```text
data/prepare_dataset.py  (--source synthetic | kaggle | both)
        |
        v
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
├── configs/data_source.yaml
├── data/
│   ├── prepare_dataset.py
│   ├── generate_data.py
│   ├── ingest_kaggle.py
│   └── raw/
├── validation/validate_data.py
├── features/build_features.py
├── feature_store/feature_store.db
├── training/train.py
├── serving/api.py
├── monitoring/
│   ├── logger.py
│   ├── check_drift.py
│   └── simulate_drift_traffic.py
├── model_store/
├── scripts/
│   ├── run_m2_pipeline.py           # Option A: Week 1 / M2
│   ├── run_train.py                 # Option A: M2 + M3
│   └── snapshot_datasets.py         # DVC: all data-source snapshots
├── dvc.yaml / dvc.lock
├── docs/DVC.md
├── USAGE.md
├── reports/
└── docker/Dockerfile
```

## Usage (local + Colab)

Full instructions (Option A / Option B, local and Google Colab): **[USAGE.md](USAGE.md)**

There are **two execution paths** (same as Flavors B and C):

| Path | When to use | Entry |
|------|-------------|--------|
| **Option A** | Fastest end-to-end run | `scripts/run_m2_pipeline.py` then `scripts/run_train.py` |
| **Option B** | Step-by-step / debugging | prepare → validate → features → train → serve |

### Local — Option A (quick, recommended)

```bash
python scripts/run_m2_pipeline.py
python scripts/run_train.py
uvicorn serving.api:app --reload --port 8000
python monitoring/simulate_drift_traffic.py
python monitoring/check_drift.py
```

### Local — Option B (step by step)

```bash
python data/prepare_dataset.py --source synthetic
python validation/validate_data.py
python features/build_features.py
python training/train.py
uvicorn serving.api:app --reload --port 8000
python monitoring/simulate_drift_traffic.py
python monitoring/check_drift.py
```

Swagger: http://127.0.0.1:8000/docs

### Data source switch (before Option A or B)

```bash
# configs/data_source.yaml  OR:
python data/prepare_dataset.py --source synthetic   # default
python data/prepare_dataset.py --source kaggle
python data/prepare_dataset.py --source both
```

`scripts/run_m2_pipeline.py` (Option A) already calls `prepare_dataset.py` using the config default.

### Colab — Option A (easiest)

```python
!git clone https://github.com/bits-pgaiml-mle/mp1-delivery-eta.git
%cd mp1-delivery-eta
!pip install -q -r requirements.txt
!python scripts/run_m2_pipeline.py
!python scripts/run_train.py
```

### Colab — Option B (step by step)

```python
!python data/prepare_dataset.py --source synthetic
!python validation/validate_data.py
!python features/build_features.py
!python training/train.py
```

Use `fastapi.testclient.TestClient` for `/predict` on Colab (details in USAGE.md). T4 GPU is not required for Flavor A.

## Dataset versioning (DVC)

All dataset modes (`synthetic`, `kaggle`, `both`) are snapshotted under `data/versions/` and tracked with DVC. Details: **[docs/DVC.md](docs/DVC.md)**.

```bash
dvc repro          # regenerate all source snapshots + active data/raw
dvc push           # push to local remote ./dvc-storage (optional)
git tag week1-data-v1
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
