# agent.py
# The core research agent — runs the tool-calling loop and streams events.

import json
import asyncio
import logging
from openai import OpenAI
from prompts import SYSTEM_PROMPT, TOOL_SCHEMAS
from tools import execute_tool

client = OpenAI()
MAX_ITERATIONS = 15  # Safety cap — prevents infinite loops

# Configure file logging
logging.basicConfig(
    filename='research_process.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


async def run_research_agent(query: str, event_queue: asyncio.Queue):
    """
    Run the research agent for a given query.
    Streams events to event_queue as tool calls happen.
    
    Event types:
      {"type": "tool_call",   "tool": name, "args": {...}}
      {"type": "tool_result", "tool": name, "result": {...}}
      {"type": "thinking",    "message": "..."}
      {"type": "complete",    "report": "..."}
      {"type": "error",       "message": "..."}
    """

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": f"Research this topic thoroughly: {query}"}
    ]

    await event_queue.put({
        "type": "thinking",
        "message": f'Starting research on: "{query}"'
    })
    logging.info(f"=== STARTING NEW RESEARCH SESSION ===")
    logging.info(f"Query: {query}")

    for iteration in range(MAX_ITERATIONS):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=TOOL_SCHEMAS,
                tool_choice="auto",
                temperature=0.3
            )

            message = response.choices[0].message
            finish_reason = response.choices[0].finish_reason

            # ── Agent chose to call tools ─────────────────────────────────
            if finish_reason == "tool_calls" and message.tool_calls:
                messages.append(message)

                tool_results = []
                for tool_call in message.tool_calls:
                    name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments)

                    # Stream: tool is being called
                    await event_queue.put({
                        "type": "tool_call",
                        "tool": name,
                        "args": args,
                        "iteration": iteration + 1
                    })
                    logging.info(f"[Iteration {iteration + 1}] Calling Tool: {name}")
                    logging.info(f"Arguments: {json.dumps(args)}")

                    # Execute the tool
                    result_str = execute_tool(name, args)
                    result = json.loads(result_str)

                    # Stream: tool result
                    await event_queue.put({
                        "type": "tool_result",
                        "tool": name,
                        "result": result
                    })
                    logging.info(f"Tool Result ({name}): {json.dumps(result)[:500]}...")

                    tool_results.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": name,
                        "content": result_str
                    })

                messages.extend(tool_results)

            # ── Agent decided it's done — final report ────────────────────
            elif finish_reason == "stop":
                report = message.content

                await event_queue.put({
                    "type": "complete",
                    "report": report,
                    "iterations": iteration + 1
                })
                logging.info(f"=== RESEARCH COMPLETE ===")
                logging.info(f"Finished in {iteration + 1} iterations. Report length: {len(report)} chars.")
                return

            else:
                await event_queue.put({
                    "type": "error",
                    "message": f"Unexpected finish reason: {finish_reason}"
                })
                return

        except Exception as e:
            await event_queue.put({
                "type": "error",
                "message": str(e)
            })
            logging.error(f"Error during research loop: {str(e)}")
            return

    # Hit iteration limit
    await event_queue.put({
        "type": "error",
        "message": f"Research exceeded {MAX_ITERATIONS} iterations. Try a narrower query."
    })
    logging.warning(f"Research aborted: Exceeded {MAX_ITERATIONS} iterations limit.")
