import logging

import aiohttp
from starlette.status import HTTP_503_SERVICE_UNAVAILABLE

from app.configs.environment import EnvKey
from app.core.exceptions.api_exception import ApiErrorsCode, ApiException

LOGGER = logging.getLogger(__name__)


class OllamaClient:
    def __init__(self, config: dict):
        self._url = config[EnvKey.WIKI_OLLAMA_URL].rstrip("/")
        self._model = config[EnvKey.WIKI_LLM_MODEL_NAME]

    async def chat(self, system_prompt: str, user_prompt: str) -> str:
        payload = {
            "model": self._model,
            "stream": False,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self._url}/api/chat", json=payload
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
        except Exception as exc:
            LOGGER.error("ollama call failed: %s", exc)
            raise ApiException(
                status_code=HTTP_503_SERVICE_UNAVAILABLE,
                error_code=ApiErrorsCode.LLM_UNAVAILABLE,
                message="language model unavailable",
            )
        return data.get("message", {}).get("content", "").strip()
