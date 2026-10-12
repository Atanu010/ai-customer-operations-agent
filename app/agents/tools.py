from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Customer, KnowledgeDocument, Order
from app.db.repositories import KnowledgeRepository

logger = logging.getLogger("ai_customer_ops")


def validate_positive_int(value: Any, name: str) -> int:
    if value is None or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer.")
    return value


async def get_order_status(session: AsyncSession, order_id: int) -> dict[str, Any]:
    order_id = validate_positive_int(order_id, "order_id")
    order = await session.get(Order, order_id)
    if order is None:
        return {"status": "not_found", "order_id": order_id, "message": "Order was not found."}
    logger.info("Tool executed: get_order_status order_id=%s", order_id)
    return {
        "status": "ok",
        "tool_name": "get_order_status",
        "order_id": order.id,
        "order": {
            "id": order.id,
            "customer_id": order.customer_id,
            "status": order.status,
            "tracking_number": order.tracking_number,
            "product_name": order.product_name,
            "estimated_delivery": order.estimated_delivery.isoformat() if order.estimated_delivery else None,
        },
    }


async def get_order_details(session: AsyncSession, order_id: int) -> dict[str, Any]:
    order_id = validate_positive_int(order_id, "order_id")
    order = await session.get(Order, order_id)
    if order is None:
        return {"status": "not_found", "order_id": order_id, "message": "Order not found."}
    logger.info("Tool executed: get_order_details order_id=%s", order_id)
    return {
        "status": "ok",
        "tool_name": "get_order_details",
        "order_id": order.id,
        "order": {
            "id": order.id,
            "customer_id": order.customer_id,
            "status": order.status,
            "tracking_number": order.tracking_number,
            "product_name": order.product_name,
            "estimated_delivery": order.estimated_delivery.isoformat() if order.estimated_delivery else None,
            "created_at": order.created_at.isoformat() if order.created_at else None,
        },
    }


async def get_customer_orders(session: AsyncSession, customer_id: int) -> dict[str, Any]:
    customer_id = validate_positive_int(customer_id, "customer_id")
    customer = await session.get(Customer, customer_id)
    if customer is None:
        return {"status": "not_found", "customer_id": customer_id, "message": "Customer not found."}
    result = await session.execute(
        __import__("sqlalchemy").select(Order).where(Order.customer_id == customer_id).order_by(Order.created_at.desc())
    )
    orders = result.scalars().all()
    logger.info("Tool executed: get_customer_orders customer_id=%s count=%d", customer_id, len(orders))
    return {
        "status": "ok",
        "tool_name": "get_customer_orders",
        "customer_id": customer_id,
        "orders": [
            {
                "id": order.id,
                "status": order.status,
                "product_name": order.product_name,
                "tracking_number": order.tracking_number,
                "estimated_delivery": order.estimated_delivery.isoformat() if order.estimated_delivery else None,
            }
            for order in orders
        ],
    }


async def search_knowledge_base(session: AsyncSession, query: str) -> dict[str, Any]:
    if not query or len(query.strip()) < 2:
        raise ValueError("Query must be at least 2 characters long.")
    documents = await KnowledgeRepository.search(session, query, top_k=3)
    logger.info("Tool executed: search_knowledge_base query=%s count=%d", query, len(documents))
    return {
        "status": "ok",
        "tool_name": "search_knowledge_base",
        "query": query,
        "results": [
            {
                "id": document.id,
                "title": document.title,
                "content": document.content[:500],
                "metadata": document.document_metadata,
            }
            for document in documents
        ],
    }


async def create_support_interaction(
    session: AsyncSession,
    *,
    customer_id: int,
    request_text: str,
    detected_intent: str,
    tool_used: str | None,
    response: str,
    success: bool,
    latency_ms: int,
) -> dict[str, Any]:
    customer_id = validate_positive_int(customer_id, "customer_id")
    if not request_text or not request_text.strip():
        raise ValueError("request_text cannot be empty.")
    interaction = __import__("app.db.models", fromlist=["SupportInteraction"]).SupportInteraction(
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
    logger.info("Tool executed: create_support_interaction id=%s customer_id=%s", interaction.id, customer_id)
    return {
        "status": "ok",
        "tool_name": "create_support_interaction",
        "interaction_id": interaction.id,
        "success": success,
    }


TOOL_REGISTRY: dict[str, Any] = {
    "get_order_status": get_order_status,
    "get_order_details": get_order_details,
    "get_customer_orders": get_customer_orders,
    "search_knowledge_base": search_knowledge_base,
    "create_support_interaction": create_support_interaction,
}
