from pydantic import BaseModel, EmailStr
from datetime import datetime


class MessageResponse(BaseModel):
    message: str


class ErrorResponse(BaseModel):
    detail: str


class PaginationParams(BaseModel):
    page: int = 1
    limit: int = 20


class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    pages: int
