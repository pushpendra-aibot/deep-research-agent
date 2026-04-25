# main.py

import asyncio
import json
import uuid
from fastapi import FastAPI, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

from agent import run_research_agent

app = FastAPI(title="AI Research Agent")

# In-memory session store
sessions: dict[str, asyncio.Queue] = {}
results:  dict[str, str] = {}


class ResearchRequest(BaseModel):
    query: str


@app.post("/research")
async def start_research(request: ResearchRequest, background_tasks: BackgroundTasks):
    """Start a research session. Returns a session_id to stream events from."""
    session_id = str(uuid.uuid4())
    queue = asyncio.Queue()
    sessions[session_id] = queue

    # Run agent in background
    background_tasks.add_task(
        run_research_agent, request.query, queue
    )

    return {"session_id": session_id, "query": request.query}


@app.get("/stream/{session_id}")
async def stream_events(session_id: str):
    """SSE endpoint — streams tool call events for a session."""
    if session_id not in sessions:
        return JSONResponse({"error": "Session not found"}, status_code=404)

    queue = sessions[session_id]

    async def event_generator():
        while True:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=60.0)
                yield {
                    "data": json.dumps(event),
                    "event": event.get("type", "message")
                }
                if event.get("type") in ["complete", "error"]:
                    # Store final report
                    if event.get("type") == "complete":
                        results[session_id] = event.get("report", "")
                    # Cleanup
                    del sessions[session_id]
                    break
            except asyncio.TimeoutError:
                yield {"data": json.dumps({"type": "ping"}), "event": "ping"}

    return EventSourceResponse(event_generator())


@app.get("/report/{session_id}")
async def get_report(session_id: str):
    """Get the final report for a completed session."""
    report = results.get(session_id)
    if not report:
        return JSONResponse({"error": "Report not ready or not found"}, status_code=404)
    return {"report": report}


# Serve frontend
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
