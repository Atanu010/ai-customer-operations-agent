from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, HTTPException, Path

from app.db.database import async_session_factory
from app.schemas.order import OrderRead
from app.services.order_service import get_order_by_id

router = APIRouter(prefix="/api", tags=["orders"])


@router.get("/orders/{order_id}")
async def get_order(order_id: Annotated[int, Path(ge=1)]) -> OrderRead:
    async with async_session_factory() as session:
        try:
            order = await get_order_by_id(session, order_id)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        if order is None:
            raise HTTPException(status_code=404, detail="Order not found")
        return OrderRead.model_validate(order)
