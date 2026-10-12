from __future__ import annotations

from fastapi import APIRouter

from app.services.evaluation_service import EvaluationService

router = APIRouter(prefix="/api", tags=["evaluation"])


@router.post("/evaluation/run")
async def run_evaluation() -> dict:
    service = EvaluationService()
    return await service.run_suite()


@router.get("/evaluation/latest")
async def get_latest_evaluation() -> dict:
    service = EvaluationService()
    return service.latest_summary or {"message": "No evaluation has been run yet."}
