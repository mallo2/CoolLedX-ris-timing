import logging
import requests

LOGGER = logging.getLogger(__name__)

def get_lap_time(car_number,timeout = 10):
    api_url = "https://live.ris-timing.be/api/live-timing"
    uuid = "00000000-0000-0000-0000-000000000002"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "*/*",
        "Referer": "https://live.ris-timing.be/moto",
        "Origin": "https://live.ris-timing.be",
    }

    try:
        response = requests.get(
            api_url,
            params={"uuid": uuid},
            headers=headers,
            timeout=timeout
        )
        response.raise_for_status()
        payload = response.json()
    except requests.exceptions.RequestException:
        LOGGER.exception("Erreur API lors de la récupération du temps au tour")
        return None
    except ValueError:
        LOGGER.exception("Réponse API invalide: impossible de décoder le JSON")
        return None

    for car in payload.get("cars"):
        if car.get("car_number") == car_number:
            lap = car.get("lap") or {}
            return lap.get("lap_time_ms")

    LOGGER.info("Car number %s not found in API response", car_number)
    return None