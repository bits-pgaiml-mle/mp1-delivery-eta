from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    print("Week 2 stub: train and compare models with MLflow.")
    print("Planned runs: linear_regression vs hist_gradient_boosting")
    print(f"Expect processed data at: {ROOT / 'data' / 'processed' / 'trips_features.csv'}")
    print(f"Expect model artifact at: {ROOT / 'models' / 'best_model.joblib'}")
    raise SystemExit(
        "Not implemented yet. Implement after Week-1 data + feature pipeline is complete."
    )


if __name__ == "__main__":
    main()
