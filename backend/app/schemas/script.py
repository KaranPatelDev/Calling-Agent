from pydantic import BaseModel
from datetime import datetime


class ScriptCreate(BaseModel):
    name: str
    content: str
    language: str = "hi-IN"
    tts_voice: str | None = None
    audio_type: str = "tts"


class ScriptUpdate(BaseModel):
    name: str | None = None
    content: str | None = None
    language: str | None = None
    tts_voice: str | None = None
    audio_type: str | None = None


class ScriptResponse(BaseModel):
    id: str
    user_id: str
    name: str
    content: str
    language: str
    tts_voice: str | None
    audio_type: str
    audio_file_path: str | None
    audio_file_size: int | None
    audio_mime_type: str | None
    is_active: bool
    version: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ScriptImportRow(BaseModel):
    name: str
    content: str
    language: str = "hi-IN"


class ScriptBulkImport(BaseModel):
    scripts: list[ScriptImportRow]
