from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories import KnowledgeRepository
from app.rag.documents import KnowledgeChunk, chunk_text
from app.rag.embeddings import EmbeddingProvider, EmbeddingProviderFactory
from app.rag.retrieval import Retriever


class RAGService:
    def __init__(self, embedding_provider: EmbeddingProvider | None = None):
        self.embedding_provider = embedding_provider or EmbeddingProviderFactory.create()

    async def search(self, session: AsyncSession, query: str, top_k: int = 5) -> list[KnowledgeChunk]:
        if not query or len(query.strip()) < 2:
            raise ValueError("Query must be at least 2 characters long.")

        documents = await KnowledgeRepository.list_documents(session)
        if not documents:
            return []

        query_vector = await self.embedding_provider.embed(query)
        scored: list[KnowledgeChunk] = []

        for document in documents:
            for chunk in chunk_text(document.content, chunk_size=300, overlap=80):
                chunk_vector = await self.embedding_provider.embed(chunk)
                score = Retriever.cosine_similarity(query_vector, chunk_vector)
                scored.append(
                    KnowledgeChunk(
                        id=document.id,
                        title=document.title,
                        content=chunk,
                        metadata=document.document_metadata,
                        score=score,
                    )
                )

        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:top_k]
