"""
tests/test_validator.py — Validation Layer Tests
==================================================
AI Engineering Roadmap 2026 · Episode 3

Tests for the validator module.

Validation is the most important layer to test because it's your
last line of defence before bad data reaches the user.

Run with:
  pytest tests/test_validator.py -v
"""

import pytest
from app.validator import validate_response, validate_tool_input, validate_tool_output
from app.state import AssistantState


class TestValidateResponse:

    def _make_state(self, tool_used=None):
        state = AssistantState(user_query="test query")
        state.tool_used = tool_used
        return state

    def test_valid_response_passes(self):
        result = {"final_response": "Here is the answer."}
        state = self._make_state()
        validated = validate_response(result, state)
        assert validated.is_valid is True
        assert validated.final_response == "Here is the answer."

    def test_empty_final_response_fails(self):
        result = {"final_response": "   "}
        state = self._make_state()
        validated = validate_response(result, state)
        # Should either repair or return fallback — but never crash
        assert isinstance(validated.final_response, str)
        assert len(validated.final_response) > 0

    def test_missing_final_response_key_handled(self):
        result = {}  # No final_response key
        state = self._make_state()
        validated = validate_response(result, state)
        assert isinstance(validated.final_response, str)
        assert len(validated.final_response) > 0

    def test_none_result_handled(self):
        result = None
        state = self._make_state()
        validated = validate_response(result, state)
        assert isinstance(validated.final_response, str)

    def test_state_marked_valid_on_success(self):
        result = {"final_response": "The answer is 42."}
        state = self._make_state()
        validate_response(result, state)
        assert state.is_valid is True

    def test_state_records_tool_used(self):
        result = {
            "final_response": "It is 14°C in Paris.",
            "tool_output": {"temperature": 14},
        }
        state = self._make_state(tool_used="weather")
        state.tool_output = {"temperature": 14}
        validated = validate_response(result, state)
        assert validated.tool_used == "weather"


class TestValidateToolInput:

    def test_valid_calculator_input(self):
        is_valid, error = validate_tool_input("calculator", "What is 25% of 480?")
        assert is_valid is True
        assert error is None

    def test_empty_query_fails(self):
        is_valid, error = validate_tool_input("calculator", "")
        assert is_valid is False
        assert error is not None

    def test_whitespace_only_fails(self):
        is_valid, error = validate_tool_input("weather", "   ")
        assert is_valid is False
        assert error is not None

    def test_calculator_with_no_digits_fails(self):
        is_valid, error = validate_tool_input("calculator", "What is the meaning of life?")
        assert is_valid is False

    def test_valid_weather_input(self):
        is_valid, error = validate_tool_input("weather", "Weather in London")
        assert is_valid is True
        assert error is None

    def test_very_long_query_fails(self):
        is_valid, error = validate_tool_input("calculator", "x" * 3000)
        assert is_valid is False


class TestValidateToolOutput:

    def test_valid_calculator_output(self):
        output = {"result": 120.0, "expression": "25% of 480", "query": "...", "error": None}
        is_valid, error = validate_tool_output("calculator", output)
        assert is_valid is True
        assert error is None

    def test_calculator_missing_result_key_fails(self):
        output = {"expression": "25% of 480", "query": "..."}
        is_valid, error = validate_tool_output("calculator", output)
        assert is_valid is False

    def test_calculator_non_numeric_result_fails(self):
        output = {"result": "about 120", "expression": "...", "query": "...", "error": None}
        is_valid, error = validate_tool_output("calculator", output)
        assert is_valid is False

    def test_none_output_fails(self):
        is_valid, error = validate_tool_output("calculator", None)
        assert is_valid is False
        assert error is not None

    def test_valid_weather_output(self):
        output = {
            "location": "London, UK",
            "temperature": 14.0,
            "condition": "Cloudy",
            "unit": "C",
            "error": None,
        }
        is_valid, error = validate_tool_output("weather", output)
        assert is_valid is True

    def test_weather_missing_required_keys_fails(self):
        output = {"temperature": 14.0}  # Missing location and condition
        is_valid, error = validate_tool_output("weather", output)
        assert is_valid is False
