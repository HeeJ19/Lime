"""Weather lookup for the recommendation engine: calls Open-Meteo's free,
keyless forecast API for the user's current local conditions, which the
recommendation service then turns into a style-matching query.

Open-Meteo requires no API key and allows 10K free calls/day. Called
directly via httpx, same lightweight pattern as vlm_tagging.py, rather
than pulling in a client SDK.
"""

import httpx

_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

# WMO weather codes (https://open-meteo.com/en/docs) collapsed into the
# coarse buckets the recommendation service maps to outfit styles.
_WEATHER_CODES: dict[int, str] = {
    0: "clear",
    1: "mostly clear",
    2: "partly cloudy",
    3: "overcast",
    45: "foggy",
    48: "foggy",
    51: "drizzling",
    53: "drizzling",
    55: "drizzling",
    61: "rainy",
    63: "rainy",
    65: "rainy",
    71: "snowy",
    73: "snowy",
    75: "snowy",
    77: "snowy",
    80: "showery",
    81: "showery",
    82: "showery",
    85: "snowy",
    86: "snowy",
    95: "stormy",
    96: "stormy",
    99: "stormy",
}


class WeatherError(Exception):
    """Raised when Open-Meteo can't be reached or returns an unusable response.

    Callers must turn this into a clean user-facing message rather than letting
    the recommendation flow crash.
    """


class CurrentWeather:
    def __init__(self, temperature_c: float, condition: str):
        self.temperature_c = temperature_c
        self.condition = condition


def get_current_weather(latitude: float, longitude: float) -> CurrentWeather:
    """Fetch current temperature (°C) and a plain-English condition for a location."""
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,weather_code",
    }

    try:
        resp = httpx.get(_FORECAST_URL, params=params, timeout=15)
        resp.raise_for_status()
        current = resp.json()["current"]
        temperature_c = float(current["temperature_2m"])
        code = int(current["weather_code"])
    except (httpx.HTTPError, KeyError, TypeError, ValueError) as e:
        raise WeatherError(f"Open-Meteo returned an unusable response: {e}") from e

    return CurrentWeather(temperature_c=temperature_c, condition=_WEATHER_CODES.get(code, "clear"))
