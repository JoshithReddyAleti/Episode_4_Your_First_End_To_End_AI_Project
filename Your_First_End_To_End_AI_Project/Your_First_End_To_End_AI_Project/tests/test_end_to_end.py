"""tests/test_end_to_end.py — Integration Tests (Episode 4)"""
import pytest
from unittest.mock import patch
from app.main import main
from app.state import AssistantState
from app.router import route_query
from app.validator import validate_response
from app.conversation import ConversationManager
from app.utils.config import load_config


@pytest.fixture(autouse=True)
def load_env():
    load_config()


class TestFullPipeline:

    @patch("app.router.call_llm")
    @patch("app.tools.calculator.run")
    def test_calculator_pipeline(self, mock_calc, mock_llm):
        mock_llm.side_effect = ["calculator", "25% of 480 is 120."]
        mock_calc.return_value = {"result": 120.0, "expression": "25% of 480", "query": "...", "error": None}

        state = AssistantState(user_query="What is 25% of 480?")
        result = route_query("What is 25% of 480?", state)
        validated = validate_response(result, state)

        assert validated.final_response is not None
        assert isinstance(validated.final_response, str)
        assert len(validated.final_response) > 0

    @patch("app.router.call_llm")
    def test_direct_pipeline(self, mock_llm):
        mock_llm.side_effect = ["direct", "A vector embedding is a numerical representation."]

        state = AssistantState(user_query="What is a vector embedding?")
        result = route_query("What is a vector embedding?", state)
        validated = validate_response(result, state)

        assert validated.final_response is not None
        assert len(validated.final_response) > 5

    @patch("app.router.call_llm")
    @patch("app.tools.calculator.run")
    def test_conversation_records_turns(self, mock_calc, mock_llm):
        """Verify conversation manager records turns correctly."""
        mock_llm.side_effect = ["calculator", "120."]
        mock_calc.return_value = {"result": 120.0, "expression": "25% of 480", "query": "...", "error": None}

        conversation = ConversationManager()
        state = AssistantState(user_query="What is 25% of 480?")
        result = route_query("What is 25% of 480?", state)
        validated = validate_response(result, state)

        conversation.add_turn(
            user_query="What is 25% of 480?",
            tool_used=state.tool_used,
            assistant_response=validated.final_response,
            is_valid=validated.is_valid,
        )

        assert conversation.get_turn_count() == 1
        assert conversation.get_last_turn().tool_used == "calculator"

    def test_pipeline_never_returns_empty(self):
        """Even under total failure, something is returned."""
        state = AssistantState(user_query="test")
        result = {"final_response": "Fallback response."}
        validated = validate_response(result, state)
        assert len(validated.final_response.strip()) > 0
