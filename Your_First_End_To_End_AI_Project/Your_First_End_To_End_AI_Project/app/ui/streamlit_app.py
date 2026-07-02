"""
ui/streamlit_app.py — Streamlit Web Interface
===============================================
AI Engineering Roadmap 2026 · Episode 4

This is the layer that turns your backend pipeline into a product.

Why Streamlit?
  - Zero frontend knowledge needed (Python only)
  - Looks professional instantly
  - Great for portfolios and demos
  - Used in real AI teams for internal tools

What this UI provides:
  - Chat interface with message history
  - Sidebar with session stats and tool usage
  - Conversation export as JSON
  - Transparent tool usage display
  - New session button

Run with:
  streamlit run app/ui/streamlit_app.py
"""

import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
from app.router import route_query
from app.state import AssistantState
from app.validator import validate_response
from app.conversation import ConversationManager
from app.utils.config import load_config
from app.utils.logger import get_logger

logger = get_logger(__name__)


def init_session():
    """Initialise Streamlit session state on first load."""
    if "conversation" not in st.session_state:
        st.session_state.conversation = ConversationManager(max_context_turns=5)
    if "messages" not in st.session_state:
        st.session_state.messages = []


def run_pipeline(user_query: str) -> str:
    """
    Run the full AI pipeline for a user query.
    Returns the final response string.
    """
    state = AssistantState(user_query=user_query)
    conversation = st.session_state.conversation

    # Inject conversation context into routing
    context = conversation.get_context_for_routing()
    result = route_query(user_query, state, conversation_context=context)

    # Validate
    validated = validate_response(result, state)

    # Record the turn
    conversation.add_turn(
        user_query=user_query,
        routing_decision=state.routing_decision,
        tool_used=state.tool_used,
        tool_output=state.tool_output,
        assistant_response=validated.final_response,
        is_valid=validated.is_valid,
        error=state.error,
    )

    return validated.final_response, state.tool_used


def render_sidebar():
    """Render the sidebar with session stats and controls."""
    conversation = st.session_state.conversation

    st.sidebar.title("🤖 AI Assistant")
    st.sidebar.markdown("*AI Engineering Roadmap 2026 — Episode 4*")
    st.sidebar.divider()

    # Session stats
    st.sidebar.markdown("### 📊 Session Stats")
    col1, col2 = st.sidebar.columns(2)
    col1.metric("Turns", conversation.get_turn_count())
    col2.metric("Success", f"{conversation.get_success_rate()}%")

    # Tool usage breakdown
    tool_freq = conversation.get_tool_frequency()
    if tool_freq:
        st.sidebar.markdown("### 🔧 Tools Used")
        for tool, count in sorted(tool_freq.items(), key=lambda x: -x[1]):
            emoji = {"calculator": "🧮", "weather": "🌤️", "wikipedia": "📖", "converter": "📏"}.get(tool, "🔧")
            st.sidebar.markdown(f"{emoji} **{tool}** — {count}x")

    st.sidebar.divider()

    # Available tools
    st.sidebar.markdown("### 💡 Try asking")
    st.sidebar.markdown(
        "- *What's 25% of 480?*\n"
        "- *Weather in Tokyo?*\n"
        "- *Tell me about BERT*\n"
        "- *Convert 100F to Celsius*\n"
        "- *What did I ask first?*"
    )

    st.sidebar.divider()

    # Controls
    col_a, col_b = st.sidebar.columns(2)
    if col_a.button("🗑️ New Session", use_container_width=True):
        st.session_state.conversation = ConversationManager()
        st.session_state.messages = []
        st.rerun()

    if col_b.button("📥 Export JSON", use_container_width=True):
        json_export = conversation.export_json()
        st.sidebar.download_button(
            label="Download",
            data=json_export,
            file_name="conversation_export.json",
            mime="application/json",
        )


def main():
    """Main Streamlit app entry point."""
    st.set_page_config(
        page_title="AI Assistant — Episode 4",
        page_icon="🤖",
        layout="centered",
    )

    load_config()
    init_session()
    render_sidebar()

    # Main chat area
    st.title("🤖 AI Assistant")
    st.caption("Episode 4 — Your First End-to-End AI Project  ·  [AI Engineering Roadmap 2026](https://www.linkedin.com/newsletters/ai-engineering-roadmap-2026-7467249724752908288/)")

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("tool_used"):
                emoji = {"calculator": "🧮", "weather": "🌤️", "wikipedia": "📖", "converter": "📏"}.get(message["tool_used"], "🔧")
                st.caption(f"{emoji} Used tool: **{message['tool_used']}**")

    # Chat input
    if user_input := st.chat_input("Ask me anything..."):
        # Display user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response, tool_used = run_pipeline(user_input)
                    st.markdown(response)
                    if tool_used:
                        emoji = {"calculator": "🧮", "weather": "🌤️", "wikipedia": "📖", "converter": "📏"}.get(tool_used, "🔧")
                        st.caption(f"{emoji} Used tool: **{tool_used}**")
                except Exception as e:
                    response = f"Something went wrong: {e}"
                    tool_used = None
                    st.error(response)

        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "tool_used": tool_used,
        })

        st.rerun()


if __name__ == "__main__":
    main()
