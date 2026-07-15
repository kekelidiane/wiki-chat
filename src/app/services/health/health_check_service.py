import logging

from app.storage.rds.clients.database_manager import DataBaseManager

LOGGER = logging.getLogger(__name__)


class HealthCheckService:
    def __init__(self, database_manager: DataBaseManager):
        self._db = database_manager

    async def check(self) -> dict:
        try:
            await self._db.fetch_row("SELECT 1")
            database = "up"
        except Exception as exc:
            LOGGER.error("database health check failed: %s", exc)
            database = "down"
        return {"status": "ok", "database": database}
