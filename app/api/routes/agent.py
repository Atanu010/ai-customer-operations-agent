from __future__ import annotations

from fastapi import APIRouter

from app.schemas.agent import AgentQueryRequest, AgentResponse
from app.services.agent_service import AgentService

router = APIRouter(prefix="/api", tags=["agent"])


@router.post("/agent/query", response_model=AgentResponse)
async def query_agent(payload: AgentQueryRequest) -> AgentResponse:
    service = AgentService()
    result = await service.process_query(payload.message, customer_id=payload.customer_id)
    return AgentResponse(**result)
