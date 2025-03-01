from uuid import UUID
from pydantic import BaseModel
from typing import Union


class AuthAccountToken(BaseModel):
    token: str


class AccountInput(BaseModel):
    email: str
    password: str

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class AccountOutput(BaseModel):
    email: str
    password: str

    class config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True