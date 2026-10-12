from __future__ import annotations

from app.core.config import settings
from app.llm.base import BaseLLMProvider
from app.llm.mock_provider import MockLLMProvider
from app.llm.openai_provider import OpenAICompatibleLLMProvider


class LLMProviderFactory:
    @staticmethod
    def create() -> BaseLLMProvider:
        if settings.llm_provider == "mock":
            return MockLLMProvider()
        if settings.llm_provider == "openai":
            if not settings.openai_api_key:
                raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER=openai.")
            return OpenAICompatibleLLMProvider()
        if not settings.openai_api_key:
            return MockLLMProvider()
        return OpenAICompatibleLLMProvider()
