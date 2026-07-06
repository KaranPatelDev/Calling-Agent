from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
import csv
import io

from app.database import get_db
from app.models.user import User
from app.models.campaign import Campaign
from app.models.call_log import CallLog
from app.api.deps import get_current_user
from app.schemas.call_log import CallLogResponse, CampaignStats
from app.schemas.common import PaginatedResponse

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/dashboard")
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    total_campaigns = (await db.execute(
        select(func.count()).select_from(Campaign).where(Campaign.user_id == current_user.id)
    )).scalar() or 0

    active_campaigns = (await db.execute(
        select(func.count()).select_from(Campaign).where(
            Campaign.user_id == current_user.id, Campaign.status == "running"
        )
    )).scalar() or 0

    campaign_ids_q = select(Campaign.id).where(Campaign.user_id == current_user.id)
    total_calls = (await db.execute(
        select(func.count()).select_from(CallLog).where(CallLog.campaign_id.in_(campaign_ids_q))
    )).scalar() or 0

    successful_calls = (await db.execute(
        select(func.count()).select_from(CallLog).where(
            CallLog.campaign_id.in_(campaign_ids_q), CallLog.status == "completed"
        )
    )).scalar() or 0

    failed_calls = (await db.execute(
        select(func.count()).select_from(CallLog).where(
            CallLog.campaign_id.in_(campaign_ids_q),
            CallLog.status.in_(["failed", "busy", "no-answer"])
        )
    )).scalar() or 0

    success_rate = (successful_calls / total_calls * 100) if total_calls > 0 else 0.0

    return {
        "total_campaigns": total_campaigns,
        "active_campaigns": active_campaigns,
        "total_calls": total_calls,
        "successful_calls": successful_calls,
        "failed_calls": failed_calls,
        "success_rate": round(success_rate, 2),
    }


@router.get("/campaigns/{campaign_id}/stats", response_model=CampaignStats)
async def get_campaign_stats(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    campaign = await db.get(Campaign, campaign_id)
    if not campaign or campaign.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Campaign not found")

    in_progress = (await db.execute(
        select(func.count()).select_from(CallLog).where(
            CallLog.campaign_id == campaign_id,
            CallLog.status.in_(["dialing", "ringing", "in-progress"])
        )
    )).scalar() or 0

    queued = (await db.execute(
        select(func.count()).select_from(CallLog).where(
            CallLog.campaign_id == campaign_id, CallLog.status == "queued"
        )
    )).scalar() or 0

    avg_duration = (await db.execute(
        select(func.avg(CallLog.duration_seconds)).where(
            CallLog.campaign_id == campaign_id, CallLog.status == "completed"
        )
    )).scalar() or 0.0

    total = campaign.total_contacts or 1
    success_rate = (campaign.successful_contacts / total * 100) if total > 0 else 0.0

    return CampaignStats(
        total_contacts=campaign.total_contacts,
        completed_contacts=campaign.completed_contacts,
        successful_contacts=campaign.successful_contacts,
        failed_contacts=campaign.failed_contacts,
        no_answer_contacts=campaign.no_answer_contacts,
        in_progress_contacts=in_progress,
        queued_contacts=queued,
        success_rate=round(success_rate, 2),
        avg_duration_seconds=round(float(avg_duration), 2),
    )


@router.get("/campaigns/{campaign_id}/export")
async def export_call_logs(
    campaign_id: str,
    format: str = "csv",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    campaign = await db.get(Campaign, campaign_id)
    if not campaign or campaign.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Campaign not found")

    result = await db.execute(
        select(CallLog).where(CallLog.campaign_id == campaign_id).order_by(CallLog.created_at.desc())
    )
    logs = list(result.scalars().all())

    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "ID", "Contact ID", "Exotel Call ID", "Status", "Duration (s)",
            "Started At", "Ended At", "Retry Count", "Error", "Recording URL", "Created At"
        ])
        for log in logs:
            writer.writerow([
                log.id, log.contact_id, log.exotel_call_id, log.status,
                log.duration_seconds, log.started_at, log.ended_at,
                log.retry_count, log.error_message, log.recording_url, log.created_at,
            ])
        output.seek(0)
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode("utf-8")),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=call_logs_{campaign_id}.csv"},
        )

    raise HTTPException(status_code=400, detail="Unsupported format. Use 'csv'.")
