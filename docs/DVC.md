# DVC usage — mp1-delivery-eta

## What is versioned

| Path | Sources |
|------|---------|
| `data/versions/synthetic/` | Generated trips |
| `data/versions/kaggle/` | NYC-taxi adapted trips |
| `data/versions/both/` | Concatenated mix |
| `data/raw/trips.csv` | Active dataset (from `configs/data_source.yaml`) |

Tracked via `dvc.yaml` stage `snapshot_datasets` (see `dvc.lock`).

## Setup

```bash
pip install -r requirements.txt
dvc pull   # if a remote is configured; otherwise regenerate below
```

## Regenerate and version all sources

```bash
dvc repro
git add dvc.yaml dvc.lock .dvc .gitignore data/.gitignore
git commit -m "Update DVC dataset snapshots"
git tag -f week1-data-v1
```

## Switch active source without full repro

```bash
python data/prepare_dataset.py --source kaggle
# then optionally: dvc add data/raw/trips.csv
```

## Local remote (optional, for `dvc push` / `dvc pull` demos)

```bash
dvc remote add -d localremote ./dvc-storage
dvc push
```

`dvc-storage/` is gitignored; teammates without the remote can run `dvc repro`.
