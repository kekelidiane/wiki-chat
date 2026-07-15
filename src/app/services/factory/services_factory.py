from app.configs.environment import ENVIRONMENT_CONFIG
from app.services.embeddings.embeddings_service import EmbeddingsService
from app.services.health.health_check_service import HealthCheckService
from app.services.ingestion.ingestion_service import IngestionService
from app.services.llm.ollama_client import OllamaClient
from app.services.rag.rag_service import RagService
from app.storage.rds.clients.database_manager import DATA_BASE_MANAGER
from app.storage.vector.vector_store import VectorStore


class ChatServices:
    def __init__(
        self,
        health_check_service: HealthCheckService,
        rag_service: RagService,
        ingestion_service: IngestionService,
        embeddings_service: EmbeddingsService,
    ):
        self._health_check_service = health_check_service
        self._rag_service = rag_service
        self._ingestion_service = ingestion_service
        self._embeddings_service = embeddings_service

    @property
    def health_check_service(self) -> HealthCheckService:
        return self._health_check_service

    @property
    def rag_service(self) -> RagService:
        return self._rag_service

    @property
    def ingestion_service(self) -> IngestionService:
        return self._ingestion_service

    @property
    def embeddings_service(self) -> EmbeddingsService:
        return self._embeddings_service


class ServicesFactory:
    def __init__(self, provider: ChatServices):
        self._provider = provider

    def __call__(self) -> ChatServices:
        return self._provider


_EMBEDDINGS = EmbeddingsService(ENVIRONMENT_CONFIG)
_VECTOR_STORE = VectorStore(DATA_BASE_MANAGER, ENVIRONMENT_CONFIG)
_OLLAMA = OllamaClient(ENVIRONMENT_CONFIG)

CHAT_SERVICES = ChatServices(
    HealthCheckService(DATA_BASE_MANAGER),
    RagService(_EMBEDDINGS, _VECTOR_STORE, _OLLAMA, ENVIRONMENT_CONFIG),
    IngestionService(DATA_BASE_MANAGER, _EMBEDDINGS, _VECTOR_STORE, ENVIRONMENT_CONFIG),
    _EMBEDDINGS,
)
CHAT_FACTORY = ServicesFactory(CHAT_SERVICES)
