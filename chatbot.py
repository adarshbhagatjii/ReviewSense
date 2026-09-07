

from __future__ import annotations

from services.supervisor import run_supervisor


def ask_question(question: str) -> str:
    """
    Run the Supervisor Agent for *question* and return a human-readable answer.

    The Supervisor will:
      1. Analyse the question.
      2. Select and call the appropriate retrieval tool(s).
      3. Generate a final answer grounded in the retrieved data.
    """
    return run_supervisor(question)
