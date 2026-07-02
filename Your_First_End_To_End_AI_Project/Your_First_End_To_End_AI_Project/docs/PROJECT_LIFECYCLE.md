# 🔄 The Project Lifecycle — From Idea to Interview

> The 7-step process that separates hobby projects from portfolio-grade work.
> This is the meta-skill that Episode 4 teaches.

---

## Why Process Matters More Than Code

You can write perfect Python and still have a project that impresses nobody.

The difference between a project that gets ignored and one that gets you hired is not the code quality — it's the **process visible around the code**: clear scope, clean architecture, working tests, strong documentation, and a story you can tell.

This guide walks through the exact lifecycle used to build this repo.

---

## Step 1: Scope — Define the Problem

Before writing a single line of code, answer these questions:

**What problem does this solve?**
> An AI assistant that can decide when to use tools, call external APIs, validate outputs, remember conversation context, and present results through a web interface.

**Who is this for?**
> AI engineering students who want a portfolio project that demonstrates real system design.

**What is the MVP (Minimum Viable Product)?**
> A working assistant with at least 2 tools, validation, and a Streamlit UI. No authentication, no database, no deployment.

**What is explicitly out of scope?**
> User accounts, persistent memory across sessions, fine-tuning, multi-user support, production deployment.

### Why Scoping Matters

Most beginners skip this step and start building. They add features randomly, never ship, and end up with a bloated codebase that doesn't do one thing well.

A scoped project ships. An unscoped project doesn't.

**In interviews, say:**
> *"I scoped the project before building. The MVP was a 4-tool assistant with a Streamlit UI, conversation memory, and validation. I explicitly chose not to add authentication or persistence — those would be Episode 6 concerns."*

---

## Step 2: Architect — Design Before Building

Draw the system before coding it. You don't need fancy tools — a text diagram is enough.

```
UI Layer (Streamlit)
       ↓
Conversation Manager (session state)
       ↓
Router (LLM classifies intent)
       ↓
Tool Execution OR Direct LLM
       ↓
Validation (Pydantic schemas, retry)
       ↓
State Update + Response
```

### Key Architecture Decisions for This Project

| Decision | Rationale |
|---|---|
| Separate router from tools | Single Responsibility — router decides, tools execute |
| Conversation manager outside the LLM | LLMs are stateless — memory must be engineered externally |
| Pydantic at every boundary | Catch bad data early, not deep in business logic |
| Tool registry as a dict | Open/Closed Principle — add tools without changing the router |
| Streamlit for UI | Fastest path from backend to visual product in Python |

**In interviews, say:**
> *"I separated the conversation manager from the router because the LLM is stateless — it doesn't remember previous turns. The conversation manager injects relevant context at routing time, but the router itself remains stateless and testable."*

---

## Step 3: Build — Milestones, Not Features

Never build everything at once. Use milestones:

| Milestone | What Ships | How to Verify |
|---|---|---|
| 1 | CLI assistant with calculator + weather | `python run.py` → tools work |
| 2 | Add conversation history | Ask "what did I ask first?" → correct recall |
| 3 | Add Wikipedia tool | "Tell me about BERT" → factual summary |
| 4 | Add unit converter | "100F to C" → 37.78 |
| 5 | Streamlit UI | `streamlit run` → chat interface works |
| 6 | Tests + docs | `pytest tests/ -v` → all pass |

### Why Milestones Matter

Each milestone is a **working, demonstrable checkpoint**. If you get stuck at Milestone 4, you still have a working project from Milestone 3. You can commit, push, and show it.

Random feature-building means you might have 10 half-finished features and nothing that works.

**For LinkedIn build-in-public posts:** each milestone = one post. Six milestones = six posts = six weeks of content.

---

## Step 4: Test — Prove It Works

Three levels of testing in this project:

### Unit Tests
Test one component in isolation.
```python
def test_fahrenheit_to_celsius():
    result = converter_run("Convert 100 F to C")
    assert result["result"] == pytest.approx(37.78, rel=0.01)
```

### Mock Tests
Test components that depend on external APIs without making real calls.
```python
@patch("app.router.call_llm", return_value="calculator")
def test_routes_to_calculator(self, mock_llm):
    # No real API call — fast, free, deterministic
```

### Integration Tests
Test the full pipeline end-to-end.
```python
def test_conversation_records_turns(self):
    # Run the full pipeline and verify the conversation manager updated
```

**In interviews, say:**
> *"I tested tools in isolation with unit tests, mocked the LLM for router tests to keep them fast and free, and wrote integration tests to verify the full pipeline including conversation state."*

---

## Step 5: Document — Make It Undeniable

A README is your project's first impression. It has 10 seconds to convince someone to keep scrolling.

### What a Strong README Contains

1. **One-line description** — what this does
2. **Why it matters** — not what it is, but why anyone should care
3. **Architecture diagram** — shows you think in systems
4. **Quick start** — 4 commands to run it
5. **Example usage** — show, don't tell
6. **What I learned** — reflection = maturity
7. **Tech stack** — with rationale, not just logos

### What a Weak README Looks Like

> "This is my chatbot project. It uses Python and OpenAI. Run main.py."

That tells a hiring manager nothing about your engineering ability.

---

## Step 6: Deploy — Give It a URL

A project that only runs on your laptop is a demo. A project with a URL is a product.

Deployment options for this project:

| Platform | Effort | Cost | Best For |
|---|---|---|---|
| Streamlit Cloud | 5 minutes | Free | Fastest path to a live URL |
| Railway | 15 minutes | Free tier | More control |
| Render | 15 minutes | Free tier | Good for APIs |
| Fly.io | 30 minutes | Free tier | Docker-based |

See [`DEPLOYMENT.md`](DEPLOYMENT.md) for step-by-step instructions.

---

## Step 7: Tell the Story — LinkedIn + Interviews

The project is done. Now you need to tell people about it.

### LinkedIn Post Template

```
I stopped building chatbots. I started shipping AI systems.

This week I built [project name] — a [one-sentence description].

What makes it different from a tutorial project:
→ [Feature 1 + why it matters]
→ [Feature 2 + why it matters]
→ [Feature 3 + why it matters]

The biggest thing I learned: [key insight]

GitHub: [link]

If you're learning AI engineering, this is the layer worth focusing on next.
```

### Interview Answer Template

> "I built [project] to demonstrate [engineering skill]. The core challenge was [problem]. I solved it by [approach]. The system has [features]. I tested it with [testing strategy]. The main thing I learned was [insight]."

---

## The Meta-Lesson

The 7 steps above are not just for this project. They apply to every project you'll ever build — at school, at work, or for your portfolio.

```
Scope → Architect → Build → Test → Document → Deploy → Tell
```

Master this process and every project you touch will be stronger than 90% of what's on GitHub.

---

*Back to [README](../README.md) · [Concepts](CONCEPTS.md) · [Interview Prep](INTERVIEW_PREP.md)*
