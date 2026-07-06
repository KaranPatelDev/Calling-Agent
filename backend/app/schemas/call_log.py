from pydantic import BaseModel
from datetime import datetime


class CallLogResponse(BaseModel):
    id: str
    campaign_id: str
    contact_id: str
    exotel_call_id: str | None
    status: str
    duration_seconds: int
    started_at: datetime | None
    ended_at: datetime | None
    retry_count: int
    error_message: str | None
    audio_file_url: str | None
    recording_url: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class CampaignStats(BaseModel):
    total_contacts: int
    completed_contacts: int
    successful_contacts: int
    failed_contacts: int
    no_answer_contacts: int
    in_progress_contacts: int
    queued_contacts: int
    success_rate: float
    avg_duration_seconds: float


class ExportRequest(BaseModel):
    campaign_id: str
    format: str = "csv"
    status_filter: str | None = None
