import os

import pytest

from app.configs.environment import ENVIRONMENT_CONFIG
from app.services.llm.ollama_client import OllamaClient

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not os.getenv("WIKI_IT_OLLAMA"), reason="WIKI_IT_OLLAMA not set"
    ),
]


async def test_chat_against_real_ollama():
    client = OllamaClient(ENVIRONMENT_CONFIG)
    answer = await client.chat(
        "Réponds en un mot.", "Quelle est la capitale de la France ?"
    )
    assert isinstance(answer, str) and answer.strip()
