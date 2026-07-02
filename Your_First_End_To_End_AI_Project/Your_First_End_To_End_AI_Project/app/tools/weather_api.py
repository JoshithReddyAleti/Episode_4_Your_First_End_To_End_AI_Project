"""
tools/weather_api.py — Weather API Tool
=========================================
AI Engineering Roadmap 2026 · Episode 3

This tool demonstrates how to call a real external API and return
structured data that the rest of the system can validate and use.

This is the core skill that moves you from "LLM app" to "AI system":
knowing how to connect external data sources.

Uses the Open-Meteo API (free, no API key required) + the
geocoding API to resolve city names to coordinates.

Key concepts demonstrated:
  - Real external API call (not mocked)
  - Structured dict return
  - Error handling for network failures
  - Data extraction and normalisation
  - Separation from LLM logic (this tool has zero LLM calls)
"""

import requests
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Open-Meteo — free, no key required
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

TIMEOUT_SECONDS = 10

# WMO weather code descriptions
# https://open-meteo.com/en/docs#weathervariables
WMO_CODES = {
    0: "Clear sky",
    1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Foggy", 48: "Icy fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
    80: "Slight showers", 81: "Moderate showers", 82: "Violent showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Heavy thunderstorm",
}


def run(query: str) -> dict:
    """
    Fetch current weather for the location mentioned in the query.

    Args:
        query: Natural language query containing a city/location name

    Returns:
        dict with keys:
          - 'location': the resolved location name
          - 'temperature': current temperature (Celsius)
          - 'feels_like': apparent temperature (Celsius)
          - 'condition': human-readable weather description
          - 'wind_speed': km/h
          - 'humidity': percentage
          - 'unit': 'C'
          - 'error': None on success, error string on failure
    """
    logger.info(f"Weather tool received: {query!r}")

    location = _extract_location(query)
    if not location:
        return _error_response("Could not identify a location in your query.")

    coords = _geocode(location)
    if not coords:
        return _error_response(f"Could not find coordinates for location: {location!r}")

    weather = _fetch_weather(coords["lat"], coords["lon"])
    if not weather:
        return _error_response(f"Could not fetch weather data for {location}.")

    output = {
        "location": coords["name"],
        "temperature": weather["temperature"],
        "feels_like": weather["feels_like"],
        "condition": weather["condition"],
        "wind_speed": weather["wind_speed"],
        "humidity": weather["humidity"],
        "unit": "C",
        "error": None,
    }

    logger.info(f"Weather result: {output['location']} — {output['temperature']}°C, {output['condition']}")
    return output


def _extract_location(query: str) -> str | None:
    """
    Extract a location name from the query string.

    Simple heuristic: look for keywords like 'in', 'for', 'at' and
    take the following word(s). Falls back to the last word of the query.
    """
    import re
    query_clean = query.strip().rstrip("?.")

    # Look for "in <Location>", "for <Location>", "at <Location>"
    match = re.search(
        r"\b(?:in|for|at|weather)\s+([A-Za-z\s,]+?)(?:\s+(?:today|now|currently|right now))?\s*$",
        query_clean,
        re.IGNORECASE
    )
    if match:
        return match.group(1).strip()

    # Last resort: everything after the last known trigger word
    words = query_clean.split()
    if len(words) >= 2:
        return words[-1]

    return None


def _geocode(location: str) -> dict | None:
    """
    Convert a city name to latitude/longitude using Open-Meteo Geocoding.

    Returns:
        dict with 'lat', 'lon', 'name' — or None on failure
    """
    try:
        resp = requests.get(
            GEOCODING_URL,
            params={"name": location, "count": 1, "language": "en", "format": "json"},
            timeout=TIMEOUT_SECONDS
        )
        resp.raise_for_status()
        data = resp.json()

        if not data.get("results"):
            logger.warning(f"Geocoding: no results for {location!r}")
            return None

        result = data["results"][0]
        return {
            "lat": result["latitude"],
            "lon": result["longitude"],
            "name": f"{result['name']}, {result.get('country', '')}".strip(", "),
        }

    except requests.RequestException as e:
        logger.error(f"Geocoding request failed: {e}")
        return None


def _fetch_weather(lat: float, lon: float) -> dict | None:
    """
    Fetch current weather from Open-Meteo for given coordinates.

    Returns:
        dict with weather data — or None on failure
    """
    try:
        resp = requests.get(
            WEATHER_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "current": [
                    "temperature_2m",
                    "apparent_temperature",
                    "weather_code",
                    "wind_speed_10m",
                    "relative_humidity_2m",
                ],
                "temperature_unit": "celsius",
                "wind_speed_unit": "kmh",
                "timezone": "auto",
            },
            timeout=TIMEOUT_SECONDS
        )
        resp.raise_for_status()
        data = resp.json()

        current = data.get("current", {})
        wmo_code = current.get("weather_code", 0)

        return {
            "temperature": round(current.get("temperature_2m", 0), 1),
            "feels_like": round(current.get("apparent_temperature", 0), 1),
            "condition": WMO_CODES.get(wmo_code, "Unknown"),
            "wind_speed": round(current.get("wind_speed_10m", 0), 1),
            "humidity": current.get("relative_humidity_2m", 0),
        }

    except requests.RequestException as e:
        logger.error(f"Weather API request failed: {e}")
        return None


def _error_response(message: str) -> dict:
    """Return a standardised error dict."""
    logger.warning(f"Weather tool error: {message}")
    return {
        "location": None,
        "temperature": None,
        "feels_like": None,
        "condition": None,
        "wind_speed": None,
        "humidity": None,
        "unit": "C",
        "error": message,
    }
