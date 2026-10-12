from __future__ import annotations

import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path

from sqlalchemy import func, select, text
from sqlalchemy.exc import OperationalError

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db.database import Base, async_session_factory, engine
from app.db.models import Customer, KnowledgeDocument, Order


async def wait_for_database(max_retries: int = 30, delay_seconds: int = 2) -> None:
    last_error: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            async with engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            return
        except OperationalError as exc:
            last_error = exc
            if attempt == max_retries:
                raise
            await asyncio.sleep(delay_seconds)
    if last_error is not None:
        raise last_error


async def seed_database() -> None:
    await wait_for_database()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        existing_customers = await session.execute(select(func.count(Customer.id)))
        if existing_customers.scalar_one() > 0:
            return

        customers = [
            Customer(id=1, name="Ava Patel", email="ava.patel@example.com"),
            Customer(id=2, name="Marcus Lee", email="marcus.lee@example.com"),
            Customer(id=3, name="Nina Garcia", email="nina.garcia@example.com"),
        ]
        session.add_all(customers)
        await session.commit()

        orders = [
            Order(
                id=1001,
                customer_id=1,
                status="in_transit",
                tracking_number="TRK-1001",
                product_name="Wireless Headphones",
                estimated_delivery=datetime.utcnow() + timedelta(days=2),
                created_at=datetime.utcnow() - timedelta(days=7),
                updated_at=datetime.utcnow(),
            ),
            Order(
                id=1002,
                customer_id=1,
                status="delivered",
                tracking_number="TRK-1002",
                product_name="Smartwatch",
                estimated_delivery=datetime.utcnow() - timedelta(days=1),
                created_at=datetime.utcnow() - timedelta(days=14),
                updated_at=datetime.utcnow(),
            ),
            Order(
                id=1003,
                customer_id=2,
                status="processing",
                tracking_number="TRK-1003",
                product_name="Desk Lamp",
                estimated_delivery=datetime.utcnow() + timedelta(days=5),
                created_at=datetime.utcnow() - timedelta(days=4),
                updated_at=datetime.utcnow(),
            ),
            Order(
                id=1004,
                customer_id=2,
                status="delivered",
                tracking_number="TRK-1004",
                product_name="Coffee Grinder",
                estimated_delivery=datetime.utcnow() - timedelta(days=3),
                created_at=datetime.utcnow() - timedelta(days=18),
                updated_at=datetime.utcnow(),
            ),
            Order(
                id=1005,
                customer_id=3,
                status="out_for_delivery",
                tracking_number="TRK-1005",
                product_name="Portable Speaker",
                estimated_delivery=datetime.utcnow() + timedelta(days=1),
                created_at=datetime.utcnow() - timedelta(days=9),
                updated_at=datetime.utcnow(),
            ),
        ]
        session.add_all(orders)

        documents = [
            KnowledgeDocument(
                title="Return Policy",
                content="Eligible returns are accepted within 30 days of delivery for unopened items. We provide a prepaid return label for eligible orders, and refunds are processed within 5 to 7 business days after the item is received.",
                document_metadata={"category": "returns"},
            ),
            KnowledgeDocument(
                title="Cancellation Policy",
                content="Orders can be canceled before shipment processing begins. If the order has already left our warehouse, it cannot be canceled and will instead follow the standard return process.",
                document_metadata={"category": "cancellation"},
            ),
            KnowledgeDocument(
                title="Delivery Policy",
                content="Standard delivery takes 3 to 7 business days. Express shipping is available for priority orders. Delays can occur during peak periods or due to carrier issues outside of our control.",
                document_metadata={"category": "delivery"},
            ),
            KnowledgeDocument(
                title="Refund Policy",
                content="Refunds are issued to the original payment method within 5 to 10 business days. Shipping costs are non-refundable unless the item was damaged or incorrectly shipped.",
                document_metadata={"category": "refunds"},
            ),
            KnowledgeDocument(
                title="Damaged Item Policy",
                content="If you receive a damaged or defective item, contact support within 48 hours of delivery. We may request photos and will arrange replacement or refund depending on product availability.",
                document_metadata={"category": "damages"},
            ),
        ]
        session.add_all(documents)
        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed_database())
