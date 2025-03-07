from pydantic import BaseModel, computed_field, Field
from typing import List
from uuid import UUID
from app.schemas import ProductBase


class CartItemCreate(BaseModel):
    product_id: UUID
    quantity: int = 1


class CartItemResponse(BaseModel):
    product: ProductBase
    product_id: UUID
    quantity: int
    # unit_price: float
    # total_price: float

    # Campos computados
    @computed_field
    @property
    def unit_price(self) -> float:
        return self.product.price  # type: ignore
    
    @computed_field
    @property
    def total_price(self) -> float:
        return self.unit_price * self.quantity

    class Config:
        from_attributes = True
        populate_by_name = True


class CartResponse(BaseModel):
    id: UUID
    cart_items: List[CartItemResponse] = Field(..., alias="items")

    @computed_field
    @property
    def items(self) -> List[CartItemResponse]:
        return self.cart_items

    @computed_field
    @property
    def total(self) -> float:
        items = type(self).items.fget(self)
        return sum(item.total_price for item in items)

    class Config:
        from_attributes = True
