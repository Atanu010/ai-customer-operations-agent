from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class CustomerRead(BaseModel):
    id: int
    name: str
    email: EmailStr

    model_config = {"from_attributes": True}


class CustomerOrderRead(BaseModel):
    id: int
    status: str
    product_name: str
    tracking_number: str | None = None
    estimated_delivery: str | None = None

    model_config = {"from_attributes": True}


class CustomerDetailResponse(BaseModel):
    customer: CustomerRead
    orders: list[CustomerOrderRead] = Field(default_factory=list)
