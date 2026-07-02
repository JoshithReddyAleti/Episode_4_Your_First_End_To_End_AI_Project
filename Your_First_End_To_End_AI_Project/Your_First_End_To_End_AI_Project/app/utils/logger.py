"""
utils/logger.py — Structured Logger
=====================================
AI Engineering Roadmap 2026 · Episode 3

Why structured logging matters:

In production, you don't sit and watch your terminal.
You need logs that can be:
  - Searched (find all errors in the last hour)
  - Filtered (show only calculator tool calls)
  - Sent to a monitoring service (Datadog, CloudWatch, etc.)

This logger formats output cleanly and includes the module name,
so you always know WHERE a log line came from.
"""

import logging
import sys
import os


def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger for the given module name.

    Usage:
        logger = get_logger(__name__)
        logger.info("Router decision: calculator")
        logger.warning("Validation failed — retrying")
        logger.error("API call failed", exc_info=True)

    Args:
        name: Usually __name__ — gives you the module path in logs

    Returns:
        Configured Logger instance
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        # Don't add handlers twice if this function is called multiple times
        return logger

    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    logger.setLevel(getattr(logging, log_level, logging.INFO))

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Prevent propagation to root logger (avoids duplicate output)
    logger.propagate = False

    return logger
