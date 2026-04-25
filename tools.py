# tools.py

import os
import re
import json
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from tavily import TavilyClient
from datetime import datetime

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))



# ── Tool 1: Web Search ────────────────────────────────────────────────────────

def web_search(query: str, num_results: int = 5) -> dict:
    """Search the web using Tavily — built for LLM agents, returns clean results."""
    try:
        response = tavily.search(
            query=query,
            max_results=num_results,
            search_depth="basic",
            include_answer=False
        )
        results = [
            {
                "url": r["url"],
                "title": r["title"],
                "snippet": r["content"][:300]
            }
            for r in response.get("results", [])
        ]
        return {"results": results, "query": query}
    except Exception as e:
        return {"error": str(e), "results": []}


# ── Tool 2: Fetch Page ────────────────────────────────────────────────────────

def fetch_page(url: str) -> dict:
    """Fetch a webpage and extract clean readable text."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; ResearchAgent/1.0)"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove noise
        for tag in soup(["script", "style", "nav", "header",
                          "footer", "aside", "ads"]):
            tag.decompose()

        # Extract main content
        main = (
            soup.find("article") or
            soup.find("main") or
            soup.find(id=re.compile(r"content|main|article", re.I)) or
            soup.find(class_=re.compile(r"content|main|article|post", re.I)) or
            soup.body
        )

        text = main.get_text(separator=" ", strip=True) if main else ""
        text = re.sub(r"\s+", " ", text).strip()

        return {
            "url": url,
            "text": text[:4000],    # Keep within token budget
            "char_count": len(text)
        }
    except Exception as e:
        return {"url": url, "error": str(e), "text": ""}


# ── Tool 3: Extract Key Points ────────────────────────────────────────────────

def extract_key_points(text: str, topic: str, source_url: str) -> dict:
    """Use gpt-4o-mini to extract the most relevant points from a page."""
    if not text or len(text) < 100:
        return {"points": [], "source_url": source_url}

    prompt = f"""Extract the 5 most important and specific points from this text 
that are relevant to the research topic: "{topic}"

TEXT:
{text[:3000]}

Rules:
- Only include factual, specific points (not generic statements)
- Each point must be a complete, self-contained sentence
- Include specific numbers, dates, or names where present
- Ignore marketing language or filler content

Respond with JSON only:
{{"points": ["point 1", "point 2", "point 3", "point 4", "point 5"]}}"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        temperature=0.1,
        messages=[
            {"role": "system", "content": "Extract key facts. JSON only."},
            {"role": "user", "content": prompt}
        ]
    )
    result = json.loads(response.choices[0].message.content)
    return {
        "points": result.get("points", []),
        "source_url": source_url
    }


# ── Tool 4: Verify Claim ─────────────────────────────────────────────────────

def verify_claim(claim: str, evidence: list[str]) -> dict:
    """Cross-check a claim against collected evidence."""
    evidence_text = "\n".join([f"- {e}" for e in evidence[:10]])

    prompt = f"""You are a fact-checker. Determine whether the following claim 
is supported, refuted, or unclear based on the evidence provided.

CLAIM: "{claim}"

EVIDENCE:
{evidence_text}

Respond with JSON only:
{{
  "verdict": "supported" | "refuted" | "unclear",
  "confidence": 0.0-1.0,
  "reasoning": "one sentence explanation",
  "supporting_evidence": ["quotes that support"],
  "contradicting_evidence": ["quotes that contradict"]
}}"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        temperature=0.0,
        messages=[
            {"role": "system", "content": "You are a precise fact-checker. JSON only."},
            {"role": "user", "content": prompt}
        ]
    )
    return json.loads(response.choices[0].message.content)


# ── Tool 5: Detect Contradictions ────────────────────────────────────────────

def detect_contradictions(findings: list[str]) -> dict:
    """Find contradictions across all collected findings."""
    if len(findings) < 2:
        return {"contradictions": [], "total_findings": len(findings)}

    findings_text = "\n".join([f"{i+1}. {f}" for i, f in enumerate(findings)])

    prompt = f"""Analyse these research findings and identify any contradictions 
or significant disagreements between them.

FINDINGS:
{findings_text}

Respond with JSON only:
{{
  "contradictions": [
    {{
      "finding_a": "first claim",
      "finding_b": "conflicting claim",
      "explanation": "why these conflict"
    }}
  ],
  "summary": "overall consistency assessment in one sentence"
}}

Return empty contradictions array if findings are consistent."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        temperature=0.1,
        messages=[
            {"role": "system", "content": "Find contradictions in research. JSON only."},
            {"role": "user", "content": prompt}
        ]
    )
    return json.loads(response.choices[0].message.content)


# ── Tool Dispatcher ───────────────────────────────────────────────────────────

TOOL_MAP = {
    "web_search": web_search,
    "fetch_page": fetch_page,
    "extract_key_points": extract_key_points,
    "verify_claim": verify_claim,
    "detect_contradictions": detect_contradictions
}

def execute_tool(name: str, arguments: dict) -> str:
    """Execute a tool by name and return its result as a JSON string."""
    if name not in TOOL_MAP:
        return json.dumps({"error": f"Unknown tool: {name}"})
    try:
        result = TOOL_MAP[name](**arguments)
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": str(e)})
