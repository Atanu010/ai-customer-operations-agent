import pytest

from app.agents.customer_agent import CustomerOperationsAgent
from app.agents.tools import TOOL_REGISTRY
from app.core.config import settings
from app.llm.base import ToolCall
from app.llm.mock_provider import MockLLMProvider
from app.llm.provider import LLMProviderFactory
from app.rag.embeddings import EmbeddingProviderFactory, MockEmbeddingProvider


@pytest.mark.asyncio
async def test_mock_llm_selects_registered_tool() -> None:
    provider = MockLLMProvider()
    calls = await provider.select_tools("Where is my order 1001?")

    assert calls
    assert isinstance(calls[0], ToolCall)
    assert calls[0].tool_name in TOOL_REGISTRY
    assert "order_id" in calls[0].arguments or "customer_id" in calls[0].arguments


@pytest.mark.asyncio
async def test_mock_embedding_provider_generates_vector() -> None:
    provider = EmbeddingProviderFactory.create()
    assert isinstance(provider, MockEmbeddingProvider)

    vector = await provider.embed("return policy after delivery")
    assert isinstance(vector, list)
    assert len(vector) > 0
    assert all(isinstance(value, float) for value in vector)


def test_llm_factory_uses_mock_mode_by_default() -> None:
    original = settings.llm_provider
    settings.llm_provider = "mock"
    try:
        provider = LLMProviderFactory.create()
        assert isinstance(provider, MockLLMProvider)
    finally:
        settings.llm_provider = original


def test_invalid_tool_name_rejected() -> None:
    agent = CustomerOperationsAgent()
    with pytest.raises(ValueError):
        agent._validate_tool_call("not_a_real_tool", {"order_id": 1001})
