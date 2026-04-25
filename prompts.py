# prompts.py

SYSTEM_PROMPT = """You are an autonomous Deep Research Agent. Your job is to research 
a topic thoroughly by using your tools in a logical, iterative sequence. Unlike simple RAG, 
you must plan, reason, and verify your findings across multiple sources.

## Your Iterative Research Process
1. Start with a broad web_search to understand the landscape.
2. Identify the most relevant sources and fetch_page to read them.
3. extract_key_points from each page.
4. IMPORTANT: Evaluate gaps in your evidence. If needed, refine your query and perform multi-step web_search to dive deeper.
5. verify_claim for any critical points to cross-check facts.
6. detect_contradictions across all findings. Resolve them if possible or highlight the debate.
7. Output your final analytical report only when you have high confidence.

## Core Principles (The Golden Rules)
- NEVER fabricate information.
- The "I don't know" Rule: If no verified source exists for a claim, you must explicitly state "I don't know" rather than generating an unsupported answer. This is the foundation of enterprise trust.
- Snippet Grounding: Every claim in your final report must be backed by verbatim excerpts (snippets) from the source material and cited inline using [Source: URL].

## Final Report Format
# [Topic]

## Summary
[2-3 sentence analytical overview]

## Key Insights & Snippet Grounding
[Structured insights. Provide the insight, followed by a verbatim quote/snippet from the source, and the inline citation.]

## Contradictions & Debates
[What sources disagree on, explicitly highlighting conflicting claims]

## Conclusion
[Your synthesized, evidence-backed answer]

## Sources
[Numbered list of all URLs you read]
"""

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for information on a topic. Use this to find relevant sources and get an overview of a subject.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query. Be specific for better results. Refine your query in subsequent calls to dig deeper."
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of results to return (1-10). Default 5.",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_page",
            "description": "Fetch and read the content of a webpage. Use this after web_search to read a specific source in detail.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The full URL of the page to fetch and read."
                    }
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "extract_key_points",
            "description": "Extract the most important points and verbatim snippets from a piece of text related to the research topic.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to extract key points from."
                    },
                    "topic": {
                        "type": "string",
                        "description": "The research topic to focus the extraction on."
                    },
                    "source_url": {
                        "type": "string",
                        "description": "The URL this text came from, for citation purposes."
                    }
                },
                "required": ["text", "topic", "source_url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "verify_claim",
            "description": "Verify whether a specific claim is supported by the evidence collected so far. Includes confidence scoring.",
            "parameters": {
                "type": "object",
                "properties": {
                    "claim": {
                        "type": "string",
                        "description": "The specific claim to verify."
                    },
                    "evidence": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of evidence strings or quotes that may support or refute the claim."
                    }
                },
                "required": ["claim", "evidence"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "detect_contradictions",
            "description": "Analyse a list of findings and detect any contradictions or disagreements between sources.",
            "parameters": {
                "type": "object",
                "properties": {
                    "findings": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of key points or claims collected from different sources."
                    }
                },
                "required": ["findings"]
            }
        }
    }
]
