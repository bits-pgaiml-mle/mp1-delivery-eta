# Progress Update — mp1-delivery-eta (Flavor A)

**Last updated:** 02 Aug 2026  
**Branch baseline:** `main` (Taxila alignment merged via PR #2)  
**Course:** PCAM ZC412 Machine Learning Engineering · Mini-Project-1

> Clarification: Mini-project **Week 1** maps to module **M2** (data ingestion / validation / features) in the assignment brief.  
> Course **M1** is foundations (Taxila ELS: notebook → fragile service). This repo already includes the production-style service pieces that extend M1 into M4.

---

## Progress till now

### Setup & collaboration

| Item | Status | Notes |
|------|--------|-------|
| GitHub org `bits-pgaiml-mle` | Done | Free plan |
| Repo `mp1-delivery-eta` | Done | Flavor A selected for implementation |
| Local clone + WILP git identity | Done | `2025paml586@wilp.bits-pilani.ac.in` |
| Taxila/QuickBite + M2 ELS layout | Done | Merged to `main` |
| Incremental git history | Done | Scaffold PR + Taxila align PR |

### Mini-project Week 1 / M2 (data layer)

| Item | Status | Artifact |
|------|--------|----------|
| Synthetic trip data generation | Done | `data/generate_data.py` → `data/raw/trips.csv` |
| Immutable raw folder | Done | `data/raw/` |
| Schema validation (Pandera) | Done | `validation/validate_data.py` |
| Statistical validation checks | Done | same script |
| Feature engineering (shared) | Done | `features/build_features.py` |
| Offline feature store (SQLite) | Done | `feature_store/feature_store.db` |
| Feature schema contract | Done | `data/feature_schema.json` |
| One-command M2 pipeline | Done | `scripts/run_m2_pipeline.py` |
| Dataset versioning (DVC) + tag | **Done** | `dvc.yaml` snapshots all sources; tag `week1-data-v1` |

### Ahead of Week 1 (already implemented for later weeks)

| Module | Item | Status |
|--------|------|--------|
| M3 | MLflow experiments (Linear vs HistGradientBoosting) | Done |
| M3 | Model selection record | Done (`model_store/selection.json`, `reports/model_comparison.md`) |
| M4 | FastAPI + Pydantic `/predict`, `/health` | Done |
| M4 | Docker stub | Done |
| M5 | Prediction logging | Done (`monitoring/logger.py`) |
| M5 | Drift simulation + check | Done |
| M5 | Retraining trigger design (documented) | Draft done |
| Docs | Architecture + governance checklist | Draft done in README |

---

## Pending for Week 1 (M2 milestone)

Complete these to mark **End of Week 1** as per brief/transcripts (“ingestion, validation, feature pipeline complete; dataset version tagged”):

1. ~~**Initialize DVC and version the raw dataset**~~ **Done** (`dvc repro`, see `docs/DVC.md`)
2. **Add team member names/roles** in README (group submission)
3. **Confirm Flavor A** on the course group spreadsheet
4. **Short Week-1 note in this file** after DVC (dataset size, validation PASS evidence, feature list)

Optional polish (nice-to-have for Week 1, not blockers):

- Commit a sample validation run log under `reports/week1_validation.md`
- Ensure teammates can reproduce: `pip install -r requirements.txt` + `python scripts/run_m2_pipeline.py`

---

## Pending later (not Week 1)

| When | Item |
|------|------|
| Week 2 / M3 | Capture MLflow UI screenshots into report; refine model comparison narrative |
| Week 3 / M4 | Record curl/Postman samples; harden API error cases; optional cloud host |
| Week 4 / M5 | Stronger drift scenarios + final retraining design |
| Submission | Course-page **report** (design decisions) |
| Submission | **Video demo ≤ 10 min with voiceover** (mandatory) |

---

## How to reproduce current state

```bash
cd mp1-delivery-eta
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python scripts/run_m2_pipeline.py   # Week 1 / M2
python scripts/run_train.py         # M3 (optional for Week 1)
```

---

## Decision log (so far)

| Decision | Choice | Why |
|----------|--------|-----|
| Flavor | A — Delivery ETA | Closest to Taxila QuickBite; tabular; matches brief |
| Target | `eta_minutes` (regression) | Flavor A problem statement |
| Validation | Pandera + stats checks | Matches M2 ELS Taxila guidance |
| Feature store | SQLite offline store | Taxila QuickBite / M2 pattern |
| Serving | FastAPI + Pydantic | Taxila + brief |
| Tracking | MLflow | Taxila + brief |
| Best model (current) | HistGradientBoosting | Lower MAE than linear (~2.78 vs ~4.14) |
