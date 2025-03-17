from datetime import datetime
from pydantic import (
    BaseModel, 
    field_validator, 
    ConfigDict
)
from typing import List, Literal
from uuid import UUID


class OrderItemCreate(BaseModel):
    product_id: UUID
    quantity: int
    unit_price: float

    @field_validator('quantity')
    def validate_quantity(cls, v):
        if v < 1:
            raise ValueError("Quantity must be at least 1")
        return v
    

class PaymentMethod(BaseModel):
    provider: Literal['stripe']
    payment_intent_id: str
    method_type: str
    last4: str


class OrderCreate(BaseModel):
    items: List[OrderItemCreate]
    shipping_address: dict  
    payment_method: PaymentMethod
    checkout_id: str


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

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        },
        arbitrary_types_allowed=True  # Adicione esta linha
    )