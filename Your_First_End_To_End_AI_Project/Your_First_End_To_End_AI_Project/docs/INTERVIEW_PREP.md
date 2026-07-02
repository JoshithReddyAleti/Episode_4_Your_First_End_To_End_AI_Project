# 🎤 Interview Prep — Episode 4 Project

---

## The One-Sentence Summary

> "I built and shipped a complete AI assistant with a Streamlit UI, 4-tool routing, conversation memory, Pydantic validation, and full test coverage — demonstrating the entire lifecycle from scoping to deployment."

---

## The Full Story (2-minute version)

> "Episode 3 was a backend pipeline. Episode 4 was about shipping a product.
>
> I added a Streamlit interface so the project is accessible to non-technical users, a conversation history manager so the system remembers what was said within a session, and two new tools — Wikipedia summaries and a unit converter — to show the architecture scales cleanly.
>
> The key engineering challenge was context injection: the LLM is stateless, so I built a conversation manager that tracks every turn and injects the last 5 into the routing prompt. This gives the router enough context to handle follow-up questions like 'What about Paris?' after a weather query, without blowing up the token budget.
>
> I followed a 7-step lifecycle: scope, architect, build in milestones, test, document, prepare for deployment, and write the story. The project has 40+ tests across unit, mock, and integration layers, with full documentation including an interview prep guide and a deployment guide.
>
> The biggest lesson: the difference between a project and a product is not code — it's process."

---

## Key Questions

### "Why did you add a UI?"
> "A CLI tool and a Streamlit app do the same thing technically, but the perception is completely different. Adding a UI makes the project accessible to non-developers, demo-able in interviews, and shareable via URL. It also forced me to think about user experience — error states, loading indicators, conversation display — which is a production engineering skill."

### "How does conversation memory work if LLMs are stateless?"
> "The LLM has no memory between calls. The conversation manager stores every turn as a structured object, and at routing time, the last N turns are serialized and injected into the routing prompt. The LLM 'sees' the history as part of its context window. The trade-off is token cost — more history means better context but higher cost, so I made the number of injected turns configurable."

### "How do you add a new tool?"
> "Three changes: create a new tool file with a run() function that returns a dict, add one import line to the tool registry, and add one example to the routing prompt. The router, validator, UI, and tests don't need to change — that's the Open/Closed Principle."

### "What would you add next?"
> "Persistent memory across sessions using SQLite or Redis, deployment to Streamlit Cloud, observability with structured logging to an external service, and eventually RAG so the assistant can answer questions about uploaded documents. That's Episode 5."

---

## Resume Bullets

> **Full lifecycle:** Designed, built, tested, documented, and prepared for deployment a 4-tool AI assistant with Streamlit UI, session memory, Pydantic validation, and 40+ tests — following a structured 7-step project lifecycle.

> **Technical depth:** Engineered stateful conversation management for a stateless LLM system, with configurable context injection, structured turn tracking, and JSON export for observability.

> **Product thinking:** Added a Streamlit web interface, conversation history sidebar, and tool usage transparency — transforming a backend pipeline into a demo-ready AI product.

---

*Back to [README](../README.md) · [Concepts](CONCEPTS.md) · [Project Lifecycle](PROJECT_LIFECYCLE.md)*
