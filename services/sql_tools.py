

from __future__ import annotations

from typing import Optional

from services.database import get_connection


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

_SELECT = """
    SELECT
        id,
        source_row_id,
        reviewer_name,
        country,
        rating,
        review_date,
        review_title,
        review_text
    FROM amazon_reviews
"""

_COLS = (
    "id", "source_row_id", "reviewer_name", "country",
    "rating", "review_date", "review_title", "review_text",
)


def _rows_to_dicts(rows: list) -> list[dict]:
    return [dict(zip(_COLS, row)) for row in rows]


def _run(sql: str, params: tuple = ()) -> list[dict]:
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return _rows_to_dicts(rows)


# ---------------------------------------------------------------------------
# MCP Tool: get_review_by_id
# ---------------------------------------------------------------------------

def get_review_by_id(review_id: int) -> list[dict]:
    """
    Return the single review whose *id* (or *source_row_id*) matches.

    Example query: "show review 12283"
    """
    sql = _SELECT + """
        WHERE id = %s OR source_row_id = %s
        LIMIT 1
    """
    return _run(sql, (review_id, review_id))


# ---------------------------------------------------------------------------
# MCP Tool: get_reviews_by_country
# ---------------------------------------------------------------------------

def get_reviews_by_country(
    country: str,
    limit: int = 10,
    rating: Optional[int] = None,
) -> list[dict]:
    """
    Return up to *limit* reviews from *country* (ISO code, case-insensitive).
    Optionally filter by *rating*.

    Example query: "show me 50 US reviews"
    """
    country = country.upper().strip()

    if rating is not None:
        sql = _SELECT + """
            WHERE country = %s AND rating = %s
            ORDER BY id
            LIMIT %s
        """
        return _run(sql, (country, rating, limit))

    sql = _SELECT + """
        WHERE country = %s
        ORDER BY id
        LIMIT %s
    """
    return _run(sql, (country, limit))


# ---------------------------------------------------------------------------
# MCP Tool: get_reviews_by_rating
# ---------------------------------------------------------------------------

def get_reviews_by_rating(
    rating: int,
    limit: int = 10,
    country: Optional[str] = None,
) -> list[dict]:
    """
    Return up to *limit* reviews with *rating* stars.
    Optionally filter by *country*.

    Example query: "show all 1-star reviews"
    """
    if country is not None:
        country = country.upper().strip()
        sql = _SELECT + """
            WHERE rating = %s AND country = %s
            ORDER BY id
            LIMIT %s
        """
        return _run(sql, (rating, country, limit))

    sql = _SELECT + """
        WHERE rating = %s
        ORDER BY id
        LIMIT %s
    """
    return _run(sql, (rating, limit))


# ---------------------------------------------------------------------------
# MCP Tool: count_reviews
# ---------------------------------------------------------------------------

def count_reviews(
    country: Optional[str] = None,
    rating: Optional[int] = None,
) -> dict:
    """
    Return a count dict: {"count": N, "country": ..., "rating": ...}

    Example queries:
      "count reviews from GB"
      "how many 1-star reviews are there?"
      "how many reviews in total?"
    """
    conn = get_connection()
    cur  = conn.cursor()

    conditions = []
    params: list = []

    if country is not None:
        conditions.append("country = %s")
        params.append(country.upper().strip())
    if rating is not None:
        conditions.append("rating = %s")
        params.append(rating)

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    cur.execute(f"SELECT COUNT(*) FROM amazon_reviews {where}", params)
    total = cur.fetchone()[0]
    cur.close()
    conn.close()

    return {"count": total, "country": country, "rating": rating}
