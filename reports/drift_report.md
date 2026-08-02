# Drift Simulation & Retraining Design

**Project:** mp1-delivery-eta (Flavor A)  
**Module:** M5 — Monitoring, Drift & Retraining  
**Status:** Placeholder — fill after Week 4

## Monitoring signals

- Prediction log path: `monitoring/logs/predictions.csv`
- Metrics: MAE, RMSE, prediction vs actual residual mean

## Drift scenarios to simulate

1. Rush-hour surge (shift pickup_hour distribution toward 17–20)
2. Weather shock (increase Rainy share)
3. Traffic regime change (increase High traffic share)

## Retraining trigger (draft)

Retrain when rolling 7-day MAE exceeds `configs/config.yaml -> monitoring.mae_retrain_threshold` **and** at least N=200 labeled actual ETAs are available.
