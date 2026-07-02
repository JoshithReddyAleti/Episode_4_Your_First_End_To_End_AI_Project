"""
schemas/response_schema.py — Response Schema
=============================================
AI Engineering Roadmap 2026 · Episode 3

Pydantic schemas define the contract for your data.

Why does this matter?

Without schemas:
  - Any dict can pass through your system
  - Missing fields only cause errors at runtime, deep in your code
  - Testing is guesswork

With schemas:
  - Data is validated at the boundary
  - Missing/wrong types raise immediate, clear errors
  - Your code can trust the data it receives

This is the same principle used in production APIs and microservices.
"""

from typing import Optional, Any
from pydantic import BaseModel, field_validator


class ValidatedResponse(BaseModel):
    """
    The final, validated response object returned to the user.

    This is the output contract for the entire pipeline.
    If validation passes, the caller gets one of these. Always.
    """

    final_response: str
    is_valid: bool
    tool_used: Optional[str] = None
    tool_output: Optional[Any] = None

    @field_validator("final_response")
    @classmethod
    def response_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("final_response cannot be empty.")
        return v.strip()

    class Config:
        frozen = False  # Allow mutation after creation if needed
