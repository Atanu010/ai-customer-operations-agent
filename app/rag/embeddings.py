from __future__ import annotations

from abc import ABC, abstractmethod
import re
from collections import Counter

from openai import OpenAI

from app.core.config import settings


class EmbeddingProvider(ABC):
    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        raise NotImplementedError


class MockEmbeddingProvider(EmbeddingProvider):
    async def embed(self, text: str) -> list[float]:
        tokens = re.findall(r"\w+", text.lower())
        if not tokens:
            return [0.0]
        counts = Counter(tokens)
        vocab = sorted(counts)
        vector = [float(counts[t]) for t in vocab]
        magnitude = sum(v * v for v in vector) ** 0.5 or 1.0
        return [v / magnitude for v in vector]


class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(self, client: OpenAI | None = None, model: str | None = None) -> None:
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when EMBEDDING_PROVIDER=openai.")
        self.client = client or OpenAI(api_key=settings.openai_api_key)
        self.model = model or settings.openai_embedding_model

    async def embed(self, text: str) -> list[float]:
        if not text or not text.strip():
            return [0.0]
        response = self.client.embeddings.create(model=self.model, input=text)
        return list(response.data[0].embedding)


class EmbeddingProviderFactory:
    @staticmethod
    def create() -> EmbeddingProvider:
        if settings.embedding_provider == "openai":
            if not settings.openai_api_key:
                raise ValueError("OPENAI_API_KEY is required when EMBEDDING_PROVIDER=openai.")
            return OpenAIEmbeddingProvider()
        return MockEmbeddingProvider()


SimpleEmbeddingProvider = MockEmbeddingProvider
