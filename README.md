# wiki-chat

Chatbot RAG de la base de connaissances interne. Il répond aux questions
en s'appuyant sur les articles publiés du `wiki`, avec citation des
sources.

## Fonctionnement

1. **Ingestion** — les articles publiés du `wiki_db` sont découpés,
   encodés avec `BAAI/bge-m3` (1024 dimensions) et stockés dans une table
   `pgvector`.
2. **Recherche** — la question est encodée puis comparée aux fragments
   par similarité cosinus (top-k).
3. **Génération** — le contexte retrouvé est envoyé à `llama3.1` via
   Ollama, qui rédige la réponse.

## Prérequis

1. Python 3.11 ou plus
2. PostgreSQL avec l'extension `pgvector`
3. Ollama avec le modèle `llama3.1`
4. Un realm Keycloak pour l'authentification

## Démarrage

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install ".[dev]"
cp .env.example .env      # renseigne WIKI_DB_CONNEXION et les autres variables
python run.py
```

Documentation Swagger : `http://localhost:8081/api/v1/wiki-chat/documentation`

## Endpoints

1. `GET /api/v1/wiki-chat/health` — état du service et de la base.
2. `POST /api/v1/wiki-chat/chat` — pose une question, renvoie réponse +
   sources. Authentifié (token Keycloak).
3. `POST /api/v1/wiki-chat/ingest` — réindexe les articles publiés.
   Réservé aux rôles `manager` et `director`.

## Qualité

```bash
ruff check src tests
black --check src tests
pytest
```
