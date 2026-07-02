"""
tools/wikipedia_tool.py — Wikipedia Summary Tool
===================================================
AI Engineering Roadmap 2026 · Episode 4

NEW in Episode 4.

This tool fetches a summary of any topic from the Wikipedia API.
It gives the LLM access to factual, sourced information — reducing
hallucination risk for knowledge questions.

Uses the free Wikipedia REST API (no API key required).

Key concepts demonstrated:
  - Real API integration (no mocks)
  - Content extraction and truncation
  - Graceful fallback when topic not found
  - Structured dict output
"""

import requests
from app.utils.logger import get_logger

logger = get_logger(__name__)

WIKIPEDIA_API = "https://en.wikipedia.org/api/rest_v1/page/summary"
TIMEOUT_SECONDS = 10
MAX_SUMMARY_CHARS = 800


def run(query: str) -> dict:
    """
    Fetch a Wikipedia summary for the topic in the query.

    Args:
        query: Natural language query containing a topic

    Returns:
        dict with keys: title, summary, url, error
    """
    logger.info(f"Wikipedia tool received: {query!r}")

    topic = _extract_topic(query)
    if not topic:
        return _error_response("Could not identify a topic in your query.")

    try:
        resp = requests.get(
            f"{WIKIPEDIA_API}/{topic}",
            headers={"User-Agent": "AIEngineeringRoadmap/1.0"},
            timeout=TIMEOUT_SECONDS,
        )

        if resp.status_code == 404:
            # Try with spaces replaced by underscores
            topic_alt = topic.replace(" ", "_")
            resp = requests.get(
                f"{WIKIPEDIA_API}/{topic_alt}",
                headers={"User-Agent": "AIEngineeringRoadmap/1.0"},
                timeout=TIMEOUT_SECONDS,
            )

        if resp.status_code == 404:
            return _error_response(f"No Wikipedia article found for: {topic!r}")

        resp.raise_for_status()
        data = resp.json()

        summary = data.get("extract", "")
        if len(summary) > MAX_SUMMARY_CHARS:
            summary = summary[:MAX_SUMMARY_CHARS].rsplit(".", 1)[0] + "."

        output = {
            "title": data.get("title", topic),
            "summary": summary,
            "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
            "error": None,
        }

        logger.info(f"Wikipedia result: {output['title']} ({len(summary)} chars)")
        return output

    except requests.RequestException as e:
        logger.error(f"Wikipedia API error: {e}")
        return _error_response(f"Wikipedia API request failed: {e}")


def _extract_topic(query: str) -> str | None:
    """Extract the topic to search from the query."""
    import re

    query_clean = query.strip().rstrip("?.")

    # Remove common prefixes
    for prefix in [
        "tell me about", "what is", "what are", "who is", "who was",
        "explain", "define", "describe", "summarize", "summary of",
        "look up", "search for", "wikipedia", "wiki",
    ]:
        pattern = rf"^{prefix}\s+"
        query_clean = re.sub(pattern, "", query_clean, flags=re.IGNORECASE)

    topic = query_clean.strip()
    return topic if topic else None


def _error_response(message: str) -> dict:
    logger.warning(f"Wikipedia tool error: {message}")
    return {"title": None, "summary": None, "url": None, "error": message}
