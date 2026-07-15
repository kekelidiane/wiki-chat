import asyncio
import logging

from app.configs.environment import EnvKey
from app.services.ingestion.ingestion_service import IngestionService

LOGGER = logging.getLogger(__name__)


def _is_truthy(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


class SyncScheduler:
    def __init__(self, ingestion: IngestionService, config: dict):
        self._ingestion = ingestion
        self._enabled = _is_truthy(config[EnvKey.WIKI_SYNC_ENABLED])
        self._interval = int(config[EnvKey.WIKI_SYNC_INTERVAL_SECONDS])
        self._task: asyncio.Task | None = None

    def start(self) -> None:
        if not self._enabled:
            LOGGER.info("sync scheduler disabled")
            return
        self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        if self._task is None:
            return
        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass
        self._task = None

    async def _run(self) -> None:
        LOGGER.info("sync scheduler started, interval %ss", self._interval)
        while True:
            try:
                await self._ingestion.sync()
            except Exception as exc:
                LOGGER.error("scheduled sync failed: %s", exc)
            await asyncio.sleep(self._interval)
