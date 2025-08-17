# app/db.py
import asyncio
import logging
from typing import Any

import asyncpg

from .models import CREATE_EVENTS_TABLE, CREATE_SLUGS_TABLE, CREATE_USERS_TABLE

log = logging.getLogger(__name__)


def _prepare_query(query: str, params: tuple) -> str:
    """Replaces '?' placeholders with '$1', '$2', etc. for asyncpg."""
    for i in range(len(params)):
        query = query.replace('?', f'${i + 1}', 1)
    return query


class Database:
    """Manages the connection to and operations on the PostgreSQL database."""

    def __init__(self, dsn: str):
        self.dsn = dsn
        self._pool: asyncpg.Pool | None = None

    async def connect(self) -> None:
        try:
            self._pool = await asyncpg.create_pool(dsn=self.dsn, timeout=10)
            async with self._pool.acquire() as connection:
                await self._create_tables(connection)
            log.info("Successfully connected to PostgreSQL and created tables.")
        except (asyncpg.PostgresError, OSError, asyncio.TimeoutError) as e:
            log.error("Database connection failed. Is the Docker container running? Error: %s", e)
            raise

    async def _create_tables(self, connection: asyncpg.Connection) -> None:
        await connection.execute(CREATE_USERS_TABLE)
        await connection.execute(CREATE_SLUGS_TABLE)
        await connection.execute(CREATE_EVENTS_TABLE)
        log.info("Tables checked/created successfully.")

    async def execute(self, query: str, params: tuple = ()) -> None:
        if not self._pool: raise ConnectionError("Database pool is not initialized.")
        prepared_query = _prepare_query(query, params)
        try:
            async with self._pool.acquire() as connection:
                await connection.execute(prepared_query, *params)
        except asyncpg.PostgresError as e:
            log.error("Failed to execute query: %s\nQuery: %s", e, prepared_query)
            raise

    async def fetchone(self, query: str, params: tuple = ()) -> dict[str, Any] | None:
        if not self._pool: raise ConnectionError("Database pool is not initialized.")
        prepared_query = _prepare_query(query, params)
        try:
            async with self._pool.acquire() as connection:
                row = await connection.fetchrow(prepared_query, *params)
                return dict(row) if row else None
        except asyncpg.PostgresError as e:
            log.error("Failed to fetch one row: %s\nQuery: %s", e, prepared_query)
            return None

    async def fetchall(self, query: str, params: tuple = ()) -> list[dict[str, Any]]:
        if not self._pool: raise ConnectionError("Database pool is not initialized.")
        prepared_query = _prepare_query(query, params)
        try:
            async with self._pool.acquire() as connection:
                rows = await connection.fetch(prepared_query, *params)
                return [dict(row) for row in rows]
        except asyncpg.PostgresError as e:
            log.error("Failed to fetch all rows: %s\nQuery: %s", e, prepared_query)
            return []

    async def disconnect(self) -> None:
        if self._pool:
            await self._pool.close()
            self._pool = None
            log.info("Database connection pool closed.")