
# Retrieval layer — three modes:
#
#   semantic_search(query, k)
#       Pure pgvector ANN search using HNSW cosine distance.
#       Returns top-k reviews most similar to *query*.
#
#   hybrid_search(query, country, rating, k)
#       Metadata pre-filter in SQL (WHERE country=… AND rating=…)
#       then pgvector similarity search inside that filtered set.
#       Returns top-k reviews from the filtered universe.
#
#   search_reviews(question, k)           ← kept for backward compat
#       Alias for semantic_search.

from __future__ import annotations

from typing import Optional

from services.database import get_connection
from services.embeddings import create_embedding


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_SELECT_COLS = """
    SELECT
        id,
        country,
        rating,
        review_title,
        review_text,
        review_date,
        reviewer_name,
        source_row_id,
        embedding <=> %s::vector AS distance
"""


def _rows_to_dicts(rows: list) -> list[dict]:
    keys = (
        "id", "country", "rating", "review_title", "review_text",
        "review_date", "reviewer_name", "source_row_id", "distance",
    )
    return [dict(zip(keys, row)) for row in rows]


# ---------------------------------------------------------------------------
# MCP Tool: semantic_search
# ---------------------------------------------------------------------------

def semantic_search(query: str, k: int = 5) -> list[dict]:
    """
    Pure vector similarity search over the full table.

    Uses the HNSW index (cosine distance).  ef_search=100 gives
    >95 % recall with ~7 ms query time on 21 K rows.

    Returns a list of dicts (id, country, rating, review_title,
    review_text, review_date, reviewer_name, source_row_id, distance).
    """
    query_vec = create_embedding(query)

    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("SET hnsw.ef_search = 100;")

    cur.execute(
        _SELECT_COLS + """
        FROM amazon_reviews
        ORDER BY embedding <=> %s::vector
        LIMIT %s
        """,
        (query_vec, query_vec, k),
    )

    rows = cur.fetchall()
    cur.close()
    conn.close()

    print(f"[semantic_search] query='{query}' k={k} → {len(rows)} results")
    return _rows_to_dicts(rows)


# ---------------------------------------------------------------------------
# MCP Tool: hybrid_search
# ---------------------------------------------------------------------------

def hybrid_search(
    query: str,
    country: Optional[str] = None,
    rating: Optional[int]  = None,
    k: int = 10,
) -> list[dict]:
    """
    Metadata-filtered vector similarity search.

    Strategy
    --------
    1. Build a WHERE clause from the supplied metadata filters
       (country, rating).  Both are optional.
    2. Run pgvector cosine-distance ordering inside that filtered
       subset — the HNSW index is still used when the filtered
       candidate set is large enough; for very small sets PostgreSQL
       falls back to a sequential scan automatically.
    3. Return the top-*k* most similar rows.

    Example
    -------
    "What do US customers say about refunds?"
      → country='US', query='refunds'
      → filters ~4 000 rows then finds the 10 most similar ones.
    """
    query_vec = create_embedding(query)

    conditions: list[str] = []
    params: list           = [query_vec]          # first %s  = distance calc

    if country is not None:
        conditions.append("country = %s")
        params.append(country.upper().strip())
    if rating is not None:
        conditions.append("rating = %s")
        params.append(rating)

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    # Second copy of query_vec for ORDER BY
    params.append(query_vec)
    params.append(k)

    sql = _SELECT_COLS + f"""
        FROM amazon_reviews
        {where}
        ORDER BY embedding <=> %s::vector
        LIMIT %s
    """

    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("SET hnsw.ef_search = 100;")
    cur.execute(sql, params)

    rows = cur.fetchall()
    cur.close()
    conn.close()

    print(
        f"[hybrid_search] query='{query}' "
        f"country={country} rating={rating} k={k} → {len(rows)} results"
    )
    return _rows_to_dicts(rows)


# ---------------------------------------------------------------------------
# Backward-compatible alias
# ---------------------------------------------------------------------------

def search_reviews(question: str, k: int = 5) -> list[dict]:
    """Backward-compatible wrapper — delegates to semantic_search."""
    return semantic_search(question, k=k)
