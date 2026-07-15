import logging

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.configs.environment import EnvKey
from app.services.embeddings.embeddings_service import EmbeddingsService
from app.storage.rds.clients.database_manager import DataBaseManager
from app.storage.vector.vector_store import VectorStore

LOGGER = logging.getLogger(__name__)

_PUBLISHED_QUERY = """
    SELECT article_id, title, content, version
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

    async def _index_article(self, article) -> int:
        chunks = self._splitter.split_text(article["content"] or "")
        if not chunks:
            return 0
        embeddings = self._embeddings.embed(chunks)
        return await self._vector_store.add_chunks(
            article["article_id"],
            article["title"],
            article["version"],
            chunks,
            embeddings,
        )

    async def reindex(self) -> dict:
        await self._vector_store.ensure_schema()
        await self._vector_store.clear()

        articles = await self._db.fetch(_PUBLISHED_QUERY)
        indexed_articles = 0
        indexed_chunks = 0
        for article in articles:
            added = await self._index_article(article)
            if added:
                indexed_articles += 1
                indexed_chunks += added

        LOGGER.info(
            "reindex done: %s articles, %s chunks", indexed_articles, indexed_chunks
        )
        return {"articles": indexed_articles, "chunks": indexed_chunks}

    async def sync(self) -> dict:
        await self._vector_store.ensure_schema()

        articles = await self._db.fetch(_PUBLISHED_QUERY)
        indexed = await self._vector_store.indexed_versions()
        published_ids = set()

        updated = 0
        for article in articles:
            article_id = article["article_id"]
            published_ids.add(article_id)
            if indexed.get(article_id) == article["version"]:
                continue
            await self._vector_store.delete_article(article_id)
            if await self._index_article(article):
                updated += 1

        removed = 0
        for article_id in set(indexed) - published_ids:
            await self._vector_store.delete_article(article_id)
            removed += 1

        LOGGER.info("sync done: %s updated, %s removed", updated, removed)
        return {"updated": updated, "removed": removed}
