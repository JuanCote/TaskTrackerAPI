from pydantic import BaseModel, Field


class AuthUser(BaseModel):
    username: str = Field(max_length=20, min_length=6)
    password: str = Field(max_length=30, min_length=6)