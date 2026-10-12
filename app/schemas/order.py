from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class OrderRead(BaseModel):
    id: int
    customer_id: int
    status: str
    tracking_number: str | None = None
    product_name: str
    estimated_delivery: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class OrderStatusResponse(BaseModel):
    order_id: int
    status: str
    tracking_number: str | None = None
    product_name: str
    estimated_delivery: datetime | None = None
