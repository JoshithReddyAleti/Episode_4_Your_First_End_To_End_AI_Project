"""
tests/test_conversation.py — Conversation Manager Tests
========================================================
AI Engineering Roadmap 2026 · Episode 4

Tests for the conversation history manager — the new stateful
layer that Episode 4 introduces.

Run with:
  pytest tests/test_conversation.py -v
"""

import json
import pytest
from app.conversation import ConversationManager, ConversationTurn


class TestConversationTurn:

    def test_turn_creation(self):
        turn = ConversationTurn(turn_number=1, user_query="Hello")
        assert turn.turn_number == 1
        assert turn.user_query == "Hello"
        assert turn.tool_used is None
        assert turn.is_valid is False

    def test_turn_to_dict(self):
        turn = ConversationTurn(
            turn_number=1, user_query="What is 2+2?",
            tool_used="calculator", assistant_response="4", is_valid=True,
        )
        d = turn.to_dict()
        assert d["query"] == "What is 2+2?"
        assert d["tool_used"] == "calculator"
        assert d["valid"] is True

    def test_turn_context_string_with_tool(self):
        turn = ConversationTurn(
            turn_number=1, user_query="What is 2+2?",
            tool_used="calculator", assistant_response="4",
        )
        ctx = turn.to_context_string()
        assert "calculator" in ctx
        assert "2+2" in ctx

    def test_turn_context_string_without_tool(self):
        turn = ConversationTurn(
            turn_number=1, user_query="Explain AI",
            assistant_response="AI is...",
        )
        ctx = turn.to_context_string()
        assert "calculator" not in ctx


class TestConversationManager:

    def test_empty_manager(self):
        mgr = ConversationManager()
        assert mgr.get_turn_count() == 0
        assert mgr.get_last_turn() is None
        assert mgr.get_context_for_routing() == ""
        assert mgr.get_success_rate() == 0.0

    def test_add_turn(self):
        mgr = ConversationManager()
        turn = mgr.add_turn(
            user_query="Hello",
            tool_used=None,
            assistant_response="Hi!",
            is_valid=True,
        )
        assert mgr.get_turn_count() == 1
        assert turn.turn_number == 1
        assert mgr.get_last_turn().user_query == "Hello"

    def test_multiple_turns(self):
        mgr = ConversationManager()
        mgr.add_turn(user_query="Q1", assistant_response="A1", is_valid=True)
        mgr.add_turn(user_query="Q2", tool_used="calculator", assistant_response="A2", is_valid=True)
        mgr.add_turn(user_query="Q3", tool_used="weather", assistant_response="A3", is_valid=False)

        assert mgr.get_turn_count() == 3
        assert mgr.get_last_turn().user_query == "Q3"

    def test_tool_frequency(self):
        mgr = ConversationManager()
        mgr.add_turn(user_query="Q1", tool_used="calculator", is_valid=True)
        mgr.add_turn(user_query="Q2", tool_used="weather", is_valid=True)
        mgr.add_turn(user_query="Q3", tool_used="calculator", is_valid=True)

        freq = mgr.get_tool_frequency()
        assert freq["calculator"] == 2
        assert freq["weather"] == 1

    def test_success_rate(self):
        mgr = ConversationManager()
        mgr.add_turn(user_query="Q1", is_valid=True)
        mgr.add_turn(user_query="Q2", is_valid=True)
        mgr.add_turn(user_query="Q3", is_valid=False)

        assert mgr.get_success_rate() == pytest.approx(66.7, rel=0.1)

    def test_context_respects_max_turns(self):
        mgr = ConversationManager(max_context_turns=2)
        mgr.add_turn(user_query="Q1", assistant_response="A1", is_valid=True)
        mgr.add_turn(user_query="Q2", assistant_response="A2", is_valid=True)
        mgr.add_turn(user_query="Q3", assistant_response="A3", is_valid=True)

        context = mgr.get_context_for_routing()
        assert "Q1" not in context  # oldest should be excluded
        assert "Q2" in context
        assert "Q3" in context

    def test_export_json(self):
        mgr = ConversationManager()
        mgr.add_turn(user_query="Hello", assistant_response="Hi!", is_valid=True)
        exported = mgr.export_json()
        parsed = json.loads(exported)

        assert parsed["total_turns"] == 1
        assert "100" in parsed["success_rate"]
        assert len(parsed["turns"]) == 1

    def test_clear(self):
        mgr = ConversationManager()
        mgr.add_turn(user_query="Q1", is_valid=True)
        mgr.add_turn(user_query="Q2", is_valid=True)
        assert mgr.get_turn_count() == 2

        mgr.clear()
        assert mgr.get_turn_count() == 0
        assert mgr.get_last_turn() is None

    def test_tools_used_list(self):
        mgr = ConversationManager()
        mgr.add_turn(user_query="Q1", tool_used="calculator", is_valid=True)
        mgr.add_turn(user_query="Q2", is_valid=True)  # no tool
        mgr.add_turn(user_query="Q3", tool_used="weather", is_valid=True)

        tools = mgr.get_tools_used()
        assert tools == ["calculator", "weather"]
