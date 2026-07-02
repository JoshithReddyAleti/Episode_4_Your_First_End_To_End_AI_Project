# 🧠 Key Concepts — Episode 4

> Deep-dive on every new concept introduced in this episode.

---

## 1. Session State vs Persistent State

**Session state** (this episode): Data lives in memory for the duration of one session. When the app restarts, it's gone. Streamlit's `st.session_state` and our `ConversationManager` are both session-scoped.

**Persistent state** (Episode 6): Data survives restarts — stored in a database, file, or external service. Needed for long-term memory, user profiles, and production systems.

**Why session first:** You have to understand how state works before you add persistence. Most bugs in stateful systems come from not understanding the lifecycle of data — when it's created, when it's updated, when it's lost.

---

## 2. Context Injection — How Conversation Memory Works

The LLM is stateless. It doesn't remember what you said 5 seconds ago. Every API call is independent.

So how does conversation memory work?

**Answer:** You inject the conversation history into the prompt.

```python
# What the router sends to the LLM:
"""
Previous conversation:
User: What's the weather in London?
Assistant [weather]: It's 14°C and partly cloudy in London.

User: What about Paris?
                       ↑ "what about" only makes sense with context above

Classify this query: What about Paris?
"""
```

Without the injected context, "What about Paris?" is meaningless. With it, the LLM knows the user is asking about weather in Paris.

**Engineering trade-off:** More context = better understanding but higher token cost. That's why `max_context_turns` exists — it limits how many recent turns are injected.

---

## 3. The UI Layer — Why It Changes Everything

A CLI tool and a Streamlit app do the same thing. But the perception is completely different:

| Dimension | CLI | Streamlit |
|---|---|---|
| First impression | "Looks like a script" | "Looks like a product" |
| Accessibility | Developers only | Anyone with a browser |
| Demo-ability | Hard to show in interviews | Easy to share a URL |
| Portfolio impact | Low | High |

**Streamlit is not the only option.** Gradio, Panel, and custom React apps work too. The point is: if your project has no interface, it's invisible to most people.

---

## 4. Tool Expansion — The Open/Closed Principle

Adding a tool in this architecture requires exactly 3 changes:

1. Create `app/tools/new_tool.py` with a `run(query: str) -> dict` function
2. Add one line to `app/tools/__init__.py`
3. Add one line to `app/prompts/routing_prompt.txt`

You do NOT change the router, the validator, the state, or the UI. They all work with any number of tools.

This is the **Open/Closed Principle**: the system is open for extension (add tools) and closed for modification (don't touch existing code).

**In interviews, say:**
> *"I designed the tool system using the Open/Closed Principle — adding a new tool requires creating one file and updating two lines, with zero changes to the router or validator."*

---

## 5. Separation of Concerns — The Full Picture

Episode 3 introduced separation of concerns. Episode 4 makes it concrete across more layers:

| Component | Responsibility | Knows About |
|---|---|---|
| `streamlit_app.py` | Display + user interaction | conversation, router |
| `conversation.py` | Track session history | Nothing else |
| `router.py` | Decide what to do | tools, llm_client |
| `tools/*.py` | Execute capabilities | Nothing else |
| `validator.py` | Check outputs | schemas |
| `state.py` | Track pipeline run | Nothing else |

Each component can be tested independently. Each can be replaced without affecting others.

---

## 6. Export and Observability

The "Export JSON" feature isn't just a nice-to-have. It demonstrates:

- **Audit trail thinking** — you can reconstruct what happened in any session
- **Debugging capability** — when something goes wrong, you have data
- **Production mindset** — real systems need observability

The exported JSON includes every turn, every tool used, success rates, and timestamps. In production, this data would go to a logging service.

---

*Back to [README](../README.md) · [Project Lifecycle](PROJECT_LIFECYCLE.md) · [Interview Prep](INTERVIEW_PREP.md)*
