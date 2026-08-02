import requests

URL = "http://127.0.0.1:8000/predict"


def post(payload: dict) -> None:
    r = requests.post(URL, json=payload, timeout=10)
    r.raise_for_status()


def main() -> None:
    for i in range(8):
        post(
            {
                "distance_km": 2.0 + i * 0.4,
                "pickup_hour": 11,
                "is_weekend": 0,
                "passenger_count": 1,
                "weather": "Clear",
                "traffic_level": "Low",
                "pickup_zone": "Z01",
                "dropoff_zone": "Z02",
            }
        )
    print("Baseline (short-trip) batch done")

    for i in range(14):
        post(
            {
                "distance_km": 12.0 + i * 0.7,
                "pickup_hour": 19,
                "is_weekend": 1,
                "passenger_count": 3,
                "weather": "Rainy",
                "traffic_level": "High",
                "pickup_zone": "Z08",
                "dropoff_zone": "Z03",
            }
        )
    print("Drift (rush/rain/long-trip) batch done")


if __name__ == "__main__":
    main()
