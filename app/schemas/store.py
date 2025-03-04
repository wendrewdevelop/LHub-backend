from pydantic import BaseModel
from typing import Union
from uuid import UUID


class StoreBase(BaseModel):
    name: str
    description: str | None = None
    address: str

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