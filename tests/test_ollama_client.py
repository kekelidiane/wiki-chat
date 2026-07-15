import aiohttp
import pytest

from app.configs.environment import ENVIRONMENT_CONFIG
from app.core.exceptions.api_exception import ApiErrorsCode, ApiException
from app.services.llm.ollama_client import OllamaClient


class FakeResponse:
    def __init__(self, payload, status=200):
        self._payload = payload
        self._status = status

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    def raise_for_status(self):
        if self._status >= 400:
            raise aiohttp.ClientError(f"http status {self._status}")

    async def json(self):
        return self._payload


class FakeSession:
    def __init__(self, response):
        self._response = response

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    def post(self, url, json=None):
        return self._response


def _patch_session(monkeypatch, response):
    monkeypatch.setattr(aiohttp, "ClientSession", lambda *a, **k: FakeSession(response))


async def test_chat_returns_message_content(monkeypatch):
    _patch_session(monkeypatch, FakeResponse({"message": {"content": "  bonjour  "}}))
    answer = await OllamaClient(ENVIRONMENT_CONFIG).chat("system", "user")
    assert answer == "bonjour"


async def test_chat_raises_when_ollama_down(monkeypatch):
    _patch_session(monkeypatch, FakeResponse({}, status=500))
    with pytest.raises(ApiException) as exc_info:
        await OllamaClient(ENVIRONMENT_CONFIG).chat("system", "user")
    assert exc_info.value.error_code == ApiErrorsCode.LLM_UNAVAILABLE
