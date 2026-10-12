from __future__ import annotations

from fastapi import APIRouter

from app.db.database import async_session_factory
from app.db.repositories import SupportInteractionRepository
from app.schemas.agent import SupportInteractionCreateRequest, SupportInteractionRead

router = APIRouter(prefix="/api", tags=["interactions"])


@router.post("/interactions", response_model=SupportInteractionRead)
async def create_interaction(payload: SupportInteractionCreateRequest) -> SupportInteractionRead:
    async with async_session_factory() as session:
        interaction = await SupportInteractionRepository.create(
            session,
            customer_id=payload.customer_id,
            request_text=payload.request_text,
            detected_intent=payload.detected_intent,
            tool_used=payload.tool_used,
            response=payload.response,
            success=payload.success,
            latency_ms=payload.latency_ms,
        )
        return SupportInteractionRead.model_validate(interaction)
