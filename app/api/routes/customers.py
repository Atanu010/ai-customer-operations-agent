from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import async_session_factory
from app.schemas.customer import CustomerDetailResponse, CustomerOrderRead, CustomerRead
from app.services.customer_service import get_customer_by_id, get_customer_orders

router = APIRouter(prefix="/api", tags=["customers"])


async def _resolve_customer(session: AsyncSession, customer_id: int):
    customer = await get_customer_by_id(session, customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    orders = await get_customer_orders(session, customer_id)
    return CustomerDetailResponse(
        customer=CustomerRead.model_validate(customer),
        orders=[
            CustomerOrderRead(
                id=order.id,
                status=order.status,
                product_name=order.product_name,
                tracking_number=order.tracking_number,
                estimated_delivery=order.estimated_delivery.isoformat() if order.estimated_delivery else None,
            )
            for order in orders
        ],
    )


@router.get("/customers/{customer_id}")
async def get_customer(customer_id: Annotated[int, Path(ge=1)]) -> CustomerDetailResponse:
    async with async_session_factory() as session:
        return await _resolve_customer(session, customer_id)


@router.get("/customers/{customer_id}/orders")
async def get_customer_order_list(customer_id: Annotated[int, Path(ge=1)]) -> list[CustomerOrderRead]:
    async with async_session_factory() as session:
        customer = await get_customer_by_id(session, customer_id)
        if customer is None:
            raise HTTPException(status_code=404, detail="Customer not found")
        orders = await get_customer_orders(session, customer_id)
        return [
            CustomerOrderRead(
                id=order.id,
                status=order.status,
                product_name=order.product_name,
                tracking_number=order.tracking_number,
                estimated_delivery=order.estimated_delivery.isoformat() if order.estimated_delivery else None,
            )
            for order in orders
        ]
