import os

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")

import pytest

from app.db.database import Base, async_session_factory, engine, init_db
from app.db.models import Customer, KnowledgeDocument, Order


@pytest.fixture(autouse=True)
async def initialize_database():
    await init_db()

    async with async_session_factory() as session:
        session.add_all(
            [
                Customer(id=1, name="Ava Patel", email="ava.patel@example.com"),
                Customer(id=2, name="Marcus Lee", email="marcus.lee@example.com"),
                Order(
                    id=1001,
                    customer_id=1,
                    status="in_transit",
                    tracking_number="TRK-1001",
                    product_name="Wireless Headphones",
                ),
                Order(
                    id=1002,
                    customer_id=1,
                    status="delivered",
                    tracking_number="TRK-1002",
                    product_name="Smartwatch",
                ),
                Order(
                    id=1003,
                    customer_id=2,
                    status="processing",
                    tracking_number="TRK-1003",
                    product_name="Desk Lamp",
                ),
                KnowledgeDocument(
                    title="Return Policy",
                    content="Returns are accepted within 30 days of delivery for unopened items. Refunds are processed within 5 to 7 business days.",
                    document_metadata={"category": "returns"},
                ),
                KnowledgeDocument(
                    title="Delivery Policy",
                    content="Standard delivery takes 3 to 7 business days and express shipping is available for priority orders.",
                    document_metadata={"category": "delivery"},
                ),
            ]
        )
        await session.commit()

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
