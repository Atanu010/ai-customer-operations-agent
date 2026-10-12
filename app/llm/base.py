from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field


class IntentClassification(BaseModel):
    intent: str
    order_id: int | None = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    requires_tool: bool = False


class ToolCall(BaseModel):
    tool_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class BaseLLMProvider(ABC):
    @abstractmethod
    async def classify_intent(self, message: str) -> IntentClassification:
        raise NotImplementedError

    @abstractmethod
    async def select_tools(self, message: str, tools: list[dict[str, Any]] | None = None) -> list[ToolCall]:
        raise NotImplementedError

    @abstractmethod
    async def generate_response(self, *, message: str, intent: str, tool_result: dict[str, Any] | None = None) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def generate_embedding(self, text: str) -> list[float]:
        raise NotImplementedError
