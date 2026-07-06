import uuid
from datetime import datetime
from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class TTSCache(Base):
    __tablename__ = "tts_cache"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    script_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    audio_file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    audio_file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(), default=datetime.utcnow)
