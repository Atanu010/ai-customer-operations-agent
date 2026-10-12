import pytest

from app.db.database import async_session_factory
from app.services.rag_service import RAGService


@pytest.mark.asyncio
async def test_rag_search_returns_documents() -> None:
    async with async_session_factory() as session:
        results = await RAGService().search(session, "Can I return an item after delivery?")
        assert len(results) >= 1
        assert any("return" in result.content.lower() for result in results)
