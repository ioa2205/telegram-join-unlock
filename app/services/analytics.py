# app/services/analytics.py
import logging

from app.db import Database

log = logging.getLogger(__name__)


async def log_event(db: Database, user_id: int, event_type: str, slug: str | None = None):
    """Logs a user event to the database."""
    query = "INSERT INTO events (user_id, type, slug) VALUES (?, ?, ?)"
    try:
        await db.execute(query, (user_id, event_type, slug))
        log.info("Logged event '%s' for user %d (slug: %s)", event_type, user_id, slug)
    except Exception as e:
        log.error("Failed to log event for user %d: %s", user_id, e)


async def get_stats(db: Database) -> dict:
    """Retrieves various statistics from the database."""
    total_users_q = "SELECT COUNT(*) as count FROM users"
    joined_users_q = "SELECT COUNT(*) as count FROM users WHERE joined_ok = 1"
    
    # THE FIX IS HERE: Using PostgreSQL's interval syntax
    active_30d_q = "SELECT COUNT(DISTINCT user_id) as count FROM events WHERE ts >= NOW() - INTERVAL '30 days'"

    total_users = (await db.fetchone(total_users_q) or {}).get("count", 0)
    joined_users = (await db.fetchone(joined_users_q) or {}).get("count", 0)
    active_30d = (await db.fetchone(active_30d_q) or {}).get("count", 0)

    per_slug_stats_q = """
    SELECT
        s.slug, s.label,
        COALESCE(starts.count, 0) as starts,
        COALESCE(verifies.count, 0) as verifies,
        COALESCE(sends.count, 0) as sends
    FROM slugs s
    LEFT JOIN (SELECT slug, COUNT(*) as count FROM events WHERE type = 'start' GROUP BY slug) starts ON s.slug = starts.slug
    LEFT JOIN (SELECT slug, COUNT(*) as count FROM events WHERE type = 'verify_ok' GROUP BY slug) verifies ON s.slug = verifies.slug
    LEFT JOIN (SELECT slug, COUNT(*) as count FROM events WHERE type = 'file_sent' GROUP BY slug) sends ON s.slug = sends.slug
    """
    per_slug_stats = await db.fetchall(per_slug_stats_q)

    return {
        "total_users": total_users,
        "joined_users": joined_users,
        "active_30d": active_30d,
        "per_slug": per_slug_stats
    }

async def get_slug_performance(db: Database, slug_id: str) -> dict:
    """Retrieves performance statistics for a single slug."""
    starts_q = "SELECT COUNT(*) as count FROM events WHERE type = 'start' AND slug = ?"
    verifies_q = "SELECT COUNT(*) as count FROM events WHERE type = 'verify_ok' AND slug = ?"
    sends_q = "SELECT COUNT(*) as count FROM events WHERE type = 'file_sent' AND slug = ?"

    starts = (await db.fetchone(starts_q, (slug_id,)) or {}).get("count", 0)
    verifies = (await db.fetchone(verifies_q, (slug_id,)) or {}).get("count", 0)
    sends = (await db.fetchone(sends_q, (slug_id,)) or {}).get("count", 0)

    return {"starts": starts, "verifies": verifies, "sends": sends}