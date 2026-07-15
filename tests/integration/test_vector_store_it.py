import os

import pytest

from app.configs.environment import EnvKey
from app.storage.rds.clients.database_manager import DataBaseManager
from app.storage.vector.vector_store import VectorStore

_IT_DB = os.getenv("WIKI_IT_DB")

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(not _IT_DB, reason="WIKI_IT_DB not set"),
]


def _config():
    return {
        EnvKey.WIKI_DB_CONNEXION: _IT_DB,
        EnvKey.WIKI_DB_MIN_CON: "1",
        EnvKey.WIKI_DB_MAX_CON: "2",
        EnvKey.WIKI_PGVECTOR_DIM: "4",
    }


async def test_add_search_delete_roundtrip():
    config = _config()
    db = DataBaseManager(config)
    await db.connect()
    store = VectorStore(db, config)
    try:
        await store.ensure_schema()
        await store.clear()

        await store.add_chunks(
            "a1", "Title A", 1, ["hello", "world"], [[1, 0, 0, 0], [0, 1, 0, 0]]
        )
        assert await store.indexed_versions() == {"a1": 1}

        matches = await store.search([1, 0, 0, 0], top_k=1)
        assert matches and matches[0]["article_id"] == "a1"

        await store.delete_article("a1")
        assert await store.indexed_versions() == {}
    finally:
        await store.clear()
        await db.close()
