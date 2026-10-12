from __future__ import annotations

from pydantic import BaseModel, Field


class AgentQueryRequest(BaseModel):
    message: str = Field(..., min_length=3, max_length=2000)
    customer_id: int | None = None


class AgentToolResult(BaseModel):
    name: str
    success: bool
    data: dict | list | None = None
    error: str | None = None


class AgentResponse(BaseModel):
    intent: str
    answer: str
    actions_taken: list[str] = Field(default_factory=list)
    order_id: int | None = None
    confidence: float = Field(ge=0.0, le=1.0)
    requires_human: bool = False
    requires_tool: bool = False
    tool_used: str | None = None


class SupportInteractionCreateRequest(BaseModel):
    customer_id: int
    request_text: str
    detected_intent: str
    tool_used: str | None = None
    response: str
    success: bool
    latency_ms: int = 0


class SupportInteractionRead(BaseModel):
    id: int
    customer_id: int
    request_text: str
    detected_intent: str
    tool_used: str | None = None
    response: str
    success: bool
    latency_ms: int

    model_config = {"from_attributes": True}
