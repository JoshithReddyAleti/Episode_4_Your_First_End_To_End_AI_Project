"""
conversation.py — Conversation History Manager
=================================================
AI Engineering Roadmap 2026 · Episode 4

What's new in Episode 4?

In Episode 3, every query was independent. The system had no memory
of what happened before. Ask "What did I just ask?" and it has no idea.

In Episode 4, we add conversation memory — the system tracks every
turn of the conversation within a session.

Why this matters for production AI:
  - Users expect context ("What about London?" after asking about weather)
  - Multi-turn workflows require state across turns
  - Debugging is impossible without a conversation audit trail
  - Interview differentiator: shows you understand stateful systems

Key engineering decisions:
  - Memory lives OUTSIDE the LLM (the LLM is stateless)
  - Each turn is a structured object, not raw text
  - History is injected into the LLM context at routing time
  - Session-scoped (resets on restart — Episode 6 adds persistence)
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Any
import json


@dataclass
class ConversationTurn:
    """
    A single turn in the conversation.

    Each turn captures everything that happened for one user query:
    what was asked, what tool was used, what was returned, whether
    it was valid, and when it happened.

    This is the atomic unit of conversation memory.
    """
    turn_number: int
    user_query: str
    routing_decision: Optional[str] = None
    tool_used: Optional[str] = None
    tool_output: Optional[Any] = None
    assistant_response: Optional[str] = None
    is_valid: bool = False
    error: Optional[str] = None
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        return {
            "turn": self.turn_number,
            "query": self.user_query,
            "tool_used": self.tool_used,
            "response": self.assistant_response,
            "valid": self.is_valid,
            "timestamp": self.timestamp,
        }

    def to_context_string(self) -> str:
        """
        Format this turn for injection into LLM context.
        Keeps it concise — the LLM doesn't need tool_output details.
        """
        tool_info = f" [used {self.tool_used}]" if self.tool_used else ""
        return f"User: {self.user_query}\nAssistant{tool_info}: {self.assistant_response or '(no response)'}"


class ConversationManager:
    """
    Manages the full conversation history for a session.

    Responsibilities:
      - Add new turns
      - Provide context for routing (recent history as text)
      - Track statistics (tools used, success rate)
      - Export the full conversation as JSON

    Design principle: the ConversationManager owns the data.
    The router and UI read from it but don't modify it directly.
    """

    def __init__(self, max_context_turns: int = 5):
        """
        Args:
            max_context_turns: How many recent turns to inject into
                               LLM context for routing. More = better
                               context but higher token cost.
        """
        self.turns: list[ConversationTurn] = []
        self.max_context_turns = max_context_turns
        self.session_start = datetime.now(timezone.utc).isoformat()

    def add_turn(
        self,
        user_query: str,
        routing_decision: str = None,
        tool_used: str = None,
        tool_output: Any = None,
        assistant_response: str = None,
        is_valid: bool = False,
        error: str = None,
    ) -> ConversationTurn:
        """
        Record a new conversation turn.

        Args:
            user_query: What the user asked
            routing_decision: What the router decided
            tool_used: Which tool was called (None = direct LLM)
            tool_output: Raw tool output
            assistant_response: The final response shown to the user
            is_valid: Whether validation passed
            error: Error message if something went wrong

        Returns:
            The created ConversationTurn
        """
        turn = ConversationTurn(
            turn_number=len(self.turns) + 1,
            user_query=user_query,
            routing_decision=routing_decision,
            tool_used=tool_used,
            tool_output=tool_output,
            assistant_response=assistant_response,
            is_valid=is_valid,
            error=error,
        )
        self.turns.append(turn)
        return turn

    def get_context_for_routing(self) -> str:
        """
        Build a context string from recent turns for LLM routing.

        This is injected into the routing prompt so the LLM knows
        what was discussed previously. Keeps only recent turns to
        manage token cost.

        Returns:
            Formatted string of recent conversation turns
        """
        if not self.turns:
            return ""

        recent = self.turns[-self.max_context_turns:]
        context_parts = [turn.to_context_string() for turn in recent]
        return "\n\n".join(context_parts)

    def get_last_turn(self) -> Optional[ConversationTurn]:
        """Get the most recent turn, or None if no history."""
        return self.turns[-1] if self.turns else None

    def get_turn_count(self) -> int:
        """Total number of turns in this session."""
        return len(self.turns)

    def get_tools_used(self) -> list[str]:
        """List of all tools used in this session (with duplicates)."""
        return [t.tool_used for t in self.turns if t.tool_used]

    def get_tool_frequency(self) -> dict[str, int]:
        """Count how many times each tool was used."""
        freq = {}
        for turn in self.turns:
            if turn.tool_used:
                freq[turn.tool_used] = freq.get(turn.tool_used, 0) + 1
        return freq

    def get_success_rate(self) -> float:
        """Percentage of turns that passed validation."""
        if not self.turns:
            return 0.0
        valid = sum(1 for t in self.turns if t.is_valid)
        return round(valid / len(self.turns) * 100, 1)

    def export_json(self) -> str:
        """
        Export the full conversation as a JSON string.
        Useful for debugging, auditing, or sharing.
        """
        export = {
            "session_start": self.session_start,
            "total_turns": len(self.turns),
            "tools_used": self.get_tool_frequency(),
            "success_rate": f"{self.get_success_rate()}%",
            "turns": [t.to_dict() for t in self.turns],
        }
        return json.dumps(export, indent=2)

    def clear(self) -> None:
        """Clear all conversation history. Used for 'new session' in UI."""
        self.turns = []
        self.session_start = datetime.now(timezone.utc).isoformat()

    def __repr__(self) -> str:
        return (
            f"ConversationManager("
            f"{len(self.turns)} turns, "
            f"success={self.get_success_rate()}%)"
        )
