"""
tools/calculator.py — Calculator Tool
=======================================
AI Engineering Roadmap 2026 · Episode 3

This tool handles arithmetic queries that the LLM should NOT
try to compute itself.

Why not just let the LLM do the math?

LLMs are bad at maths. They pattern-match on training data.
For "25% of 480" they'll often get 120 — but ask "17.3% of 9,847"
and the odds of a correct answer drop significantly.

A calculator tool is always correct. That's the point.

This is a clean, self-contained tool:
  - Input: a natural language query string
  - Processing: extract numbers and operation, compute the result
  - Output: a validated dict with a 'result' key

Key concepts demonstrated:
  - Tool isolation (no LLM inside the tool itself)
  - Regex-based extraction
  - Error handling within the tool
  - Structured dict return (not raw text)
"""

import re
from app.utils.logger import get_logger

logger = get_logger(__name__)


def run(query: str) -> dict:
    """
    Parse and evaluate an arithmetic expression from a natural language query.

    Handles:
      - Percentages: "What is 25% of 480?"
      - Addition: "What is 100 + 250?"
      - Subtraction: "What is 500 minus 180?"
      - Multiplication: "What is 12 times 13?"
      - Division: "What is 144 divided by 12?"

    Args:
        query: A natural language string containing an arithmetic question

    Returns:
        dict with keys:
          - 'result': float result of the calculation
          - 'expression': the extracted expression string
          - 'query': the original query
          - 'error': None on success, error message on failure
    """
    logger.info(f"Calculator tool received: {query!r}")

    try:
        result, expression = _parse_and_calculate(query)

        output = {
            "result": result,
            "expression": expression,
            "query": query,
            "error": None,
        }

        logger.info(f"Calculator result: {expression} = {result}")
        return output

    except Exception as e:
        logger.error(f"Calculator error: {e}")
        return {
            "result": None,
            "expression": None,
            "query": query,
            "error": str(e),
        }


def _parse_and_calculate(query: str) -> tuple[float, str]:
    """
    Extract numbers and operation from the query and compute the result.

    Returns:
        (result, expression_string)

    Raises:
        ValueError: if the query cannot be parsed
        ZeroDivisionError: if division by zero is attempted
    """
    query_lower = query.lower()

    # Percentage: "X% of Y" or "X percent of Y"
    pct_match = re.search(
        r"(\d+(?:\.\d+)?)\s*(?:%|percent)\s+of\s+(\d+(?:,\d{3})*(?:\.\d+)?)",
        query_lower
    )
    if pct_match:
        pct = float(pct_match.group(1))
        total = float(pct_match.group(2).replace(",", ""))
        result = (pct / 100) * total
        return result, f"{pct}% of {total}"

    # Extract all numbers in the query
    numbers = re.findall(r"-?\d+(?:,\d{3})*(?:\.\d+)?", query)
    nums = [float(n.replace(",", "")) for n in numbers]

    if len(nums) < 2:
        raise ValueError(
            f"Could not extract two numbers from query: {query!r}. "
            f"Found: {nums}"
        )

    a, b = nums[0], nums[1]

    # Detect operation from keywords
    if any(w in query_lower for w in ("plus", "add", "+")):
        return a + b, f"{a} + {b}"
    if any(w in query_lower for w in ("minus", "subtract", "-")):
        return a - b, f"{a} - {b}"
    if any(w in query_lower for w in ("times", "multiply", "multiplied", "×", "*")):
        return a * b, f"{a} × {b}"
    if any(w in query_lower for w in ("divided", "divide", "÷", "/")):
        if b == 0:
            raise ZeroDivisionError("Cannot divide by zero.")
        return a / b, f"{a} ÷ {b}"

    # Default: assume multiplication if no operator found
    logger.warning("No operator found — defaulting to multiplication.")
    return a * b, f"{a} × {b}"
