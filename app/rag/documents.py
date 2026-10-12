from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class KnowledgeChunk:
    id: int = 0
    title: str = ""
    content: str = ""
    metadata: dict | None = None
    score: float = 0.0


def chunk_text(text: str, chunk_size: int = 200, overlap: int = 50) -> list[str]:
    if not text:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end]
        chunks.append(chunk.strip())
        if end == len(text):
            break
        start += max(1, chunk_size - overlap)
    return [chunk for chunk in chunks if chunk]
