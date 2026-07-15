import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.configs.environment import ENVIRONMENT_CONFIG
from app.configs.logger_config import init_logging
from app.services.factory.services_factory import CHAT_SERVICES, SYNC_SCHEDULER
from app.storage.rds.clients.database_manager import DATA_BASE_MANAGER
from app.storage.vector.vector_store import VectorStore

LOGGER = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_logging()
    LOGGER.info("wiki-chat starting")
    await DATA_BASE_MANAGER.connect()
    await VectorStore(DATA_BASE_MANAGER, ENVIRONMENT_CONFIG).ensure_schema()
    CHAT_SERVICES.embeddings_service.warm_up()
    SYNC_SCHEDULER.start()
    LOGGER.info("wiki-chat started")
    yield
    LOGGER.info("wiki-chat shutting down")
    await SYNC_SCHEDULER.stop()
    await DATA_BASE_MANAGER.close()
