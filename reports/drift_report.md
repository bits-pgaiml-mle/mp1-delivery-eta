# Drift Simulation Report

Training rows: 2000
Production predictions: 23

| Feature | Train mean | Prod mean | Shift (σ) | Status |
|---------|------------|-----------|-----------|--------|
| distance_km | 12.82 | 11.80 | 0.14 | OK |
| pickup_hour | 11.37 | 16.26 | 0.71 | OK |
| passenger_count | 2.50 | 2.30 | 0.18 | OK |

Rainy share train≈20.55% prod=65.22%

## Retraining trigger (design)
- Retrain when any numeric feature shift > 0.8σ **and** ≥200 production labels are available.
- Also retrain when rolling MAE vs actual ETA exceeds threshold in config/selection review.
