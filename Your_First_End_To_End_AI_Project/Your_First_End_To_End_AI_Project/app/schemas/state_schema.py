"""
schemas/state_schema.py — State Schema
========================================
AI Engineering Roadmap 2026 · Episode 3

Pydantic version of the system state.
Used for serialisation, logging, and future database persistence.
"""

from typing import Optional, Any
from pydantic import BaseModel


class StateSnapshot(BaseModel):
    """
    Immutable snapshot of the AssistantState at a point in time.
    Use for logging, auditing, or storing run history in a database.
    """

    user_query: str
    routing_decision: Optional[str] = None
    tool_used: Optional[str] = None
    tool_output: Optional[Any] = None
    final_response: Optional[str] = None
    is_valid: bool = False
    error: Optional[str] = None
    retry_count: int = 0
    created_at: str

    class Config:
        frozen = True  # Snapshots are immutable
