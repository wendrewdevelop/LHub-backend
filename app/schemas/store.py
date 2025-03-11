from pydantic import BaseModel, Field
from typing import Union, Optional
from uuid import UUID


class StoreBase(BaseModel):
    name: str = Field(..., min_length=3)
    address: str = Field(..., min_length=5)
    cep: str = Field(..., pattern=r'^\d{5}-\d{3}$')
    delivery_fee: float = Field(ge=0)
    description: Optional[str] = None

    class Config:
        from_attributes = True


class StoreInput(StoreBase):
    account_id: UUID

    class Config:
        from_attributes = True


class StoreOutput(StoreBase):
    id: UUID
    account_id: UUID

    class Config:
        from_attributes = True
        json_encoders = {
            UUID: lambda v: str(v),
        }