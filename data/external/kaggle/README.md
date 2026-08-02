# External / Kaggle data drop zone (Flavor A)

## Modes (`configs/data_source.yaml` or `--source`)

| Mode | Meaning |
|------|---------|
| `synthetic` | Generated trips only (default) |
| `kaggle` | NYC Taxi-style CSV adapted to project schema |
| `both` | Concatenate synthetic + Kaggle-adapted rows |

## How to use real Kaggle data

1. Download [NYC Taxi Trip Duration](https://www.kaggle.com/c/nyc-taxi-trip-duration) `train.csv`
2. Copy to:
   `data/external/kaggle/nyc_taxi_sample.csv`
   (or set `kaggle.local_csv` in `configs/data_source.yaml`)
3. Set:

```yaml
data_source: kaggle
```

or:

```bash
python data/prepare_dataset.py --source kaggle
python data/prepare_dataset.py --source both
```

If no file is present, the ingest script creates a **small NYC-like demo sample** so the pipeline still runs.
