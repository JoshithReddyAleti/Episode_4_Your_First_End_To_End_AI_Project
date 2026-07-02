"""
router.py — Routing Decision Layer (Episode 4)
================================================
AI Engineering Roadmap 2026 · Episode 4

Updated from Episode 3:
  - Now accepts conversation_context parameter
  - Routes to 4 tools (added wikipedia, converter)
  - Conversation history injected into routing prompt
"""

import json
from app.llm_client import call_llm
from app.state import AssistantState
from app.tools import TOOL_REGISTRY
from app.utils.logger import get_logger

logger = get_logger(__name__)

ROUTING_OPTIONS = ["calculator", "weather", "wikipedia", "converter", "direct"]


def route_query(user_query: str, state: AssistantState, conversation_context: str = "") -> dict:
    """
    Decide how to handle the user query and execute accordingly.

    Args:
        user_query: The user's input string
        state: The current AssistantState object
        conversation_context: Recent conversation history for context-aware routing

    Returns:
        A dict with at minimum a 'final_response' key
    """
    logger.info("Routing query...")

    routing_decision = _get_routing_decision(user_query, conversation_context)
    logger.info(f"Routing decision: {routing_decision}")
    state.routing_decision = routing_decision

    if routing_decision in TOOL_REGISTRY:
        return _execute_tool(routing_decision, user_query, state)
    else:
        return _execute_direct(user_query, state, conversation_context)


def _get_routing_decision(user_query: str, conversation_context: str = "") -> str:
    with open("app/prompts/routing_prompt.txt", "r") as f:
        prompt_template = f.read()

    prompt = prompt_template.format(
        options=", ".join(ROUTING_OPTIONS),
        query=user_query,
        conversation_context=conversation_context or "(no previous conversation)",
    )

    try:
        raw = call_llm(prompt, max_tokens=20, temperature=0)
        decision = raw.strip().lower()

        if decision not in ROUTING_OPTIONS:
            logger.warning(f"Unexpected routing decision: {decision!r}. Falling back to 'direct'.")
            return "direct"
        return decision
    except Exception as e:
        logger.error(f"Routing LLM call failed: {e}. Falling back to 'direct'.")
        return "direct"


def _execute_tool(tool_name: str, user_query: str, state: AssistantState) -> dict:
    tool_fn = TOOL_REGISTRY[tool_name]
    state.tool_used = tool_name
    logger.info(f"Executing tool: {tool_name}")

    try:
        tool_output = tool_fn(user_query)
        state.tool_output = tool_output

        final_response = _generate_response_from_tool(user_query, tool_name, tool_output)
        state.final_response = final_response

        return {"tool_output": tool_output, "final_response": final_response}
    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
        state.error = str(e)
        state.tool_output = None
        return {
            "tool_output": None,
            "final_response": f"I tried to use the {tool_name} tool but encountered an error: {e}"
        }


def _execute_direct(user_query: str, state: AssistantState, conversation_context: str = "") -> dict:
    logger.info("Answering directly via LLM.")
    state.tool_used = None

    context = ""
    if conversation_context:
        context = f"\n\nRecent conversation for context:\n{conversation_context}\n\n"

    prompt = f"{context}Answer this clearly and concisely:\n{user_query}"

    try:
        response = call_llm(prompt, max_tokens=500)
        state.final_response = response
        return {"final_response": response}
    except Exception as e:
        logger.error(f"Direct LLM call failed: {e}")
        state.error = str(e)
        return {"final_response": f"I encountered an error generating a response: {e}"}


def _generate_response_from_tool(query: str, tool_name: str, tool_output: dict) -> str:
    context = (
        f"The user asked: {query}\n"
        f"You used the {tool_name} tool and got this data: {json.dumps(tool_output)}\n"
        f"Write a clear, concise, friendly response using this data."
    )
    try:
        return call_llm(context, max_tokens=300)
    except Exception as e:
        logger.error(f"Response generation failed: {e}")
        return str(tool_output)
