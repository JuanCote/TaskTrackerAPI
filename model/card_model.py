from typing import Optional

from pydantic import BaseModel


class Card(BaseModel):
    title: str
    date: int  # timestamp
    counter: int


class UpdateCard(BaseModel):
    title: Optional[str]
    counter: Optional[int]
    date: int  # timestamp


class ResponseCard(BaseModel):
    id: str
    title: str
    date: int  # timestamp
    counter: int
    user: str