import os
from enum import Enum, auto


class EnvKey(Enum):
    WIKI_API_VERSION = auto()
    WIKI_API_NAME = auto()
    WIKI_BINDING_HOST = auto()
    WIKI_BINDING_PORT = auto()
    WIKI_ROUTE_PREFIX = auto()
    WIKI_LOG_LEVEL = auto()
    WIKI_DB_CONNEXION = auto()
    WIKI_DB_MIN_CON = auto()
    WIKI_DB_MAX_CON = auto()
    WIKI_EMBEDDINGS_MODEL_NAME = auto()
    WIKI_LLM_MODEL_NAME = auto()
    WIKI_OLLAMA_URL = auto()
    WIKI_PGVECTOR_DIM = auto()
    WIKI_TOP_K = auto()
    WIKI_CHUNK_SIZE = auto()
    WIKI_CHUNK_OVERLAP = auto()
    WIKI_JWT_AUTHORITY_DOMAIN = auto()
    WIKI_KC_REALM = auto()
    WIKI_KC_CLIENT_ID = auto()
    WIKI_ALLOWED_ORIGINS = auto()
    WIKI_ALLOWED_HOSTS = auto()
    WIKI_SYNC_ENABLED = auto()
    WIKI_SYNC_INTERVAL_SECONDS = auto()


# Non-sensitive defaults. Secrets have no default and come from the environment.
_DEFAULTS: dict[str, str] = {
    "WIKI_API_VERSION": "v1",
    "WIKI_API_NAME": "wiki-chat",
    "WIKI_BINDING_HOST": "0.0.0.0",
    "WIKI_BINDING_PORT": "8081",
    "WIKI_LOG_LEVEL": "debug",
    "WIKI_DB_MIN_CON": "5",
    "WIKI_DB_MAX_CON": "50",
    "WIKI_EMBEDDINGS_MODEL_NAME": "BAAI/bge-m3",
    "WIKI_LLM_MODEL_NAME": "llama3.1",
    "WIKI_OLLAMA_URL": "http://localhost:11434",
    "WIKI_PGVECTOR_DIM": "1024",
    "WIKI_TOP_K": "5",
    "WIKI_CHUNK_SIZE": "800",
    "WIKI_CHUNK_OVERLAP": "120",
    "WIKI_JWT_AUTHORITY_DOMAIN": "https://auth.wearedigijob.com",
    "WIKI_KC_REALM": "digijob",
    "WIKI_KC_CLIENT_ID": "wiki",
    "WIKI_ALLOWED_ORIGINS": "http://localhost:3000",
    "WIKI_ALLOWED_HOSTS": "localhost,127.0.0.1",
    "WIKI_SYNC_ENABLED": "true",
    "WIKI_SYNC_INTERVAL_SECONDS": "300",
}

# Variables that must be supplied by the environment (no safe default).
_REQUIRED = {"WIKI_DB_CONNEXION"}


def _load() -> dict[EnvKey, str]:
    config: dict[EnvKey, str] = {}
    for key in EnvKey:
        if key is EnvKey.WIKI_ROUTE_PREFIX:
            continue
        value = os.environ.get(key.name, _DEFAULTS.get(key.name))
        if value is None and key.name in _REQUIRED:
            raise RuntimeError(f"Missing required environment variable: {key.name}")
        config[key] = value

    version = config[EnvKey.WIKI_API_VERSION]
    name = config[EnvKey.WIKI_API_NAME]
    config[EnvKey.WIKI_ROUTE_PREFIX] = f"/api/{version}/{name}"
    return config


ENVIRONMENT_CONFIG = _load()
