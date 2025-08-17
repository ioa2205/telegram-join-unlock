# app/models.py

# SYNTAX CHANGES:
# - INTEGER PRIMARY KEY -> BIGINT PRIMARY KEY (Safer for large Telegram IDs)
# - AUTOINCREMENT -> SERIAL (PostgreSQL's auto-incrementing integer)
# - DATETIME -> TIMESTAMPTZ (Timestamp with timezone, more robust)
# - CURRENT_TIMESTAMP -> NOW()

CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    chat_id BIGINT NOT NULL,
    selected_slug TEXT,
    joined_ok INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
"""

CREATE_SLUGS_TABLE = """
CREATE TABLE IF NOT EXISTS slugs (
    slug TEXT PRIMARY KEY,
    label TEXT NOT NULL,
    file_id TEXT NOT NULL,
    active INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
"""

CREATE_EVENTS_TABLE = """
CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    type TEXT NOT NULL,
    slug TEXT,
    ts TIMESTAMPTZ DEFAULT NOW()
);
"""