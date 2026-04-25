# AI Deep Research Agent

An autonomous, agentic web application that performs deep, iterative research on any given topic. Unlike simple Retrieval-Augmented Generation (RAG) systems that search once and summarize, this agent plans, searches, reads, cross-checks facts, and refines its queries until it can produce a highly confident, fully cited report.

## Key Features

- **Iterative Research Loop**: The agent evaluates its findings and autonomously decides to run deeper, multi-hop searches if evidence is lacking.
- **Strict Confidence Rules**: Built with enterprise trust in mind. If the agent cannot find verified sources for a claim, it adheres to the "I don't know" rule rather than hallucinating.
- **Snippet Grounding**: Every insight in the final report is backed by verbatim excerpts extracted directly from the source pages.
- **Live Agentic Feed**: Watch the agent's thought process and tool usage in real-time via the web interface.

## Prerequisites

You need API keys for the following services:
1. **OpenAI**: To power the reasoning agent (`gpt-4o`) and extraction tasks (`gpt-4o-mini`). [Get a key here](https://platform.openai.com/).
2. **Tavily**: To perform agentic web searches. [Get a free tier key here](https://tavily.com/).

## Setup Instructions

1. **Configure Environment Variables**
   Rename `.env.example` to `.env` and insert your API keys:
   ```bash
   cp .env.example .env
   # Edit .env and set OPENAI_API_KEY and TAVILY_API_KEY
   ```

2. **Activate Virtual Environment**
   If you haven't already, ensure your virtual environment is active:
   ```bash
   source venv/bin/activate
   ```

3. **Install Dependencies** (if not already done)
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the Server**
   Run the FastAPI server using `uvicorn`:
   ```bash
   uvicorn main:app --reload
   ```

## How to Use

1. Open your browser and navigate to `http://localhost:8000`.
2. Type a complex research question into the input box (e.g., "What is the state of reasoning models in 2026?").
3. Click **Research ▶**.
4. **Watch the Live Feed**: The UI will stream the agent's actions step-by-step. You will see it searching the web, reading specific URLs, extracting points, and checking for contradictions.
5. **View the Report**: Once the agent reaches high confidence, it will output a comprehensive, structured Markdown report complete with snippet grounding and inline citations.
