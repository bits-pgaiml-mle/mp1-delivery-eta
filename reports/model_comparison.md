# Model Comparison Report

**Project:** mp1-delivery-eta (Flavor A)  
**Module:** M3 — Experimentation & Reproducibility

## Experiments

| Run | Model | MAE | RMSE | R2 | MLflow run id |
|-----|-------|-----|------|----|---------------|
| 1 | linear_regression | 4.141 | 5.401 | 0.964 | (see MLflow UI) |
| 2 | hist_gradient_boosting | 2.782 | 3.489 | 0.985 | e1584f248c934c85bda0d1c63d136dc1 |

## Decision

Best model: **hist_gradient_boosting** (`model_store/selection.json`)  
Justification: lowest MAE on held-out split (~2.8 vs ~4.1). Clear improvement over linear baseline; acceptable complexity for tabular ETA.
