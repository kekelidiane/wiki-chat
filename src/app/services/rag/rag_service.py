import logging

from starlette.status import HTTP_400_BAD_REQUEST

from app.configs.environment import EnvKey
from app.core.exceptions.api_exception import ApiErrorsCode, ApiException
from app.services.embeddings.embeddings_service import EmbeddingsService
from app.services.llm.ollama_client import OllamaClient
from app.storage.vector.vector_store import VectorStore

LOGGER = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "Tu es l'assistant de la base de connaissances interne. "
    "Réponds uniquement à partir du contexte fourni. "
    "Si le contexte ne contient pas la réponse, dis-le clairement. "
    "Réponds en français."
)


class RagService:
    def __init__(
        self,
        embeddings: EmbeddingsService,
        vector_store: VectorStore,
        llm: OllamaClient,
        config: dict,
    ):
        self._embeddings = embeddings
        self._vector_store = vector_store
        self._llm = llm
        self._top_k = int(config[EnvKey.WIKI_TOP_K])

    async def answer(self, question: str) -> dict:
        question = (question or "").strip()
        if not question:
            raise ApiException(
                status_code=HTTP_400_BAD_REQUEST,
                error_code=ApiErrorsCode.EMPTY_QUESTION,
                message="question must not be empty",
            )

        query_embedding = self._embeddings.embed_one(question)
        matches = await self._vector_store.search(query_embedding, self._top_k)

        if not matches:
            return {
                "answer": "Aucun document pertinent trouvé dans la base.",
                "sources": [],
            }

        context = "\n\n".join(f"[{m['title']}]\n{m['content']}" for m in matches)
        user_prompt = f"Contexte:\n{context}\n\nQuestion: {question}"
        answer = await self._llm.chat(_SYSTEM_PROMPT, user_prompt)

        sources = []
        seen = set()
        for match in matches:
            if match["article_id"] in seen:
                continue
            seen.add(match["article_id"])
            sources.append({"article_id": match["article_id"], "title": match["title"]})

        return {"answer": answer, "sources": sources}
