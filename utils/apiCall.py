import requests

API_URL = "https://live.ris-timing.be/api/live-timing"
UUID = "00000000-0000-0000-0000-000000000002"


def get_lap_time(car_number):
    params = {"uuid": UUID}

    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        data = response.json()

        for car in data.get("cars", []):
            if car.get("car_number") == car_number:
                lap = car.get("lap", {})
                lap_time = lap.get("lap_time_ms")
                return lap_time

        return None

    except requests.exceptions.RequestException as e:
        print(f"Erreur API: {e}")
        return None

