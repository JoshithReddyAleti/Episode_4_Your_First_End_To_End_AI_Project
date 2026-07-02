"""
conftest.py — Shared pytest fixtures

Fixtures defined here are automatically available to all test files
in this directory. No imports needed.
"""

import pytest
from app.state import AssistantState


@pytest.fixture
def sample_state():
    """A fresh AssistantState for use in tests."""
    return AssistantState(user_query="What is 25% of 480?")


@pytest.fixture
def calculator_result():
    """A valid calculator tool result dict."""
    return {
        "result": 120.0,
        "expression": "25% of 480",
        "query": "What is 25% of 480?",
        "error": None,
    }


@pytest.fixture
def weather_result():
    """A valid weather tool result dict."""
    return {
        "location": "London, UK",
        "temperature": 14.0,
        "feels_like": 11.0,
        "condition": "Partly cloudy",
        "wind_speed": 18.0,
        "humidity": 72,
        "unit": "C",
        "error": None,
    }
