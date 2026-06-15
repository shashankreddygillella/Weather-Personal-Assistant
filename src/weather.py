"""
weather.py
Fetches current and hourly weather data for Houston, TX
using the Open-Meteo API (no API key required).
"""

import json
try:
    import requests as _requests
    _USE_REQUESTS = True
except ImportError:
    import urllib.request
    _USE_REQUESTS = False

HOUSTON_LAT = 29.7604
HOUSTON_LON = -95.3698
CITY_NAME = "Houston, TX"

API_URL = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude={lat}&longitude={lon}"
    "&current=temperature_2m,precipitation,weathercode,windspeed_10m"
    "&hourly=temperature_2m,precipitation_probability,weathercode"
    "&temperature_unit=fahrenheit"
    "&wind_speed_unit=mph"
    "&precipitation_unit=inch"
    "&timezone=America%2FChicago"
    "&forecast_days=1"
)

WMO_CODES = {
    0: "Clear sky",
    1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Icy fog",
    51: "Light drizzle", 53: "Drizzle", 55: "Heavy drizzle",
    61: "Light rain", 63: "Rain", 65: "Heavy rain",
    71: "Light snow", 73: "Snow", 75: "Heavy snow",
    80: "Light showers", 81: "Showers", 82: "Heavy showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Severe thunderstorm",
}


def fetch_weather() -> dict:
    """Fetch weather data from Open-Meteo and return parsed dict."""
    url = API_URL.format(lat=HOUSTON_LAT, lon=HOUSTON_LON)
    try:
        if _USE_REQUESTS:
            response = _requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        else:
            with urllib.request.urlopen(url, timeout=10) as response:
                return json.loads(response.read().decode())
    except Exception as e:
        raise ConnectionError(f"Failed to fetch weather data: {e}")


def get_current_conditions(data: dict) -> dict:
    """Extract current weather conditions from raw API response."""
    current = data.get("current", {})
    code = current.get("weathercode", 0)
    return {
        "temperature": current.get("temperature_2m"),
        "precipitation": current.get("precipitation"),
        "windspeed": current.get("windspeed_10m"),
        "weathercode": code,
        "description": WMO_CODES.get(code, "Unknown"),
        "city": CITY_NAME,
    }


def get_hourly_conditions(data: dict) -> list:
    """Extract hourly forecast as list of dicts."""
    hourly = data.get("hourly", {})
    times = hourly.get("time", [])
    temps = hourly.get("temperature_2m", [])
    precip_probs = hourly.get("precipitation_probability", [])
    codes = hourly.get("weathercode", [])

    return [
        {
            "time": times[i],
            "temperature": temps[i],
            "precipitation_probability": precip_probs[i],
            "weathercode": codes[i],
            "description": WMO_CODES.get(codes[i], "Unknown"),
        }
        for i in range(len(times))
    ]
