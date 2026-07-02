"""
schemas/tool_schema.py — Tool Input/Output Schemas
====================================================
AI Engineering Roadmap 2026 · Episode 3

Define the data contracts for tool inputs and outputs.
Every tool call passes through these schemas.
"""

from typing import Optional, Any
from pydantic import BaseModel, field_validator


class ToolInput(BaseModel):
    """Validated input that gets passed to a tool."""

    tool_name: str
    query: str

    @field_validator("query")
    @classmethod
    def query_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Tool query cannot be empty.")
        return v.strip()

    @field_validator("tool_name")
    @classmethod
    def tool_name_must_be_known(cls, v: str) -> str:
        allowed = {"calculator", "weather", "direct"}
        if v not in allowed:
            raise ValueError(f"Unknown tool: {v!r}. Must be one of {allowed}")
        return v


class ToolOutput(BaseModel):
    """Validated output returned by a tool."""

    tool_name: str
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None

    @field_validator("data", mode="before")
    @classmethod
    def data_required_on_success(cls, v: Any, info: Any) -> Any:
        # Access other field values through info.data
        return v
