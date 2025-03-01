from pydantic import BaseModel
from typing import Union


class Token(BaseModel):
    access_token: str
    token_type: str
    user: list


class TokenData(BaseModel):
    username: Union[str, None] = None