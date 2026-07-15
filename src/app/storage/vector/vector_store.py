import logging

from app.configs.environment import EnvKey
from app.storage.rds.clients.database_manager import DataBaseManager

LOGGER = logging.getLogger(__name__)


def to_vector_literal(embedding: list[float]) -> str:
    return "[" + ",".join(repr(float(x)) for x in embedding) + "]"


class VectorStore:
    TABLE = "wiki_chunks"

    def __init__(self, database_manager: DataBaseManager, config: dict):
        self._db = database_manager
        self._dim = int(config[EnvKey.WIKI_PGVECTOR_DIM])

    async def ensure_schema(self) -> None:
        await self._db.execute("CREATE EXTENSION IF NOT EXISTS vector")
        await self._db.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.TABLE} (
                id BIGSERIAL PRIMARY KEY,
                article_id TEXT NOT NULL,
                title TEXT NOT NULL,
                chunk_index INT NOT NULL,
                content TEXT NOT NULL,
                embedding vector({self._dim}) NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
            """)
        await self._db.execute(
            f"CREATE INDEX IF NOT EXISTS ix_{self.TABLE}_article_id "
            f"ON {self.TABLE} (article_id)"
        )

    async def clear(self) -> None:
        await self._db.execute(f"TRUNCATE {self.TABLE}")

    async def add_chunks(
        self,
        article_id: str,
        title: str,
        chunks: list[str],
        embeddings: list[list[float]],
    ) -> int:
        rows = [
            (article_id, title, index, content, to_vector_literal(embedding))
            for index, (content, embedding) in enumerate(zip(chunks, embeddings))
        ]
        await self._db.execute_many(
            f"""
            INSERT INTO {self.TABLE}
                (article_id, title, chunk_index, content, embedding)
            VALUES ($1, $2, $3, $4, $5::vector)
            """,
            rows,
        )
        return len(rows)

    async def search(self, embedding: list[float], top_k: int) -> list[dict]:
        literal = to_vector_literal(embedding)
        records = await self._db.fetch(
            f"""
            SELECT article_id, title, content,
                   1 - (embedding <=> $1::vector) AS score
            FROM {self.TABLE}
            ORDER BY embedding <=> $1::vector
            LIMIT $2
            """,
            literal,
            int(top_k),
        )
        return [dict(r) for r in records]
