# services/mcp_tools.py
#
# MCP (Model Context Protocol) tool definitions.
#
# Each tool is a plain callable that accepts typed arguments and returns
# JSON-serialisable data.  The tool registry at the bottom of this module
# is what app.py exposes on the  GET /tools  and  POST /tools/{name}
# endpoints.
#
# Tools
# ─────
#   get_review_by_id(review_id)
#   get_reviews_by_country(country, limit)
#   get_reviews_by_rating(rating, limit)
#   count_reviews(country, rating)
#   semantic_search(query, k)
#   hybrid_search(query, country, rating, k)

from __future__ import annotations

from typing import Any, Optional

from services.sql_tools  import (
    get_review_by_id      as _get_by_id,
    get_reviews_by_country as _by_country,
    get_reviews_by_rating  as _by_rating,
    count_reviews          as _count,
)
from services.retriever import (
    semantic_search as _semantic,
    hybrid_search   as _hybrid,
)


# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------

def tool_get_review_by_id(review_id: int) -> dict:
    """
    Fetch a single review by its database id (or source_row_id).

    Args:
        review_id: integer primary-key or source_row_id value.

    Returns:
        { "results": [ <review dict> ], "count": 1 }
        If not found, count = 0.

    Example query:
        "Show review 12283"
    """
    results = _get_by_id(review_id)
    return {"results": results, "count": len(results)}


def tool_get_reviews_by_country(
    country: str,
    limit: int = 10,
    rating: Optional[int] = None,
) -> dict:
    """
    Fetch reviews from a specific country.

    Args:
        country: ISO country code (case-insensitive), e.g. "US", "gb".
        limit:   Maximum number of reviews to return (default 10).
        rating:  Optional star filter (1-5).

    Returns:
        { "results": [ ... ], "count": N, "country": "US" }

    Example queries:
        "Show me 50 US reviews"
        "Give me 20 GB 1-star reviews"
    """
    results = _by_country(country=country, limit=limit, rating=rating)
    return {
        "results": results,
        "count":   len(results),
        "country": country.upper().strip(),
    }


def tool_get_reviews_by_rating(
    rating: int,
    limit: int = 10,
    country: Optional[str] = None,
) -> dict:
    """
    Fetch reviews with a specific star rating.

    Args:
        rating:  Star rating to filter on (1-5).
        limit:   Maximum number of reviews to return (default 10).
        country: Optional ISO country code filter.

    Returns:
        { "results": [ ... ], "count": N, "rating": 1 }

    Example queries:
        "Show all 1-star reviews"
        "List 5-star reviews from Canada"
    """
    results = _by_rating(rating=rating, limit=limit, country=country)
    return {
        "results": results,
        "count":   len(results),
        "rating":  rating,
    }


def tool_count_reviews(
    country: Optional[str] = None,
    rating:  Optional[int] = None,
) -> dict:
    """
    Count reviews matching optional filters.

    Args:
        country: Optional ISO country code filter.
        rating:  Optional star rating filter (1-5).

    Returns:
        { "count": N, "country": ..., "rating": ... }

    Example queries:
        "Count reviews from GB"
        "How many 1-star reviews are there?"
        "Total number of reviews"
    """
    return _count(country=country, rating=rating)


def tool_semantic_search(
    query: str,
    k: int = 5,
) -> dict:
    """
    Find the most semantically similar reviews to *query* using pgvector
    HNSW cosine-distance search.

    Args:
        query: Natural-language search query.
        k:     Number of results to return (default 5).

    Returns:
        { "results": [ ... ], "count": N, "query": "..." }

    Example queries:
        "Why are customers unhappy with refunds?"
        "Common complaints about delivery"
    """
    results = _semantic(query=query, k=k)
    return {"results": results, "count": len(results), "query": query}


def tool_hybrid_search(
    query:   str,
    country: Optional[str] = None,
    rating:  Optional[int] = None,
    k:       int = 10,
) -> dict:
    """
    Metadata-filtered vector similarity search.

    First restricts the candidate pool using country/rating filters,
    then runs pgvector cosine-distance search within that subset.

    Args:
        query:   Natural-language search query.
        country: Optional ISO country code filter.
        rating:  Optional star rating filter (1-5).
        k:       Number of results to return (default 10).

    Returns:
        { "results": [ ... ], "count": N, "query": "...",
          "filters": { "country": ..., "rating": ... } }

    Example queries:
        "What do US customers say about refunds?"   → country="US"
        "Why are 1-star reviewers unhappy?"         → rating=1
        "What do GB customers think about shipping?"→ country="GB"
    """
    results = _hybrid(query=query, country=country, rating=rating, k=k)
    return {
        "results": results,
        "count":   len(results),
        "query":   query,
        "filters": {"country": country, "rating": rating},
    }


# ---------------------------------------------------------------------------
# Tool registry  (name → metadata + callable)
# ---------------------------------------------------------------------------

TOOLS: dict[str, dict[str, Any]] = {
    "get_review_by_id": {
        "description": "Fetch a single review by its id or source_row_id.",
        "parameters": {
            "review_id": {"type": "integer", "required": True},
        },
        "fn": tool_get_review_by_id,
    },
    "get_reviews_by_country": {
        "description": (
            "Return up to `limit` reviews from a given country code. "
            "Optional `rating` filter."
        ),
        "parameters": {
            "country": {"type": "string",  "required": True},
            "limit":   {"type": "integer", "required": False, "default": 10},
            "rating":  {"type": "integer", "required": False},
        },
        "fn": tool_get_reviews_by_country,
    },
    "get_reviews_by_rating": {
        "description": (
            "Return up to `limit` reviews with a specific star rating (1-5). "
            "Optional `country` filter."
        ),
        "parameters": {
            "rating":  {"type": "integer", "required": True},
            "limit":   {"type": "integer", "required": False, "default": 10},
            "country": {"type": "string",  "required": False},
        },
        "fn": tool_get_reviews_by_rating,
    },
    "count_reviews": {
        "description": (
            "Count reviews matching optional country and/or rating filters."
        ),
        "parameters": {
            "country": {"type": "string",  "required": False},
            "rating":  {"type": "integer", "required": False},
        },
        "fn": tool_count_reviews,
    },
    "semantic_search": {
        "description": (
            "Semantic vector search. Returns the top-k reviews most "
            "similar to the natural-language query."
        ),
        "parameters": {
            "query": {"type": "string",  "required": True},
            "k":     {"type": "integer", "required": False, "default": 5},
        },
        "fn": tool_semantic_search,
    },
    "hybrid_search": {
        "description": (
            "Metadata-filtered semantic search. Applies country/rating "
            "filters first, then runs pgvector similarity search inside "
            "the filtered candidate set."
        ),
        "parameters": {
            "query":   {"type": "string",  "required": True},
            "country": {"type": "string",  "required": False},
            "rating":  {"type": "integer", "required": False},
            "k":       {"type": "integer", "required": False, "default": 10},
        },
        "fn": tool_hybrid_search,
    },
}
