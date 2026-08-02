import json
import sqlite3
from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[1]
FEATURE_DB = ROOT / "feature_store" / "feature_store.db"
SCHEMA_PATH = ROOT / "data" / "feature_schema.json"
MODEL_DIR = ROOT / "model_store"
TABLE = "trip_features"
TARGET = "eta_minutes"
EXPERIMENT = "delivery_eta_prediction"


def metrics(y_true, y_pred) -> dict:
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(mean_squared_error(y_true, y_pred) ** 0.5),
        "r2": float(r2_score(y_true, y_pred)),
    }


def run_experiment(name: str, model, X_train, X_test, y_train, y_test) -> tuple[str, dict]:
    with mlflow.start_run(run_name=name) as run:
        mlflow.log_param("model_type", name)
        if hasattr(model, "get_params"):
            safe_params = {
                k: v
                for k, v in model.get_params().items()
                if isinstance(v, (int, float, str, bool)) or v is None
            }
            mlflow.log_params(safe_params)

        model.fit(X_train, y_train)
        pred = model.predict(X_test)
        m = metrics(y_test, pred)
        mlflow.log_metrics(m)
        mlflow.sklearn.log_model(model, artifact_path="model")
        if SCHEMA_PATH.exists():
            mlflow.log_artifact(str(SCHEMA_PATH))
        print(f"{name}: MAE={m['mae']:.3f} RMSE={m['rmse']:.3f} R2={m['r2']:.3f}")
        return run.info.run_id, m


def main() -> None:
    conn = sqlite3.connect(FEATURE_DB)
    df = pd.read_sql(f"SELECT * FROM {TABLE}", conn)
    conn.close()

    X = df.drop(columns=[TARGET])
    y = df[TARGET]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    mlflow.set_experiment(EXPERIMENT)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    candidates = []
    rid1, m1 = run_experiment(
        "linear_regression",
        LinearRegression(),
        X_train,
        X_test,
        y_train,
        y_test,
    )
    candidates.append(("linear_regression", rid1, m1, LinearRegression()))

    rid2, m2 = run_experiment(
        "hist_gradient_boosting",
        HistGradientBoostingRegressor(max_depth=6, learning_rate=0.08, random_state=42),
        X_train,
        X_test,
        y_train,
        y_test,
    )
    candidates.append(
        (
            "hist_gradient_boosting",
            rid2,
            m2,
            HistGradientBoostingRegressor(max_depth=6, learning_rate=0.08, random_state=42),
        )
    )

    best_name, best_run, best_metrics, best_estimator = min(candidates, key=lambda c: c[2]["mae"])
    best_estimator.fit(X_train, y_train)
    joblib.dump(best_estimator, MODEL_DIR / "best_model.joblib")

    meta = {
        "selected_model": best_name,
        "mlflow_run_id": best_run,
        "metrics": best_metrics,
        "justification": (
            "Selected lowest MAE on held-out test split. "
            "Prefer gradient boosting when it clearly beats linear baseline; "
            "otherwise keep linear for simplicity."
        ),
        "model_version": "eta-v1",
        "random_state": 42,
    }
    (MODEL_DIR / "selection.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"Selected: {best_name} (run={best_run}) -> {MODEL_DIR / 'best_model.joblib'}")


if __name__ == "__main__":
    main()
