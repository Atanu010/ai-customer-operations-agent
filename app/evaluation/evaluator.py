from __future__ import annotations

from app.services.evaluation_service import EvaluationService


async def run_evaluation() -> dict:
    service = EvaluationService()
    return await service.run_suite()
