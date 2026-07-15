import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.configs.environment import ENVIRONMENT_CONFIG, EnvKey
from app.configs.logger_config import LOGGING_CONFIG, RequestIdMiddleware
from app.configs.router_config import api_router
from app.hooks.startup_shutdown_events import lifespan


class WikiChatServer:
    def __init__(self):
        prefix = ENVIRONMENT_CONFIG[EnvKey.WIKI_ROUTE_PREFIX]
        fast_api = FastAPI(
            title="Wiki ChatBot server",
            description="RAG chatbot over the internal wiki",
            version=ENVIRONMENT_CONFIG[EnvKey.WIKI_API_VERSION],
            openapi_url=prefix + "/openapi.json",
            docs_url=prefix + "/documentation",
            redoc_url=prefix + "/redoc",
            lifespan=lifespan,
        )
        fast_api.include_router(api_router, prefix=prefix)
        fast_api.add_middleware(RequestIdMiddleware)
        fast_api.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        )
        self._fast_api = fast_api

    def run(self):
        uvicorn.run(
            self._fast_api,
            host=ENVIRONMENT_CONFIG[EnvKey.WIKI_BINDING_HOST],
            port=int(ENVIRONMENT_CONFIG[EnvKey.WIKI_BINDING_PORT]),
            log_level=ENVIRONMENT_CONFIG[EnvKey.WIKI_LOG_LEVEL],
            log_config=LOGGING_CONFIG,
        )

    @property
    def fast_api(self) -> FastAPI:
        return self._fast_api
