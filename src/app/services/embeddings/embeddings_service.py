import logging

from app.configs.environment import EnvKey

LOGGER = logging.getLogger(__name__)


class EmbeddingsService:
    def __init__(self, config: dict):
        self._model_name = config[EnvKey.WIKI_EMBEDDINGS_MODEL_NAME]
        self._model = None

    def _ensure_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            LOGGER.info("loading embeddings model %s", self._model_name)
            self._model = SentenceTransformer(self._model_name)
        return self._model

    def warm_up(self) -> None:
        self._ensure_model()

    def embed(self, texts: list[str]) -> list[list[float]]:
        model = self._ensure_model()
        vectors = model.encode(texts, normalize_embeddings=True)
        return [v.tolist() for v in vectors]

    def embed_one(self, text: str) -> list[float]:
        return self.embed([text])[0]
