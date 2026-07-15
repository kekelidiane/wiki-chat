from app.configs.environment import ENVIRONMENT_CONFIG
from app.services.ingestion.ingestion_service import IngestionService


class FakeEmbeddings:
    def embed(self, texts):
        return [[0.0] for _ in texts]


class FakeVectorStore:
    def __init__(self, indexed=None):
        self._indexed = dict(indexed or {})
        self.deleted = []
        self.added = []

    async def ensure_schema(self):
        pass

    async def indexed_versions(self):
        return dict(self._indexed)

    async def delete_article(self, article_id):
        self.deleted.append(article_id)
        self._indexed.pop(article_id, None)

    async def add_chunks(self, article_id, title, version, chunks, embeddings):
        self.added.append(article_id)
        self._indexed[article_id] = version
        return len(chunks)


class FakeDb:
    def __init__(self, rows):
        self._rows = rows

    async def fetch(self, query, *args):
        return self._rows


def _service(db, vector_store):
    return IngestionService(db, FakeEmbeddings(), vector_store, ENVIRONMENT_CONFIG)


async def test_sync_indexes_new_article():
    db = FakeDb([{"article_id": "a1", "title": "T", "content": "hello", "version": 1}])
    store = FakeVectorStore()
    result = await _service(db, store).sync()
    assert result == {"updated": 1, "removed": 0}
    assert store.added == ["a1"]


async def test_sync_skips_unchanged_article():
    db = FakeDb([{"article_id": "a1", "title": "T", "content": "hello", "version": 3}])
    store = FakeVectorStore(indexed={"a1": 3})
    result = await _service(db, store).sync()
    assert result == {"updated": 0, "removed": 0}
    assert store.added == []
    assert store.deleted == []


async def test_sync_reindexes_changed_version():
    db = FakeDb([{"article_id": "a1", "title": "T", "content": "hello", "version": 4}])
    store = FakeVectorStore(indexed={"a1": 2})
    result = await _service(db, store).sync()
    assert result == {"updated": 1, "removed": 0}
    assert store.deleted == ["a1"]
    assert store.added == ["a1"]


async def test_sync_removes_unpublished_article():
    db = FakeDb([])
    store = FakeVectorStore(indexed={"old": 1})
    result = await _service(db, store).sync()
    assert result == {"updated": 0, "removed": 1}
    assert store.deleted == ["old"]
