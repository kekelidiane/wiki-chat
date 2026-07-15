from fastapi import APIRouter

from app.api.routes.chat.chat_api import router as chat_router
from app.api.routes.health.health_check_api import router as health_router
from app.api.routes.ingest.ingest_api import router as ingest_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["Health"])
api_router.include_router(chat_router, tags=["Chat"])
api_router.include_router(ingest_router, tags=["Ingest"])
