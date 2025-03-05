from datetime import datetime
from pydantic import (
    BaseModel, 
    field_validator, 
    ConfigDict
)
from typing import List
from uuid import UUID


class OrderItemCreate(BaseModel):
    product_id: UUID
    quantity: int
    unit_price: float
    account_id: UUID

    @field_validator('quantity')
    def validate_quantity(cls, v):
        if v < 1:
            raise ValueError("Quantity must be at least 1")
        return v


class OrderCreate(BaseModel):
    items: List[OrderItemCreate]
    shipping_address: dict  
    payment_method: dict    


class OrderItemResponse(BaseModel):
    product_id: UUID
    quantity: int
    unit_price: float


class OrderResponse(BaseModel):
    id: UUID
    store_id: UUID
    total_amount: float
    status: str
    created_at: datetime
    items: List[OrderItemResponse]
    account_id: UUID

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        },
        arbitrary_types_allowed=True  # Adicione esta linha
    )