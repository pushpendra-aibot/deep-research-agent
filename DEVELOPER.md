# Developer Documentation

Welcome to the AI Research Agent codebase. This document outlines the architecture, the core files, and instructions for extending the agent.

## System Architecture

The application operates on a modern asynchronous stack:
- **FastAPI**: Handles HTTP requests and Server-Sent Events (SSE) streaming.
- **OpenAI API**: Orchestrates the agent loop via `gpt-4o` tool calling and uses `gpt-4o-mini` for fast sub-tasks (extraction, verification).
- **Vanilla JS/HTML/CSS**: A lightweight frontend that consumes the SSE stream to render the live tool feed.

### Core Workflow
1. User submits a query via `POST /research`.
2. Server assigns a `session_id`, opens an `asyncio.Queue`, and spawns the `run_research_agent` task in the background.
3. The frontend immediately opens an SSE connection to `GET /stream/{session_id}`.
4. The Agent Loop (in `agent.py`) enters a `while` loop (up to `MAX_ITERATIONS`). It passes the conversation history to OpenAI.
5. OpenAI returns a list of "tool calls".
6. The agent executes these tools synchronously/asynchronously, places the results back into the context window, and pushes UI events to the `Queue`.
7. The SSE endpoint yields these queue items to the frontend.
8. Once the LLM determines it has enough information, it stops calling tools, generates a final Markdown report, and terminates the loop.

## Codebase Map

### 1. `main.py`
The entry point. Sets up the FastAPI app, manages the in-memory session dictionary, handles the POST endpoint to kick off background research, and serves the SSE stream.

### 2. `agent.py`
Contains the core `run_research_agent` async function. This is the "brain" orchestrating the OpenAI tool-calling loop. It formats the system prompt, tracks iteration limits to prevent infinite loops, and streams typed events (`thinking`, `tool_call`, `tool_result`, `complete`, `error`) to the queue.

### 3. `prompts.py`
Holds the `SYSTEM_PROMPT` which enforces the strict "Deep Research" paradigms:
- The "I don't know" rule.
- Snippet grounding and inline citations.
- Iterative multi-hop reasoning.
Also defines `TOOL_SCHEMAS`, the JSON schemas sent to OpenAI so the model knows how to invoke functions.

### 4. `tools.py`
The implementation of the research capabilities. 
- `web_search`: Uses the Tavily API.
- `fetch_page`: Uses `requests` and `BeautifulSoup` to strip noise and extract raw text from HTML.
- `extract_key_points`: Uses `gpt-4o-mini` to extract structured snippets.
- `verify_claim`: Uses `gpt-4o-mini` to cross-check facts against evidence.
- `detect_contradictions`: Analyzes lists of findings for conflicts.
It also includes the `execute_tool` dispatcher which safely runs these functions and catches exceptions.

### 5. `frontend/`
- `index.html`: The layout structure.
- `app.js`: Connects to the SSE stream and updates the DOM dynamically as tools fire.
- `styles.css`: Dark mode aesthetics.

## How to Extend the Agent

Adding a new capability (e.g., querying a local database or a specific API) requires three steps:

1. **Implement the Python Function**: Add your tool logic in `tools.py` and register it in the `TOOL_MAP`.
   ```python
   def query_database(sql: str) -> dict:
       # ... logic ...
       return {"results": data}
   ```
   *Don't forget to add it to `TOOL_MAP`!*

2. **Define the Schema**: Add the JSON schema for your tool to `TOOL_SCHEMAS` inside `prompts.py` so the LLM knows how and when to call it.

3. **Update the Frontend (Optional but Recommended)**: To make the tool look nice in the live feed, add an icon and label to `TOOL_ICONS` and `TOOL_LABELS` in `frontend/app.js`. You can also add specific rendering logic inside `updateLastToolResult()`.
