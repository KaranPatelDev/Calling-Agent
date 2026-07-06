from pydantic import BaseModel
from datetime import datetime


class ContactListCreate(BaseModel):
    name: str
    description: str | None = None


class ContactListResponse(BaseModel):
    id: str
    user_id: str
    name: str
    description: str | None
    contact_count: int
    source: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


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


class BulkUploadResponse(BaseModel):
    total_rows: int
    valid_rows: int
    invalid_rows: int
    duplicates_skipped: int
    list_id: str
    errors: list[dict]


class ImportError(BaseModel):
    row: int
    phone: str | None = None
    errors: list[str]
