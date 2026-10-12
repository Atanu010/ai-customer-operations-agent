from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Customer, KnowledgeDocument, Order, SupportInteraction


class CustomerRepository:
    @staticmethod
    async def get_by_id(session: AsyncSession, customer_id: int) -> Customer | None:
        result = await session.execute(select(Customer).where(Customer.id == customer_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_orders(session: AsyncSession, customer_id: int) -> list[Order]:
        result = await session.execute(select(Order).where(Order.customer_id == customer_id).order_by(Order.created_at.desc()))
        return list(result.scalars().all())


class OrderRepository:
    @staticmethod
    async def get_by_id(session: AsyncSession, order_id: int) -> Order | None:
        result = await session.execute(select(Order).where(Order.id == order_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_customer_orders(session: AsyncSession, customer_id: int) -> list[Order]:
        result = await session.execute(select(Order).where(Order.customer_id == customer_id).order_by(Order.created_at.desc()))
        return list(result.scalars().all())


class SupportInteractionRepository:
    @staticmethod
    async def create(
        session: AsyncSession,
        *,
        customer_id: int,
        request_text: str,
        detected_intent: str,
        tool_used: str | None,
        response: str,
        success: bool,
        latency_ms: int,
    ) -> SupportInteraction:
        interaction = SupportInteraction(
            customer_id=customer_id,
            request_text=request_text,
            detected_intent=detected_intent,
            tool_used=tool_used,
            response=response,
            success=success,
            latency_ms=latency_ms,
        )
        session.add(interaction)
        await session.commit()
        await session.refresh(interaction)
        return interaction


class KnowledgeRepository:
    @staticmethod
    async def list_documents(session: AsyncSession) -> list[KnowledgeDocument]:
        result = await session.execute(select(KnowledgeDocument).order_by(KnowledgeDocument.created_at.desc()))
        return list(result.scalars().all())

    @staticmethod
    async def search(session: AsyncSession, query: str, top_k: int = 5) -> list[KnowledgeDocument]:
        result = await session.execute(
            select(KnowledgeDocument)
            .where(KnowledgeDocument.content.ilike(f"%{query}%"))
            .order_by(KnowledgeDocument.created_at.desc())
            .limit(top_k)
        )
        return list(result.scalars().all())
