"""
llm_client.py — LLM API Wrapper
=================================
AI Engineering Roadmap 2026 · Episode 3

Why does this file exist?

Engineering principle: isolate your external dependencies.

If you call the OpenAI API directly in 10 different files, and then
OpenAI changes their API (or you want to switch to Anthropic), you have
to change 10 files.

Instead, all LLM calls go through here. When something changes, you
change ONE file.

This is called the Adapter Pattern — a fundamental software engineering
concept you'll use throughout your career.

Key concepts demonstrated:
  - Adapter / wrapper pattern
  - Separation of concerns
  - Retry logic (with exponential backoff)
  - Clean error handling
  - Easy LLM provider swapping
"""

import time
import os
from openai import OpenAI
from app.utils.logger import get_logger

logger = get_logger(__name__)

# How many times to retry on transient failures (rate limits, network issues)
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 2


def call_llm(
    prompt: str,
    system_prompt: str = "You are a helpful, concise AI assistant.",
    model: str = None,
    max_tokens: int = 1000,
    temperature: float = 0.7,
) -> str:
    """
    Make a call to the LLM API and return the response text.

    This function handles:
      - Model selection from config
      - Retry on transient errors
      - Clean error propagation on permanent failures

    Args:
        prompt: The user message / instruction for the LLM
        system_prompt: The system-level instruction for the LLM
        model: Override the default model (optional)
        max_tokens: Maximum tokens in the response
        temperature: 0 = deterministic, 1 = creative

    Returns:
        The LLM's response as a plain string

    Raises:
        RuntimeError: If all retries fail
    """
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    selected_model = model or os.environ.get("LLM_MODEL", "gpt-4o-mini")

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt},
    ]

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.debug(f"LLM call attempt {attempt}/{MAX_RETRIES} | model={selected_model}")

            response = client.chat.completions.create(
                model=selected_model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )

            content = response.choices[0].message.content
            logger.debug(f"LLM response received ({len(content)} chars)")
            return content

        except Exception as e:
            error_str = str(e)

            # Detect rate limit errors — worth retrying
            if "rate_limit" in error_str.lower() or "429" in error_str:
                wait = RETRY_DELAY_SECONDS * attempt
                logger.warning(f"Rate limit hit. Waiting {wait}s before retry...")
                time.sleep(wait)
                continue

            # Auth errors — not worth retrying
            if "auth" in error_str.lower() or "401" in error_str or "403" in error_str:
                logger.error("Authentication error — check your OPENAI_API_KEY in .env")
                raise RuntimeError(f"LLM authentication failed: {e}") from e

            # Other errors — retry with delay
            if attempt < MAX_RETRIES:
                logger.warning(f"LLM call failed (attempt {attempt}): {e}. Retrying...")
                time.sleep(RETRY_DELAY_SECONDS)
            else:
                logger.error(f"All {MAX_RETRIES} LLM attempts failed.")
                raise RuntimeError(f"LLM call failed after {MAX_RETRIES} retries: {e}") from e

    raise RuntimeError("LLM call failed — exhausted all retries.")


# ---------------------------------------------------------------------------
# Anthropic alternative (swap this in by changing the function above)
# ---------------------------------------------------------------------------
# If you want to use Claude instead of OpenAI, replace call_llm with this:
#
# import anthropic
#
# def call_llm(prompt, system_prompt="You are a helpful assistant.",
#              model=None, max_tokens=1000, temperature=0.7):
#     client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
#     selected_model = model or "claude-sonnet-4-6"
#     message = client.messages.create(
#         model=selected_model,
#         max_tokens=max_tokens,
#         messages=[{"role": "user", "content": prompt}],
#         system=system_prompt,
#     )
#     return message.content[0].text
