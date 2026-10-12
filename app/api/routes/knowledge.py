from __future__ import annotations

from fastapi import APIRouter

from app.db.database import async_session_factory
from app.rag.documents import KnowledgeChunk
from app.schemas.knowledge import KnowledgeSearchRequest, KnowledgeSearchResponse, KnowledgeSearchResultItem
from app.services.rag_service import RAGService

router = APIRouter(prefix="/api", tags=["knowledge"])


@router.post("/knowledge/search", response_model=KnowledgeSearchResponse)
async def search_knowledge(payload: KnowledgeSearchRequest) -> KnowledgeSearchResponse:
    async with async_session_factory() as session:
        results = await RAGService().search(session, payload.query, top_k=payload.top_k)
    mapped = [
        KnowledgeSearchResultItem(
            id=result.id,
            title=result.title,
            content=result.content,
            metadata=result.metadata if hasattr(result, "metadata") else result.document_metadata,
            score=round(float(result.score), 4),
        )
        for result in results
    ]
    return KnowledgeSearchResponse(query=payload.query, results=mapped)
