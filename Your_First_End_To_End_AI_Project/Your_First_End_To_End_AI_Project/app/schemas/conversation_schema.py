"""
schemas/conversation_schema.py — Conversation Turn Schema
==========================================================
AI Engineering Roadmap 2026 · Episode 4

Pydantic schema for conversation turns.
Used for validation when exporting or storing conversations.
"""
from typing import Optional, Any
from pydantic import BaseModel

class ConversationTurnSchema(BaseModel):
    turn_number: int
    user_query: str
    routing_decision: Optional[str] = None
    tool_used: Optional[str] = None
    assistant_response: Optional[str] = None
    is_valid: bool = False
    error: Optional[str] = None
    timestamp: str

    class Config:
        frozen = True
