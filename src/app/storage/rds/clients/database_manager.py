import logging

import asyncpg

from app.configs.environment import ENVIRONMENT_CONFIG, EnvKey

LOGGER = logging.getLogger(__name__)


class DataBaseManager:
    def __init__(self, config: dict):
        self._config = config
        self._pool: asyncpg.Pool | None = None

    async def connect(self) -> None:
        self._pool = await asyncpg.create_pool(
            self._config[EnvKey.WIKI_DB_CONNEXION],
            min_size=int(self._config[EnvKey.WIKI_DB_MIN_CON]),
            max_size=int(self._config[EnvKey.WIKI_DB_MAX_CON]),
        )

    async def close(self) -> None:
        if self._pool is not None:
            await self._pool.close()
            self._pool = None

    def _ensure_pool(self) -> asyncpg.Pool:
        if self._pool is None:
            raise RuntimeError(
                "Database pool is not initialized. Call connect() at startup."
            )
        return self._pool

    async def execute(self, query: str, *args, timeout: float | None = None):
        try:
            return await self._ensure_pool().execute(query, *args, timeout=timeout)
        except Exception as exc:
            LOGGER.error("execute failed: %s", exc)
            raise

    async def execute_many(self, query: str, args, timeout: float | None = None):
        try:
            return await self._ensure_pool().executemany(query, args, timeout=timeout)
        except Exception as exc:
            LOGGER.error("execute_many failed: %s", exc)
            raise

    async def fetch(self, query: str, *args, timeout: float | None = None) -> list:
        try:
            return await self._ensure_pool().fetch(query, *args, timeout=timeout)
        except Exception as exc:
            LOGGER.error("fetch failed: %s", exc)
            raise

    async def fetch_row(self, query: str, *args, timeout: float | None = None):
        try:
            return await self._ensure_pool().fetchrow(query, *args, timeout=timeout)
        except Exception as exc:
            LOGGER.error("fetch_row failed: %s", exc)
            raise


DATA_BASE_MANAGER = DataBaseManager(ENVIRONMENT_CONFIG)
