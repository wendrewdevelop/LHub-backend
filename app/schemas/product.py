from pydantic import BaseModel
from typing import Union
from uuid import UUID


class ProductBase(BaseModel):
    name: str
    description: str | None = None
    price: float
    in_stock: bool
    qtd_in_stock: int
    ready_delivery: bool

    class Config:
        from_attributes = True


class ProductInput(ProductBase):
    account_id: UUID

    class Config:
        from_attributes = True


class ProductOutput(ProductBase):
    id: UUID
    account_id: UUID

    class Config:
        from_attributes = True
        json_encoders = {
            UUID: lambda v: str(v)
        }