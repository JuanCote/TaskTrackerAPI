from pydantic import BaseModel


class Message(BaseModel):
    sender: str
    receiver: str
    message: str
    time: int  # timestamp
    id: int