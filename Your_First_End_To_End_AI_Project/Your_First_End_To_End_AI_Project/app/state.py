"""
state.py — System State
========================
AI Engineering Roadmap 2026 · Episode 3

What is state and why does it matter?

In a simple chatbot, every message is independent. There's no memory of
what happened before, no record of which tool was used, no way to know
if the previous step succeeded or failed.

In a real system, state is everything.

State lets you:
  - Know what happened at every step of the pipeline
  - Debug when something goes wrong
  - Retry intelligently (you know what failed and why)
  - Build conversation memory (Episode 5 will expand on this)
  - Observe your system in production

Think of state as the system's working memory for a single request.

Key concepts demonstrated:
  - Dataclass-based state modelling
  - Immutable-friendly design (Pydantic in schemas/)
  - Single source of truth for a pipeline run
"""

from dataclasses import dataclass, field
from typing import Optional, Any
from datetime import datetime, timezone


@dataclass
class AssistantState:
    """
    Tracks everything that happens during a single pipeline run.

    This object is created fresh for each user query and passed through
    every layer of the system. By the time the response is returned,
    this object contains a full audit trail of what happened.

    Attributes:
        user_query: The original input from the user (never modified)
        routing_decision: What the router decided ('calculator', 'weather', 'direct')
        tool_used: The tool that was executed (None if direct LLM)
        tool_output: The raw output from the tool (dict or None)
        final_response: The cleaned, validated response shown to the user
        is_valid: Whether the response passed validation
        error: Error message if something went wrong (None = success)
        retry_count: How many retries were needed (0 = success on first try)
        created_at: Timestamp of when this pipeline run started
    """

    # Input
    user_query: str

    # Routing
    routing_decision: Optional[str] = None

    # Tool execution
    tool_used: Optional[str] = None
    tool_output: Optional[Any] = None

    # Output
    final_response: Optional[str] = None
    is_valid: bool = False

    # Error tracking
    error: Optional[str] = None
    retry_count: int = 0

    # Metadata
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        """
        Serialize the full state to a dictionary.
        Useful for logging, debugging, and future database storage.
        """
        return {
            "user_query": self.user_query,
            "routing_decision": self.routing_decision,
            "tool_used": self.tool_used,
            "tool_output": self.tool_output,
            "final_response": self.final_response,
            "is_valid": self.is_valid,
            "error": self.error,
            "retry_count": self.retry_count,
            "created_at": self.created_at,
        }

    def mark_success(self) -> None:
        """Mark this pipeline run as successfully validated."""
        self.is_valid = True
        self.error = None

    def mark_failure(self, reason: str) -> None:
        """Record a failure and the reason."""
        self.is_valid = False
        self.error = reason

    def increment_retry(self) -> None:
        """Increment the retry counter."""
        self.retry_count += 1

    def __repr__(self) -> str:
        return (
            f"AssistantState("
            f"tool={self.tool_used!r}, "
            f"valid={self.is_valid}, "
            f"retries={self.retry_count}, "
            f"error={self.error!r})"
        )
