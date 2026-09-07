# app.py

from __future__ import annotations

from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from chatbot import ask_question
from services.mcp_tools import TOOLS


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Amazon Review RAG Chatbot",
    description=(
        "Agentic RAG chatbot over 21 K+ Amazon reviews. "
        "An LLM Supervisor Agent autonomously selects and executes the "
        "correct retrieval strategy (SQL lookup, semantic search, or "
        "hybrid metadata-filtered vector search) using tool calling."
    ),
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    question: str


class ToolCallRequest(BaseModel):
    arguments: dict[str, Any] = {}


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", include_in_schema=False)
def home():
    """Serve the frontend chatbot UI."""
    return FileResponse("index.html")


# ── Main chat endpoint ──────────────────────────────────────────────────────

@app.post("/chat")
def chat(request: ChatRequest):
    """
    Submit a natural-language question.

    The LLM Supervisor Agent autonomously selects and executes the correct
    retrieval tool(s), then returns an AI-generated answer grounded
    entirely in the retrieved reviews.
    """
    answer = ask_question(request.question)
    return {"question": request.question, "answer": answer}


# ── MCP tools listing ───────────────────────────────────────────────────────

@app.get("/tools")
def list_tools():
    """
    List all available MCP tools with their descriptions and parameter schemas.
    """
    return {
        name: {
            "description": meta["description"],
            "parameters":  meta["parameters"],
        }
        for name, meta in TOOLS.items()
    }


# ── MCP tool invocation ─────────────────────────────────────────────────────

@app.post("/tools/{tool_name}")
def call_tool(tool_name: str, request: ToolCallRequest):
    """
    Invoke a named MCP tool with the supplied arguments.

    Example — semantic search:
        POST /tools/semantic_search
        { "arguments": { "query": "delivery problems", "k": 5 } }

    Example — hybrid search:
        POST /tools/hybrid_search
        { "arguments": { "query": "refunds", "country": "US", "k": 10 } }

    Example — count:
        POST /tools/count_reviews
        { "arguments": { "country": "GB" } }
    """
    if tool_name not in TOOLS:
        raise HTTPException(
            status_code=404,
            detail=f"Tool '{tool_name}' not found. "
                   f"Available tools: {list(TOOLS.keys())}",
        )

    tool_meta = TOOLS[tool_name]
    fn        = tool_meta["fn"]
    params    = tool_meta["parameters"]

    # Validate required arguments
    missing = [
        name for name, spec in params.items()
        if spec.get("required") and name not in request.arguments
    ]
    if missing:
        raise HTTPException(
            status_code=422,
            detail=f"Missing required arguments: {missing}",
        )

    # Type-coerce integers supplied as strings (common in JSON)
    coerced: dict[str, Any] = {}
    for name, spec in params.items():
        if name in request.arguments:
            val = request.arguments[name]
            if spec["type"] == "integer" and not isinstance(val, int):
                try:
                    val = int(val)
                except (TypeError, ValueError):
                    raise HTTPException(
                        status_code=422,
                        detail=f"Argument '{name}' must be an integer.",
                    )
            coerced[name] = val

    try:
        result = fn(**coerced)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return {"tool": tool_name, "arguments": coerced, "result": result}
