"""
utils/helpers.py — Shared Helper Functions
============================================
AI Engineering Roadmap 2026 · Episode 3

Utility functions used across the codebase.
Keeping these in one place avoids duplication and makes testing easy.
"""

import json
import re
from typing import Any, Optional


def safe_json_parse(text: str) -> Optional[dict]:
    """
    Attempt to parse a JSON string, returning None on failure.

    LLMs often return JSON wrapped in markdown code fences:
      ```json
      {"key": "value"}
      ```
    This function strips those fences before parsing.

    Args:
        text: A string that might contain JSON

    Returns:
        Parsed dict, or None if parsing fails
    """
    if not text:
        return None

    # Strip markdown code fences if present
    cleaned = re.sub(r"```(?:json)?\s*", "", text).strip().rstrip("`").strip()

    try:
        return json.loads(cleaned)
    except (json.JSONDecodeError, ValueError):
        return None


def truncate(text: str, max_length: int = 200) -> str:
    """
    Truncate a string for safe display in logs.

    Args:
        text: The string to truncate
        max_length: Maximum character length

    Returns:
        Truncated string with ellipsis if needed
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def sanitise_query(query: str) -> str:
    """
    Clean a user query before processing.

    - Strips leading/trailing whitespace
    - Collapses multiple spaces
    - Removes null bytes (common in malformed input)

    Args:
        query: Raw user input

    Returns:
        Cleaned query string
    """
    if not query:
        return ""
    cleaned = query.replace("\x00", "")
    cleaned = " ".join(cleaned.split())
    return cleaned.strip()


def format_number(value: float, decimals: int = 2) -> str:
    """
    Format a number for display, removing trailing zeros.

    Args:
        value: The number to format
        decimals: Maximum decimal places

    Returns:
        Formatted string (e.g., 120.0 → "120", 3.14159 → "3.14")
    """
    formatted = f"{value:.{decimals}f}"
    # Remove trailing zeros and unnecessary decimal point
    if "." in formatted:
        formatted = formatted.rstrip("0").rstrip(".")
    return formatted


def is_question(text: str) -> bool:
    """
    Simple heuristic to detect if the user input is phrased as a question.
    """
    text = text.strip().lower()
    question_starters = ("what", "who", "where", "when", "why", "how", "is", "are", "can", "do", "does")
    return text.endswith("?") or text.startswith(question_starters)
