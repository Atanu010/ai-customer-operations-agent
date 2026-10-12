from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Order
from app.db.repositories import OrderRepository


async def get_order_by_id(session: AsyncSession, order_id: int) -> Order | None:
    if order_id <= 0:
        raise ValueError("Order ID must be a positive integer.")
    return await OrderRepository.get_by_id(session, order_id)


async def get_customer_orders(session: AsyncSession, customer_id: int) -> list[Order]:
    if customer_id <= 0:
        raise ValueError("Customer ID must be a positive integer.")
    return await OrderRepository.get_customer_orders(session, customer_id)
