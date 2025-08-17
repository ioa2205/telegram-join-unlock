import re
from typing import Any

from app.db import Database


def is_valid_slug(slug: str) -> bool:
    """Validates slug format."""
    return bool(re.fullmatch(r"[a-z0-9_]{2,50}", slug))


async def get_slug_data(db: Database, slug: str) -> dict[str, Any] | None:
    """Fetches slug data from the database."""
    query = "SELECT * FROM slugs WHERE slug = ? AND active = 1"
    return await db.fetchone(query, (slug,))


async def get_all_slugs(db: Database) -> list[dict[str, Any]]:
    """Fetches all slugs from the database."""
    query = "SELECT slug, label, file_id FROM slugs ORDER BY created_at DESC"
    return await db.fetchall(query)