"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-07-06
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("phone", sa.String(15), nullable=True),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column("is_verified", sa.Boolean(), default=False),
        sa.Column("exotel_account_sid", sa.String(100), nullable=True),
        sa.Column("exotel_api_key", sa.String(100), nullable=True),
        sa.Column("exotel_api_token", sa.String(100), nullable=True),
        sa.Column("exotel_caller_id", sa.String(20), nullable=True),
        sa.Column("timezone", sa.String(50), default="Asia/Kolkata"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "scripts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("language", sa.String(10), default="hi-IN"),
        sa.Column("tts_voice", sa.String(100), nullable=True),
        sa.Column("audio_type", sa.String(10), default="tts"),
        sa.Column("audio_file_path", sa.String(500), nullable=True),
        sa.Column("audio_file_size", sa.Integer(), nullable=True),
        sa.Column("audio_mime_type", sa.String(50), nullable=True),
        sa.Column("is_active", sa.Boolean(), default=False),
        sa.Column("version", sa.Integer(), default=1),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "contact_lists",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("contact_count", sa.Integer(), default=0),
        sa.Column("source", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "contacts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("list_id", sa.String(36), sa.ForeignKey("contact_lists.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("phone", sa.String(15), nullable=False, index=True),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("company", sa.String(255), nullable=True),
        sa.Column("metadata", postgresql.JSONB(), nullable=True),
        sa.Column("dnd_registered", sa.Boolean(), default=False),
        sa.Column("last_called_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "campaigns",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("script_id", sa.String(36), sa.ForeignKey("scripts.id"), nullable=False),
        sa.Column("list_id", sa.String(36), sa.ForeignKey("contact_lists.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("status", sa.String(20), default="draft", index=True),
        sa.Column("schedule_type", sa.String(20), default="immediate"),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cron_expression", sa.String(100), nullable=True),
        sa.Column("timezone", sa.String(50), default="Asia/Kolkata"),
        sa.Column("max_concurrent_calls", sa.Integer(), default=5),
        sa.Column("retry_limit", sa.Integer(), default=3),
        sa.Column("retry_cooldown_minutes", sa.Integer(), default=30),
        sa.Column("calling_hours_start", sa.Integer(), default=9),
        sa.Column("calling_hours_end", sa.Integer(), default=21),
        sa.Column("total_contacts", sa.Integer(), default=0),
        sa.Column("completed_contacts", sa.Integer(), default=0),
        sa.Column("successful_contacts", sa.Integer(), default=0),
        sa.Column("failed_contacts", sa.Integer(), default=0),
        sa.Column("no_answer_contacts", sa.Integer(), default=0),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "call_logs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("campaign_id", sa.String(36), sa.ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("contact_id", sa.String(36), sa.ForeignKey("contacts.id"), nullable=False, index=True),
        sa.Column("exotel_call_id", sa.String(100), nullable=True, index=True),
        sa.Column("status", sa.String(20), nullable=False, index=True),
        sa.Column("duration_seconds", sa.Integer(), default=0),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("retry_count", sa.Integer(), default=0),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("audio_file_url", sa.String(500), nullable=True),
        sa.Column("recording_url", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "scheduled_jobs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("campaign_id", sa.String(36), sa.ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("apscheduler_job_id", sa.String(100), nullable=False),
        sa.Column("job_type", sa.String(50), nullable=False),
        sa.Column("status", sa.String(20), default="pending", index=True),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_heartbeat", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("retry_count", sa.Integer(), default=0),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "tts_cache",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("script_hash", sa.String(64), unique=True, nullable=False, index=True),
        sa.Column("audio_file_path", sa.String(500), nullable=False),
        sa.Column("audio_file_size", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("tts_cache")
    op.drop_table("scheduled_jobs")
    op.drop_table("call_logs")
    op.drop_table("campaigns")
    op.drop_table("contacts")
    op.drop_table("contact_lists")
    op.drop_table("scripts")
    op.drop_table("users")
