import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / "monitoring" / "predictions.db"


def init() -> None:
    DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            distance_km REAL,
            pickup_hour INTEGER,
            is_weekend INTEGER,
            passenger_count INTEGER,
            weather TEXT,
            traffic_level TEXT,
            pickup_zone TEXT,
            dropoff_zone TEXT,
            eta_minutes REAL,
            model_version TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def log(raw: dict, result: dict) -> None:
    conn = sqlite3.connect(DB)
    conn.execute(
        """
        INSERT INTO predictions VALUES
        (NULL,?,?,?,?,?,?,?,?,?,?,?)
        """,
        (
            datetime.now(timezone.utc).isoformat(),
            raw["distance_km"],
            raw["pickup_hour"],
            raw["is_weekend"],
            raw["passenger_count"],
            raw["weather"],
            raw["traffic_level"],
            raw["pickup_zone"],
            raw["dropoff_zone"],
            result["eta_minutes"],
            result["model_version"],
        ),
    )
    conn.commit()
    conn.close()
