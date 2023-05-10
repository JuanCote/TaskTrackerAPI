from pydantic import BaseModel


class Message(BaseModel):
    sender: str
    receiver: str
    message: str
    date: int  # timestamp
    id: int