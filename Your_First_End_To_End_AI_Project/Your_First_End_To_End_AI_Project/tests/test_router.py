"""tests/test_router.py — Router Tests (Episode 4)"""
import pytest
from unittest.mock import patch
from app.state import AssistantState


class TestRouter:
    def _make_state(self, query="test"):
        return AssistantState(user_query=query)

    @patch("app.router.call_llm", return_value="calculator")
    @patch("app.tools.calculator.run")
    def test_routes_to_calculator(self, mock_calc, mock_llm):
        mock_calc.return_value = {"result": 120.0, "expression": "25% of 480", "query": "...", "error": None}
        from app.router import route_query
        state = self._make_state("What is 25% of 480?")
        result = route_query("What is 25% of 480?", state)
        mock_calc.assert_called_once()
        assert state.tool_used == "calculator"

    @patch("app.router.call_llm", return_value="wikipedia")
    @patch("app.tools.wikipedia_tool.run")
    def test_routes_to_wikipedia(self, mock_wiki, mock_llm):
        mock_wiki.return_value = {"title": "AI", "summary": "Artificial intelligence...", "url": "", "error": None}
        from app.router import route_query
        state = self._make_state("Tell me about AI")
        result = route_query("Tell me about AI", state)
        mock_wiki.assert_called_once()
        assert state.tool_used == "wikipedia"

    @patch("app.router.call_llm", return_value="converter")
    @patch("app.tools.unit_converter.run")
    def test_routes_to_converter(self, mock_conv, mock_llm):
        mock_conv.return_value = {"value": 100, "from_unit": "f", "to_unit": "c", "result": 37.78, "expression": "100 f = 37.78 c", "error": None}
        from app.router import route_query
        state = self._make_state("Convert 100F to C")
        result = route_query("Convert 100F to C", state)
        mock_conv.assert_called_once()
        assert state.tool_used == "converter"

    @patch("app.router.call_llm", return_value="direct")
    def test_routes_direct(self, mock_llm):
        mock_llm.side_effect = ["direct", "Here is the answer."]
        from app.router import route_query
        state = self._make_state("What did I ask first?")
        result = route_query("What did I ask first?", state)
        assert state.tool_used is None

    @patch("app.router.call_llm", side_effect=Exception("API timeout"))
    @patch("app.router._execute_direct")
    def test_falls_back_on_failure(self, mock_direct, mock_llm):
        mock_direct.return_value = {"final_response": "Fallback."}
        from app.router import route_query
        state = self._make_state("Test")
        route_query("Test", state)
        mock_direct.assert_called_once()
