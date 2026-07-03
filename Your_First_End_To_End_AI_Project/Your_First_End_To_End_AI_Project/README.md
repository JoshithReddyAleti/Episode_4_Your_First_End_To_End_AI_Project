# 🚀 Your First End-to-End AI Project

> **Episode 4 of the [AI Engineering Roadmap 2026](https://www.linkedin.com/newsletters/ai-engineering-roadmap-2026-7467249724752908288/) Newsletter Series**
>
> *"A project without a story is just code. A story without code is just talk. You need both."*

---

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?style=flat-square)
![Pytest](https://img.shields.io/badge/Tested-pytest-0A9EDC?style=flat-square&logo=pytest&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-22C55E?style=flat-square)
![Episode](https://img.shields.io/badge/Episode-4%20of%2010-534AB7?style=flat-square)

**[📖 Newsletter](https://www.linkedin.com/newsletters/ai-engineering-roadmap-2026-7467249724752908288/) · [⬅️ Episode 3](https://github.com/JoshithReddyAleti/Building_AI_Project-Blueprint_for_Begin) · [🗺️ Roadmap](docs/ROADMAP.md) · [🧪 Tests](tests/)**

</div>

---

## 🎯 What Is This?

Episode 3 taught you how to build the engine — tool calling, validation, structured outputs.

**Episode 4 teaches you how to ship the car.**

This is the episode where everything comes together: a working AI assistant with a real UI, conversation memory, multiple tools, polished documentation, and a deployment strategy. The kind of project that makes a hiring manager stop scrolling.

```
Episode 3: "I built a tool-calling pipeline"
Episode 4: "I shipped a working AI product with a UI, memory, tests, and docs"
```

That's the difference between a learner and an engineer.

---

## 🧠 The Core Lesson

Most beginners build projects. Engineers ship products.

The gap between them is not talent — it's **process**:

| What Beginners Do | What Engineers Do |
|---|---|
| Start coding immediately | Scope the project first |
| Build features randomly | Build in milestones |
| Skip the UI | Add a real interface |
| No conversation memory | Session-aware state |
| No docs | README that tells a story |
| "It works on my machine" | Tests + deployment plan |
| Describe the tech stack | Describe the engineering decisions |

This project teaches the engineering side. Every file, every decision, every doc exists because it answers a question a hiring manager would ask.

---

## 🏗️ Architecture

This project extends the Episode 3 pipeline with three new layers: a UI, conversation memory, and an expanded tool set.

```
┌──────────────────────────────────────────────────────────────┐
│                    STREAMLIT UI LAYER                         │
│   User types a query → sees response in real time            │
│   Conversation history visible in sidebar                    │
│   Tool usage displayed transparently                         │
└───────────────────────────┬──────────────────────────────────┘
                            │
┌───────────────────────────▼──────────────────────────────────┐
│                CONVERSATION MANAGER                           │
│   Maintains session history                                  │
│   Tracks all queries, tools used, and responses              │
│   Provides context for follow-up questions                   │
└───────────────────────────┬──────────────────────────────────┘
                            │
┌───────────────────────────▼──────────────────────────────────┐
│                    ROUTING LAYER                              │
│   LLM classifies intent → selects tool or direct response   │
│   Now with conversation context for smarter routing          │
└──────┬──────────────────────────────────┬────────────────────┘
       │                                   │
       ▼                                   ▼
┌─────────────┐              ┌──────────────────────────┐
│  Direct LLM │              │    TOOL EXECUTION        │
│  Response   │              │  🧮 Calculator            │
└─────┬───────┘              │  🌤️ Weather API           │
      │                      │  📖 Wikipedia Summary     │
      │                      │  📏 Unit Converter        │
      │                      └────────────┬─────────────┘
      │                                   │
      └──────────────┬────────────────────┘
                     │
        ┌────────────▼───────────────┐
        │   VALIDATION LAYER         │
        │   Schema check → Retry     │
        │   → Fallback → Log        │
        └────────────┬───────────────┘
                     │
        ┌────────────▼───────────────┐
        │   STATE + LOGGING          │
        │   Full audit trail         │
        │   Exportable as JSON       │
        └────────────────────────────┘
```

---

## 📁 Repository Structure

```
Your_First_End_To_End_AI_Project/
│
├── app/
│   ├── main.py                    # CLI entry point (still works without UI)
│   ├── router.py                  # LLM-based routing with conversation context
│   ├── llm_client.py              # LLM API wrapper with retry logic
│   ├── state.py                   # Pipeline state tracking
│   ├── validator.py               # Output validation + retry + fallback
│   ├── conversation.py            # NEW: Conversation history manager
│   │
│   ├── ui/
│   │   └── streamlit_app.py       # NEW: Full Streamlit UI
│   │
│   ├── prompts/
│   │   ├── routing_prompt.txt     # Intent classification prompt
│   │   └── response_prompt.txt    # Response generation prompt
│   │
│   ├── tools/
│   │   ├── __init__.py            # Tool registry
│   │   ├── calculator.py          # Arithmetic (from Ep3)
│   │   ├── weather_api.py         # Live weather (from Ep3)
│   │   ├── wikipedia_tool.py      # NEW: Wikipedia summary
│   │   └── unit_converter.py      # NEW: Unit conversion
│   │
│   ├── schemas/
│   │   ├── tool_schema.py         # Tool I/O contracts
│   │   ├── response_schema.py     # Final response contract
│   │   ├── state_schema.py        # State snapshot contract
│   │   └── conversation_schema.py # NEW: Conversation turn contract
│   │
│   └── utils/
│       ├── logger.py              # Structured logging
│       ├── config.py              # Env + API key management
│       └── helpers.py             # Shared utilities
│
├── tests/
│   ├── test_tools.py              # Unit tests for all 4 tools
│   ├── test_validator.py          # Validation logic tests
│   ├── test_router.py             # Routing decision tests
│   ├── test_conversation.py       # NEW: Conversation manager tests
│   └── test_end_to_end.py         # Full pipeline integration tests
│
├── examples/
│   ├── sample_inputs.md           # Example queries for each tool
│   ├── expected_outputs.md        # What correct outputs look like
│   └── sample_conversations.md    # NEW: Multi-turn example conversations
│
├── docs/
│   ├── ROADMAP.md                 # Full AI Engineering Roadmap 2026
│   ├── CONCEPTS.md                # Episode 4 concepts deep-dive
│   ├── INTERVIEW_PREP.md          # How to talk about this project
│   ├── PROJECT_LIFECYCLE.md       # NEW: The full lifecycle guide
│   └── DEPLOYMENT.md              # NEW: How to deploy this
│
├── .env.example
├── requirements.txt
├── run.py                         # CLI runner
├── run_ui.py                      # NEW: Streamlit launcher
├── CONTRIBUTING.md
├── CHANGELOG.md
└── LICENSE
```

---

## ⚡ Quick Start

### Option A: Streamlit UI (recommended)

```bash
git clone https://github.com/JoshithReddyAleti/Episode_4_Your_First_End_To_End_AI_Project.git
cd Your_First_End_To_End_AI_Project

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Add your OPENAI_API_KEY to .env

streamlit run app/ui/streamlit_app.py
```

### Option B: CLI mode

```bash
python run.py
```

---

## 💬 What You Can Do

```
You: What's 25% of 480?
🧮 [Calculator] → 120.0
Assistant: 25% of 480 is exactly 120.

You: What's the weather in London?
🌤️ [Weather API] → 14°C, Partly cloudy
Assistant: It's currently 14°C and partly cloudy in London.

You: Tell me about the Transformer architecture
📖 [Wikipedia] → Retrieved summary
Assistant: The Transformer is a deep learning architecture introduced in 2017...

You: Convert 100 Fahrenheit to Celsius
📏 [Unit Converter] → 37.78°C
Assistant: 100°F is 37.78°C.

You: What did I ask first?
💬 [Conversation Memory] → Recalled first query
Assistant: Your first question was about calculating 25% of 480.
```

---

## 🧩 What's New in Episode 4 (vs Episode 3)

| Feature | Episode 3 | Episode 4 |
|---|---|---|
| **UI** | CLI only | Streamlit web app |
| **Tools** | 2 (calculator, weather) | 4 (+Wikipedia, +unit converter) |
| **Memory** | None (stateless) | Session conversation history |
| **Context** | Single query | Multi-turn awareness |
| **Export** | None | Export conversation as JSON |
| **Observability** | Basic logging | Sidebar tool usage display |
| **Deployment** | None | Deployment guide included |

---

## 🗺️ The Project Lifecycle

This is the process Episode 4 teaches. Every serious project follows this:

```
1. SCOPE       → What problem does this solve? What's the MVP?
2. ARCHITECT   → What are the layers? How do they connect?
3. BUILD       → Milestones, not features. Ship incrementally.
4. TEST        → Unit tests, mock tests, integration tests.
5. DOCUMENT    → README, concepts, interview prep.
6. DEPLOY      → Make it accessible. Give it a URL.
7. TELL        → Write the story. LinkedIn post. Interview answer.
```

Most beginners do step 3 and skip everything else. This project walks you through all 7.

See [`docs/PROJECT_LIFECYCLE.md`](docs/PROJECT_LIFECYCLE.md) for the full guide.

---

## 🧪 Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_conversation.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=term-missing
```

---

## 🗺️ Milestones

Follow this progression to build the system step by step:

- [x] **Milestone 1** — Port Episode 3 pipeline (calculator + weather + validation)
- [x] **Milestone 2** — Add conversation history manager
- [x] **Milestone 3** — Add Wikipedia summary tool
- [x] **Milestone 4** — Add unit converter tool
- [x] **Milestone 5** — Build Streamlit UI
- [x] **Milestone 6** — Add conversation export + sidebar observability
- [x] **Milestone 7** — Full test suite + polished docs

---

## 💼 Resume Bullet Points

> **Option 1:** Built and shipped an end-to-end AI assistant with a Streamlit UI, 4-tool routing system, session memory, Pydantic validation, and full test coverage — demonstrating production-grade AI engineering from architecture to deployment.

> **Option 2:** Engineered a multi-tool LLM application with conversation history, structured outputs, retry logic, and a web interface — the kind of project that moves beyond demos into real system design.

> **Option 3:** Designed and documented the full lifecycle of an AI product — from project scoping and architecture through testing, deployment, and interview storytelling — with working code, tests, and a live UI.

---

## 🎤 Interview Story

> *"After building a backend tool-calling pipeline in Episode 3, I wanted to prove I could ship a complete product — not just a backend script. So I added a Streamlit UI, conversation memory, two more tools, and a full documentation and deployment strategy. The key engineering challenge was maintaining conversation context across turns while keeping the routing layer stateless — I solved this by separating the conversation manager from the router and injecting only relevant context at routing time. The project has 4 tools, Pydantic schema validation on every boundary, retry logic with graceful fallbacks, and full test coverage including mocked LLM calls."*

See [`docs/INTERVIEW_PREP.md`](docs/INTERVIEW_PREP.md) for the full guide.

---

## 🛠️ Tech Stack

| Category | Tool | Why |
|---|---|---|
| Language | Python 3.10+ | Industry standard for AI/ML |
| LLM API | OpenAI / Anthropic | Production-grade LLM access |
| UI | Streamlit | Fast, visual, portfolio-friendly |
| Validation | Pydantic v2 | Schema enforcement at every boundary |
| HTTP | Requests | External API calls |
| Env Mgmt | python-dotenv | Secure key management |
| Testing | pytest | Engineering maturity signal |
| Logging | Python logging | Observability |

---

## 📚 Part of the AI Engineering Roadmap 2026

| Episode | Topic | Link |
|---|---|---|
| 1 | What is an LLM really? | [View repo →](https://github.com/JoshithReddyAleti/Understanding_LLMs_From_The_Inside_Out) |
| 2 | Python for AI — what actually matters | [View repo →](https://github.com/JoshithReddyAleti/Python_For_AI_What_Actually_Matters) |
| 3 | Tool calling, APIs & validation | [View repo →](https://github.com/JoshithReddyAleti/Building_AI_Project-Blueprint_for_Begin) |
| **4** | **Your first end-to-end AI project** | **← You are here** |
| 5 | RAG — connecting AI to your data | Coming soon |

[📬 Subscribe to the newsletter](https://www.linkedin.com/newsletters/ai-engineering-roadmap-2026-7467249724752908288/) to get each episode as it drops.

---

## 📬 Not Subscribed Yet?

This repo is part of the **AI Engineering Roadmap 2026** — a free LinkedIn newsletter that walks you step by step through becoming an AI engineer in 2026. Each episode: a real project, a carousel, a concept guide, and interview prep.

**[→ Subscribe here. It's free.](https://www.linkedin.com/newsletters/ai-engineering-roadmap-2026-7467249724752908288/)**

---

<div align="center">

**If this helped you, give it a ⭐ — it helps other students find it.**

*Built with ❤️ for the AI Engineering Roadmap 2026 community*

[⬅️ Episode 3](https://github.com/JoshithReddyAleti/Building_AI_Project_Blueprint_for_Beginners) · [Newsletter](https://www.linkedin.com/newsletters/ai-engineering-roadmap-2026-7467249724752908288/) · [Episode 5 →](#)

</div>
