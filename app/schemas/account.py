from uuid import UUID
from pydantic import BaseModel
from typing import Union


class AuthAccountToken(BaseModel):
    token: str

    class Config:
        from_attributes = True


class AccountInput(BaseModel):
    email: str
    password: str

    class Config:
        from_attributes = True


class AccountOutput(BaseModel):
    email: str
    message: str

    class Config:
        from_attributes = True