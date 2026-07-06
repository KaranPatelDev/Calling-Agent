from pydantic import BaseModel
from datetime import datetime


class CampaignCreate(BaseModel):
    name: str
    script_id: str
    list_id: str
    schedule_type: str = "immediate"
    scheduled_at: datetime | None = None
    cron_expression: str | None = None
    timezone: str = "Asia/Kolkata"
    max_concurrent_calls: int = 5
    retry_limit: int = 3
    retry_cooldown_minutes: int = 30
    calling_hours_start: int = 9
    calling_hours_end: int = 21


class CampaignUpdate(BaseModel):
    name: str | None = None
    script_id: str | None = None
    list_id: str | None = None
    schedule_type: str | None = None
    scheduled_at: datetime | None = None
    cron_expression: str | None = None
    max_concurrent_calls: int | None = None
    retry_limit: int | None = None
    retry_cooldown_minutes: int | None = None
    calling_hours_start: int | None = None
    calling_hours_end: int | None = None


class CampaignResponse(BaseModel):
    id: str
    user_id: str
    script_id: str
    list_id: str
    name: str
    status: str
    schedule_type: str
    scheduled_at: datetime | None
    cron_expression: str | None
    timezone: str
    max_concurrent_calls: int
    retry_limit: int
    retry_cooldown_minutes: int
    calling_hours_start: int
    calling_hours_end: int
    total_contacts: int
    completed_contacts: int
    successful_contacts: int
    failed_contacts: int
    no_answer_contacts: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
