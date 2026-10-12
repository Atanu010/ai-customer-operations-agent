from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Customer
from app.db.repositories import CustomerRepository


async def get_customer_by_id(session: AsyncSession, customer_id: int) -> Customer | None:
    if customer_id <= 0:
        raise ValueError("Customer ID must be a positive integer.")
    return await CustomerRepository.get_by_id(session, customer_id)


async def get_customer_orders(session: AsyncSession, customer_id: int) -> list:
    if customer_id <= 0:
        raise ValueError("Customer ID must be a positive integer.")
    return await CustomerRepository.get_orders(session, customer_id)
