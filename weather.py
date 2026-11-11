"""OpenWeatherMap client for Dionysus (no Streamlit dependency)."""

from __future__ import annotations

import logging
import re
import time
import zlib

import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
REQUEST_TIMEOUT = 10  # seconds
MAX_CITY_LEN = 85     # longest real city names are well under this

# Letters (any script), spaces, dots, apostrophes, hyphens and an optional ",CC" country code.
_CITY_RE = re.compile(r"^[^\W\d_][\w .'\-]*(,\s*[A-Za-z]{2})?$", re.UNICODE)


def clean_city(city_name: str) -> str | None:
    """Normalize user input; return None if it cannot be a city name."""
    city = " ".join((city_name or "").split())
    if not city or len(city) > MAX_CITY_LEN or not _CITY_RE.match(city):
        return None
    return city


def fetch_weather(city_name: str, api_key, session=None):
    """Fetch current weather for a city (metric units).

    Returns (data, error_message). Exactly one of them is None.
    """
    if not api_key:
        return None, "API key missing. Add OPENWEATHER_API_KEY to your .env file."

    city = clean_city(city_name)
    if city is None:
        return None, "That does not look like a city name. Use letters, spaces and hyphens only."

    params = {"q": city, "appid": api_key, "units": "metric", "lang": "en"}
    http = session or requests

    try:
        response = http.get(BASE_URL, params=params, timeout=REQUEST_TIMEOUT)
    except requests.RequestException as exc:
        # Never log the exception text: it can contain the full URL with the API key.
        logger.error("Weather request failed for %r: %s", city, type(exc).__name__)
        return None, "Weather service is unreachable. Please try again."

    logger.info("OpenWeatherMap responded %s for %r", response.status_code, city)

    if response.status_code == 200:
        try:
            data = response.json()
        except ValueError:
            return None, "Weather service sent an unreadable response."
        if not isinstance(data, dict) or not data.get("weather") or "main" not in data:
            return None, "Weather service sent an incomplete response."
        return data, None
    if response.status_code == 401:
        return None, "API key is invalid or not active yet (401)."
    if response.status_code == 404:
        return None, "City not found. Please check the spelling."
    if response.status_code == 429:
        return None, "Request limit reached. Please wait a moment and try again."
    return None, f"Unexpected response from the weather service ({response.status_code})."


# --- Demo mode -----------------------------------------------------------------
# Lets people try the app (and lets the README screenshots be reproduced) without
# an API key. The data is clearly labelled as sample data in the UI.

_DEMO_SKIES = [
    ("Clear", "clear sky", "01"), ("Clouds", "broken clouds", "04"), ("Rain", "light rain", "10"),
    ("Drizzle", "light intensity drizzle", "09"), ("Thunderstorm", "thunderstorm", "11"),
    ("Snow", "light snow", "13"), ("Mist", "mist", "50"),
]


def demo_weather(city_name: str, now: float | None = None) -> dict:
    """Deterministic, realistic-looking sample response for a city."""
    city = clean_city(city_name) or "Demo City"
    seed = zlib.crc32(city.lower().encode("utf-8"))
    main, desc, icon = _DEMO_SKIES[seed % len(_DEMO_SKIES)]
    temp = round(-5 + (seed >> 8) % 40 + ((seed >> 16) % 10) / 10, 1)
    if main == "Snow":
        temp = min(temp, 1.0)
    now = int(now if now is not None else time.time())
    day_start = now - now % 86400
    sunrise, sunset = day_start + 6 * 3600, day_start + 18 * 3600
    suffix = "d" if sunrise <= now < sunset else "n"
    return {
        "name": city.split(",")[0].title(),
        "sys": {"country": "", "sunrise": sunrise, "sunset": sunset},
        "dt": now,
        "weather": [{"main": main, "description": desc, "icon": icon + suffix}],
        "main": {"temp": temp, "feels_like": round(temp - 1.5, 1), "humidity": 40 + seed % 55},
        "wind": {"speed": round((seed >> 4) % 140 / 10, 1)},
    }
