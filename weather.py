"""OpenWeatherMap client for Dionysus (no Streamlit dependency)."""

import logging

import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
REQUEST_TIMEOUT = 10  # seconds


def fetch_weather(city_name: str, api_key):
    """Fetch current weather for a city.

    Returns (data, error_message). Exactly one of them is None.
    """
    if not api_key:
        return None, "API key missing. Add OPENWEATHER_API_KEY to your .env file."

    params = {"q": city_name, "appid": api_key, "units": "metric", "lang": "en"}

    try:
        response = requests.get(BASE_URL, params=params, timeout=REQUEST_TIMEOUT)
    except requests.RequestException as exc:
        logger.error("Weather request failed for %r: %s", city_name, exc)
        return None, "Weather service is unreachable. Please try again."

    logger.info("OpenWeatherMap responded %s for %r", response.status_code, city_name)

    if response.status_code == 200:
        return response.json(), None
    if response.status_code == 401:
        return None, "API key is invalid or not active yet (401)."
    if response.status_code == 404:
        return None, "City not found. Please check the spelling."
    if response.status_code == 429:
        return None, "Request limit reached. Please wait a moment and try again."
    return None, f"Unexpected response from the weather service ({response.status_code})."
