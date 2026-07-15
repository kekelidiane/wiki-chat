import logging

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.configs.environment import EnvKey
from app.services.embeddings.embeddings_service import EmbeddingsService
from app.storage.rds.clients.database_manager import DataBaseManager
from app.storage.vector.vector_store import VectorStore

LOGGER = logging.getLogger(__name__)

_ARTICLES_QUERY = """
    SELECT article_id, title, content
    FROM articles
    WHERE state = 'PUBLISHED' AND is_deleted = false
"""


class IngestionService:
    def __init__(
        self,
        database_manager: DataBaseManager,
        embeddings: EmbeddingsService,
        vector_store: VectorStore,
        config: dict,
    ):
        self._db = database_manager
        self._embeddings = embeddings
        self._vector_store = vector_store
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=int(config[EnvKey.WIKI_CHUNK_SIZE]),
            chunk_overlap=int(config[EnvKey.WIKI_CHUNK_OVERLAP]),
        )

    async def reindex(self) -> dict:
        await self._vector_store.ensure_schema()
        await self._vector_store.clear()

        articles = await self._db.fetch(_ARTICLES_QUERY)
        indexed_articles = 0
        indexed_chunks = 0
        for article in articles:
            chunks = self._splitter.split_text(article["content"] or "")
            if not chunks:
                continue
            embeddings = self._embeddings.embed(chunks)
            indexed_chunks += await self._vector_store.add_chunks(
                article["article_id"], article["title"], chunks, embeddings
            )
            indexed_articles += 1

        LOGGER.info(
            "reindex done: %s articles, %s chunks", indexed_articles, indexed_chunks
        )
        return {"articles": indexed_articles, "chunks": indexed_chunks}
