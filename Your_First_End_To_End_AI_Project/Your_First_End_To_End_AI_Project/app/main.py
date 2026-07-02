"""
main.py — CLI Entry Point (Episode 4)
=======================================
AI Engineering Roadmap 2026 · Episode 4

Updated from Episode 3:
  - Includes conversation history
  - Shows tool usage in responses
  - Supports multi-turn context
"""

import sys
from app.router import route_query
from app.state import AssistantState
from app.validator import validate_response
from app.conversation import ConversationManager
from app.utils.logger import get_logger
from app.utils.config import load_config

logger = get_logger(__name__)


def main():
    load_config()
    conversation = ConversationManager(max_context_turns=5)

    print("\n" + "=" * 60)
    print("  🤖  AI Assistant — Episode 4")
    print("  AI Engineering Roadmap 2026")
    print("=" * 60)
    print("  Tools: 🧮 Calculator · 🌤️ Weather · 📖 Wikipedia · 📏 Converter")
    print("  Try: 'What is 25% of 480?' or 'Convert 100F to C'")
    print("  Type 'quit' to exit, 'history' to see conversation log")
    print("=" * 60 + "\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            sys.exit(0)

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break
        if user_input.lower() == "history":
            print(f"\n{conversation.export_json()}\n")
            continue

        try:
            state = AssistantState(user_query=user_input)
            context = conversation.get_context_for_routing()
            result = route_query(user_input, state, conversation_context=context)
            validated = validate_response(result, state)

            tool_info = ""
            if state.tool_used:
                emoji = {"calculator": "🧮", "weather": "🌤️", "wikipedia": "📖", "converter": "📏"}.get(state.tool_used, "🔧")
                tool_info = f" {emoji} [{state.tool_used}]"

            conversation.add_turn(
                user_query=user_input,
                routing_decision=state.routing_decision,
                tool_used=state.tool_used,
                tool_output=state.tool_output,
                assistant_response=validated.final_response,
                is_valid=validated.is_valid,
                error=state.error,
            )

            print(f"\nAssistant{tool_info}: {validated.final_response}\n")

        except Exception as e:
            logger.error(f"Pipeline error: {e}", exc_info=True)
            print(f"\n[Error] Something went wrong: {e}\n")


if __name__ == "__main__":
    main()
