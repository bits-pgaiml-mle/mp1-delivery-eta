# Usage Guide — mp1-delivery-eta (Flavor A)

End-to-end Delivery / Ride **ETA** pipeline.  
Works on **local machine (CPU)** and **Google Colab (CPU is enough; T4 GPU not required)**.

---

## 1. Local usage

### 1.1 Setup (once)

```powershell
cd "D:\TVSRAO\BITS\PGAIML\Course\ML Engineering\Mini-Project-1\mp1-delivery-eta"
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

macOS / Linux:

```bash
cd mp1-delivery-eta
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run all commands from the **repo root**.

### Execution options (same idea as Flavors B / C)

| Path | Best for | Commands |
|------|----------|----------|
| **Option A** | Quick full run | `python scripts/run_m2_pipeline.py` then `python scripts/run_train.py` |
| **Option B** | Learn / debug each stage | prepare → validate → features → train → serve → drift |

### 1.1b Data source: synthetic / Kaggle / both

Set `configs/data_source.yaml` → `data_source: synthetic | kaggle | both`, or pass `--source` once:

```powershell
python data/prepare_dataset.py --source synthetic
python data/prepare_dataset.py --source kaggle
python data/prepare_dataset.py --source both
```

- **synthetic** — generated trips (default; fine for the brief)
- **kaggle** — adapts NYC taxi CSV under `data/external/kaggle/` (demo sample auto-created if missing)
- **both** — concatenates synthetic + Kaggle-adapted rows

Details: `data/external/kaggle/README.md`. Option A’s `scripts/run_m2_pipeline.py` calls `prepare_dataset.py` automatically.

### 1.2 Option A — easiest (recommended)

```powershell
python scripts/run_m2_pipeline.py
python scripts/run_train.py
```

**Terminal 1 — API**

```powershell
uvicorn serving.api:app --reload --port 8000
```

**Terminal 2 — predict + drift**

```powershell
python -c "import requests; print(requests.post('http://127.0.0.1:8000/predict', json={'distance_km':12.5,'pickup_hour':20,'is_weekend':1,'passenger_count':3,'weather':'Rainy','traffic_level':'High','pickup_zone':'Z01','dropoff_zone':'Z09'}).json())"
python monitoring/simulate_drift_traffic.py
python monitoring/check_drift.py
```

- Swagger: http://127.0.0.1:8000/docs  
- MLflow UI (optional): `mlflow ui` → http://127.0.0.1:5000  

### 1.3 Option B — step by step

```powershell
python data/prepare_dataset.py --source synthetic
python validation/validate_data.py
python features/build_features.py
python training/train.py
uvicorn serving.api:app --reload --port 8000
python monitoring/simulate_drift_traffic.py
python monitoring/check_drift.py
```

| Step | Entry file |
|------|------------|
| Prepare data | `data/prepare_dataset.py` (`--source synthetic\|kaggle\|both`) |
| Validate | `validation/validate_data.py` |
| Features | `features/build_features.py` |
| Train | `training/train.py` |
| Serve | `serving/api.py` via uvicorn |
| Drift simulate | `monitoring/simulate_drift_traffic.py` |
| Drift check | `monitoring/check_drift.py` |

---

## 2. Google Colab usage

### 2.1 Runtime

1. Open [Google Colab](https://colab.research.google.com/)
2. Runtime → Change runtime type → **CPU** (T4 GPU not needed for Flavor A)

### 2.2 Option A — easiest

Paste into a Colab cell:

```python
!git clone https://github.com/bits-pgaiml-mle/mp1-delivery-eta.git
%cd mp1-delivery-eta
!pip install -q -r requirements.txt

!python scripts/run_m2_pipeline.py
!python scripts/run_train.py
```

Predict without a long-running server (recommended on Colab):

```python
from fastapi.testclient import TestClient
from serving.api import app

client = TestClient(app)
print(client.get("/health").json())
print(client.post("/predict", json={
    "distance_km": 12.5,
    "pickup_hour": 20,
    "is_weekend": 1,
    "passenger_count": 3,
    "weather": "Rainy",
    "traffic_level": "High",
    "pickup_zone": "Z01",
    "dropoff_zone": "Z09",
}).json())
```

Drift check (uses logged predictions from TestClient calls + training feature store):

```python
# log a few more predictions
for i in range(8):
    client.post("/predict", json={
        "distance_km": 2.0 + i * 0.4, "pickup_hour": 11, "is_weekend": 0,
        "passenger_count": 1, "weather": "Clear", "traffic_level": "Low",
        "pickup_zone": "Z01", "dropoff_zone": "Z02",
    })
for i in range(14):
    client.post("/predict", json={
        "distance_km": 12.0 + i * 0.7, "pickup_hour": 19, "is_weekend": 1,
        "passenger_count": 3, "weather": "Rainy", "traffic_level": "High",
        "pickup_zone": "Z08", "dropoff_zone": "Z03",
    })

!python monitoring/check_drift.py
```

### 2.3 Option B — step by step on Colab

```python
!python data/prepare_dataset.py --source synthetic
!python validation/validate_data.py
!python features/build_features.py
!python training/train.py
```

Then use the TestClient cell above for `/predict`.

### 2.4 Optional: uvicorn on Colab

Possible with background process + ngrok, but **not required** for coursework. Prefer TestClient for demos/screenshots.

---

## 3. What each option does

| Stage | Option A | Option B |
|-------|----------|----------|
| M2 data | `scripts/run_m2_pipeline.py` | prepare → validate → features |
| M3 train | `scripts/run_train.py` (includes M2) | `training/train.py` |
| M4 serve | uvicorn / TestClient | same |
| M5 drift | simulate + check_drift | same |
