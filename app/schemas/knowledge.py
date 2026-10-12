from __future__ import annotations

from pydantic import BaseModel, Field


class KnowledgeSearchRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=1000)
    top_k: int = Field(default=5, ge=1, le=10)


class KnowledgeSearchResultItem(BaseModel):
    id: int
    title: str
    content: str
    metadata: dict | None = None
    score: float


class KnowledgeSearchResponse(BaseModel):
    query: str
    results: list[KnowledgeSearchResultItem] = Field(default_factory=list)
