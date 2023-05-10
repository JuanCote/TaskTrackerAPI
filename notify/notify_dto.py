from typing import Dict, Optional, List

from pydantic import BaseModel


class MessagePayload(BaseModel):
    username: str
    message: str
    notify: Dict


class ErrorResponse(BaseModel):
    count: int = 0
    errors: Optional[List[Dict]]


class Response(BaseModel):
    success_count: int
    message: str
    error: ErrorResponse


class UserDevicePayload(BaseModel):
    username: str
    token: str