import uuid
from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    script_id: Mapped[str] = mapped_column(String(36), ForeignKey("scripts.id"), nullable=False)
    list_id: Mapped[str] = mapped_column(String(36), ForeignKey("contact_lists.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="draft", index=True)
    schedule_type: Mapped[str] = mapped_column(String(20), default="immediate")
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(), nullable=True, index=True)
    cron_expression: Mapped[str | None] = mapped_column(String(100), nullable=True)
    timezone: Mapped[str] = mapped_column(String(50), default="Asia/Kolkata")
    max_concurrent_calls: Mapped[int] = mapped_column(Integer, default=5)
    retry_limit: Mapped[int] = mapped_column(Integer, default=3)
    retry_cooldown_minutes: Mapped[int] = mapped_column(Integer, default=30)
    calling_hours_start: Mapped[int] = mapped_column(Integer, default=9)
    calling_hours_end: Mapped[int] = mapped_column(Integer, default=21)
    total_contacts: Mapped[int] = mapped_column(Integer, default=0)
    completed_contacts: Mapped[int] = mapped_column(Integer, default=0)
    successful_contacts: Mapped[int] = mapped_column(Integer, default=0)
    failed_contacts: Mapped[int] = mapped_column(Integer, default=0)
    no_answer_contacts: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)
