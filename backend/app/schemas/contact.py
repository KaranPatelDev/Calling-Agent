from pydantic import BaseModel
from datetime import datetime


class ContactCreate(BaseModel):
    phone: str
    name: str | None = None
    email: str | None = None
    company: str | None = None


class ContactResponse(BaseModel):
    id: str
    list_id: str
    phone: str
    name: str | None
    email: str | None
    company: str | None
    dnd_registered: bool
    last_called_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True


class ContactImportRow(BaseModel):
    phone: str
    name: str | None = None
    email: str | None = None
    company: str | None = None
