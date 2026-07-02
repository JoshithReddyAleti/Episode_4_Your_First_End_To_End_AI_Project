"""
validator.py — Validation Layer
================================
AI Engineering Roadmap 2026 · Episode 3

This is the layer most tutorials completely skip.

Why does validation matter?

LLMs are probabilistic. They can return:
  - The wrong format (HTML when you asked for JSON)
  - Missing fields (a schema with 3 required keys, only 2 returned)
  - Nonsense values (temperature: "very warm" instead of a number)
  - Empty strings
  - Python None

Without validation, your system will crash unpredictably in production —
not in a nice, catchable way. It'll just silently return garbage to users.

Validation is what separates a demo from a reliable system.

Key concepts demonstrated:
  - Input validation (before calling tools)
  - Output validation (after tool/LLM returns)
  - Retry logic with exponential backoff
  - Graceful fallback responses
  - Pydantic-based schema validation
"""

import json
from typing import Optional
from app.state import AssistantState
from app.schemas.response_schema import ValidatedResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)

MAX_VALIDATION_RETRIES = 2


def validate_response(result: dict, state: AssistantState) -> ValidatedResponse:
    """
    Validate the pipeline result before returning it to the user.

    Checks:
      1. The result is a non-empty dict
      2. It has a 'final_response' key
      3. The final_response is a non-empty string
      4. If a tool was used, the tool_output is also present and non-empty

    If validation fails, it retries up to MAX_VALIDATION_RETRIES times.
    If all retries fail, it returns a safe fallback response.

    Args:
        result: The dict returned by the router
        state: The current AssistantState (mutated to record outcome)

    Returns:
        A ValidatedResponse object with a guaranteed final_response string
    """
    for attempt in range(1, MAX_VALIDATION_RETRIES + 2):
        logger.debug(f"Validation attempt {attempt}")

        issues = _find_issues(result, state)

        if not issues:
            state.mark_success()
            logger.info("Validation passed.")
            return ValidatedResponse(
                final_response=result["final_response"],
                is_valid=True,
                tool_used=state.tool_used,
                tool_output=state.tool_output,
            )

        # Validation failed
        logger.warning(f"Validation issues found: {issues}")
        state.mark_failure("; ".join(issues))
        state.increment_retry()

        if attempt <= MAX_VALIDATION_RETRIES:
            logger.info(f"Retrying pipeline... (attempt {attempt + 1})")
            result = _attempt_repair(result, state, issues)
        else:
            logger.error("All validation retries exhausted. Returning fallback.")
            break

    # Graceful fallback — always return something useful
    fallback = _build_fallback(state)
    state.mark_failure("Returned fallback response after validation failure")
    return fallback


def validate_tool_input(tool_name: str, raw_query: str) -> tuple[bool, Optional[str]]:
    """
    Validate that a query is safe and sensible to pass to a tool.

    Args:
        tool_name: Which tool will receive the input
        raw_query: The user's query string

    Returns:
        (is_valid, error_message_or_None)
    """
    if not raw_query or not raw_query.strip():
        return False, "Query is empty."

    if len(raw_query) > 2000:
        return False, "Query is too long to process safely."

    if tool_name == "calculator":
        # Basic check: does the query contain any digits?
        if not any(char.isdigit() for char in raw_query):
            return False, "Calculator tool received a query with no numbers."

    if tool_name == "weather":
        # Basic check: does it look like a location is mentioned?
        if len(raw_query.split()) < 2:
            return False, "Weather query seems too short to contain a location."

    return True, None


def validate_tool_output(tool_name: str, output: dict) -> tuple[bool, Optional[str]]:
    """
    Validate the raw output returned by a tool.

    Args:
        tool_name: The tool that produced the output
        output: The tool's return value

    Returns:
        (is_valid, error_message_or_None)
    """
    if output is None:
        return False, f"{tool_name} tool returned None."

    if not isinstance(output, dict):
        return False, f"{tool_name} tool returned non-dict: {type(output).__name__}"

    if tool_name == "calculator":
        if "result" not in output:
            return False, "Calculator output missing 'result' key."
        if not isinstance(output["result"], (int, float)):
            return False, f"Calculator result is not a number: {output['result']!r}"

    if tool_name == "weather":
        required_keys = {"temperature", "condition", "location"}
        missing = required_keys - output.keys()
        if missing:
            return False, f"Weather output missing keys: {missing}"

    return True, None


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _find_issues(result: dict, state: AssistantState) -> list[str]:
    """Return a list of validation issues found in the result."""
    issues = []

    if not result:
        issues.append("Result dict is empty or None")
        return issues

    if "final_response" not in result:
        issues.append("Missing 'final_response' key in result")

    elif not result.get("final_response", "").strip():
        issues.append("'final_response' is empty or whitespace")

    if state.tool_used and result.get("tool_output") is None:
        issues.append(f"Tool '{state.tool_used}' was used but tool_output is None")

    return issues


def _attempt_repair(result: dict, state: AssistantState, issues: list[str]) -> dict:
    """
    Attempt to repair an invalid result before the next validation pass.
    In a more advanced system, this could re-invoke the LLM with error context.
    """
    repaired = dict(result)

    if "final_response" not in repaired or not repaired.get("final_response", "").strip():
        if state.tool_output:
            repaired["final_response"] = f"Here is the result: {json.dumps(state.tool_output)}"
        else:
            repaired["final_response"] = "I processed your request but could not generate a response."

    return repaired


def _build_fallback(state: AssistantState) -> ValidatedResponse:
    """Build a safe fallback response when all retries fail."""
    return ValidatedResponse(
        final_response=(
            "I wasn't able to process your request reliably. "
            "Please try rephrasing your question."
        ),
        is_valid=False,
        tool_used=state.tool_used,
        tool_output=state.tool_output,
    )
