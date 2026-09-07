from __future__ import annotations

from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
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
app.mount("/static", StaticFiles(directory="static"), name="static")

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


