<div align="center">
  <img src="./thumbnail.png" alt="AI Deep Research Agent Demo Thumbnail" width="600"/>

  # 🧠 AI Deep Research Agent
  
  **An autonomous, multi-hop reasoning web application that doesn't just answer questions—it *does your research*.**

  [![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
  [![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com/)
  [![Tavily](https://img.shields.io/badge/Tavily-Search-00D2FF?style=for-the-badge)](https://tavily.com/)
</div>

---

## ⚡ What is it?

Unlike standard chatbots that do a single RAG lookup, this Deep Research Agent runs an **autonomous iterative loop** (up to 15 steps). It searches the web, reads pages, extracts facts, cross-checks claims, detects contradictions, and refines its queries until it can produce a highly confident, fully cited Markdown report.

## 🚀 Key Features

- 🔄 **Multi-Hop Agentic Loop**: The agent evaluates its findings and autonomously decides to run deeper searches if evidence is lacking.
- 🛡️ **The "I Don't Know" Golden Rule**: Built for enterprise trust. If the agent cannot find verified sources for a claim, it refuses to hallucinate and explicitly states it doesn't know.
- 📑 **Strict Snippet Grounding**: Every insight in the final report is backed by verbatim excerpts extracted directly from the source pages alongside inline URL citations.
- 📡 **Live Transparent Feed**: Watch the agent's "brain" work in real-time via Server-Sent Events (SSE). You see exactly what tools it calls, what it reads, and how confident it is.
- 📝 **Automated Session Logging**: Every step of the agent's thought process is logged and saved locally for audit trails.

---

## 🛠️ Getting Started

### 1. Prerequisites
You need API keys for the following services:
- **OpenAI**: Powers the reasoning agent (`gpt-4o-mini`).
- **Tavily**: Powers the agentic web search.

### 2. Setup Your Environment
Clone the repository and set up your API keys:
```bash
# Rename the example env file
cp .env.example .env

# Open .env and insert your OPENAI_API_KEY and TAVILY_API_KEY
```

### 3. Install Dependencies
Make sure you are in your virtual environment, then install the required Python packages:
```bash
pip install -r requirements.txt
```

### 4. Run the Server
Launch the FastAPI backend:
```bash
uvicorn main:app --reload
```

---

## 💻 How to Use

1. Open your browser and navigate to `http://localhost:8000`.
2. Type a complex, multi-layered research question into the prompt box (e.g., *"What is the state of reasoning models in 2026?"*).
3. Click **Research ▶**.
4. **Watch it Work**: The UI will stream the agent's actions step-by-step. You will see it scanning the web, extracting points, and checking for contradictions.
5. **Read the Report**: Once the agent is highly confident, it will output a comprehensive, structured Markdown report.

---

## 📂 Logs & Auditing
The system automatically generates a `research_process.log` file tracking every tool call. You can find a complete trace of a successful run in the provided `submission_logs.txt` file included in this repository!

<div align="center">
  <i>Built with ❤️ using Python, FastAPI, and Vanilla JS.</i>
</div>
