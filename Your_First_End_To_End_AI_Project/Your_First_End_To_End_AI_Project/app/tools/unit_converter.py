"""
tools/unit_converter.py — Unit Conversion Tool
================================================
AI Engineering Roadmap 2026 · Episode 4

NEW in Episode 4.

Handles temperature, length, weight, and volume conversions.
No external API needed — pure Python computation.

Demonstrates:
  - Regex-based parsing of natural language
  - Structured output for any conversion
  - Clean separation of parsing and computation
"""

import re
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Conversion tables
CONVERSIONS = {
    # Temperature
    ("f", "c"): lambda v: (v - 32) * 5 / 9,
    ("c", "f"): lambda v: v * 9 / 5 + 32,
    ("c", "k"): lambda v: v + 273.15,
    ("k", "c"): lambda v: v - 273.15,
    ("f", "k"): lambda v: (v - 32) * 5 / 9 + 273.15,
    ("k", "f"): lambda v: (v - 273.15) * 9 / 5 + 32,
    # Length
    ("km", "miles"): lambda v: v * 0.621371,
    ("miles", "km"): lambda v: v * 1.60934,
    ("m", "ft"): lambda v: v * 3.28084,
    ("ft", "m"): lambda v: v * 0.3048,
    ("cm", "inches"): lambda v: v * 0.393701,
    ("inches", "cm"): lambda v: v * 2.54,
    # Weight
    ("kg", "lbs"): lambda v: v * 2.20462,
    ("lbs", "kg"): lambda v: v * 0.453592,
    ("g", "oz"): lambda v: v * 0.035274,
    ("oz", "g"): lambda v: v * 28.3495,
    # Volume
    ("liters", "gallons"): lambda v: v * 0.264172,
    ("gallons", "liters"): lambda v: v * 3.78541,
}

# Aliases for parsing flexibility
UNIT_ALIASES = {
    "fahrenheit": "f", "fahr": "f",
    "celsius": "c", "centigrade": "c",
    "kelvin": "k",
    "kilometers": "km", "kilometre": "km", "kilometres": "km",
    "mile": "miles",
    "meters": "m", "metre": "m", "metres": "m",
    "feet": "ft", "foot": "ft",
    "centimeters": "cm", "centimetre": "cm", "centimetres": "cm",
    "inch": "inches",
    "kilograms": "kg", "kilogram": "kg",
    "pounds": "lbs", "pound": "lbs", "lb": "lbs",
    "grams": "g", "gram": "g",
    "ounces": "oz", "ounce": "oz",
    "liter": "liters", "litre": "liters", "litres": "liters",
    "gallon": "gallons",
}


def run(query: str) -> dict:
    """
    Parse a unit conversion query and return the result.

    Handles patterns like:
      "Convert 100 F to C"
      "What is 50 kg in lbs?"
      "100 miles to km"

    Args:
        query: Natural language conversion request

    Returns:
        dict with: value, from_unit, to_unit, result, error
    """
    logger.info(f"Unit converter received: {query!r}")

    try:
        value, from_unit, to_unit = _parse_conversion(query)
        from_norm = _normalize_unit(from_unit)
        to_norm = _normalize_unit(to_unit)

        key = (from_norm, to_norm)
        if key not in CONVERSIONS:
            return _error_response(
                f"Unsupported conversion: {from_norm} → {to_norm}. "
                f"Supported: {list(CONVERSIONS.keys())}"
            )

        result = round(CONVERSIONS[key](value), 4)

        output = {
            "value": value,
            "from_unit": from_norm,
            "to_unit": to_norm,
            "result": result,
            "expression": f"{value} {from_norm} = {result} {to_norm}",
            "error": None,
        }

        logger.info(f"Conversion: {output['expression']}")
        return output

    except Exception as e:
        logger.error(f"Unit converter error: {e}")
        return _error_response(str(e))


def _parse_conversion(query: str) -> tuple[float, str, str]:
    """
    Extract value, from_unit, and to_unit from a natural language query.

    Raises ValueError if parsing fails.
    """
    query_clean = query.lower().strip().rstrip("?.")

    # Pattern: "<number> <unit> to/in <unit>"
    match = re.search(
        r"(-?\d+(?:\.\d+)?)\s*([a-z°]+)\s+(?:to|in|into)\s+([a-z°]+)",
        query_clean
    )
    if match:
        return float(match.group(1)), match.group(2), match.group(3)

    # Pattern: "convert <number> <unit> to <unit>"
    match = re.search(
        r"convert\s+(-?\d+(?:\.\d+)?)\s*([a-z°]+)\s+(?:to|in)\s+([a-z°]+)",
        query_clean
    )
    if match:
        return float(match.group(1)), match.group(2), match.group(3)

    # Pattern: "<number> <unit> <unit>" (e.g., "100 fahrenheit celsius")
    match = re.search(
        r"(-?\d+(?:\.\d+)?)\s+([a-z]+)\s+(?:to\s+)?([a-z]+)",
        query_clean
    )
    if match:
        return float(match.group(1)), match.group(2), match.group(3)

    raise ValueError(
        f"Could not parse conversion from: {query!r}. "
        f"Try a format like: '100 F to C' or 'Convert 50 kg to lbs'"
    )


def _normalize_unit(unit: str) -> str:
    """Normalize a unit string to its canonical form."""
    unit = unit.lower().strip().rstrip("s") if len(unit) > 3 else unit.lower().strip()
    # Check aliases
    if unit in UNIT_ALIASES:
        return UNIT_ALIASES[unit]
    # Check if already a canonical unit
    all_units = set()
    for k in CONVERSIONS:
        all_units.add(k[0])
        all_units.add(k[1])
    if unit in all_units:
        return unit
    # Try with 's' appended
    if unit + "s" in all_units:
        return unit + "s"
    return unit


def _error_response(message: str) -> dict:
    logger.warning(f"Unit converter error: {message}")
    return {
        "value": None, "from_unit": None, "to_unit": None,
        "result": None, "expression": None, "error": message,
    }
