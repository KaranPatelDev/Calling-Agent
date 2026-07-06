from fastapi import APIRouter, Request, HTTPException
from sqlalchemy import select
from datetime import datetime
from app.database import async_session_factory
from app.models.call_log import CallLog
from app.models.campaign import Campaign

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/exotel/status")
async def exotel_status_callback(request: Request):
    body = await request.form()
    data = dict(body)

    call_sid = data.get("CallSid") or data.get("CallSid", "")
    call_status = data.get("Status", "")

    if not call_sid:
        raise HTTPException(status_code=400, detail="Missing CallSid")

    async with async_session_factory() as db:
        result = await db.execute(
            select(CallLog).where(CallLog.exotel_call_id == call_sid)
        )
        call_log = result.scalar_one_or_none()

        if call_log:
            call_log.status = call_status
            if call_status in ("completed", "failed", "no-answer", "busy"):
                call_log.ended_at = datetime.utcnow()
                if call_status == "completed" and data.get("Duration"):
                    call_log.duration_seconds = int(data["Duration"])
                if data.get("RecordingUrl"):
                    call_log.recording_url = data["RecordingUrl"]

                campaign = await db.get(Campaign, call_log.campaign_id)
                if campaign:
                    campaign.completed_contacts += 1
                    if call_status == "completed":
                        campaign.successful_contacts += 1
                    elif call_status in ("failed", "busy"):
                        campaign.failed_contacts += 1
                    elif call_status == "no-answer":
                        campaign.no_answer_contacts += 1

            await db.commit()

    return {"status": "ok"}


@router.post("/exotel/recording")
async def exotel_recording_callback(request: Request):
    body = await request.form()
    data = dict(body)
    call_sid = data.get("CallSid", "")

    if call_sid:
        async with async_session_factory() as db:
            result = await db.execute(
                select(CallLog).where(CallLog.exotel_call_id == call_sid)
            )
            call_log = result.scalar_one_or_none()
            if call_log and data.get("RecordingUrl"):
                call_log.recording_url = data["RecordingUrl"]
                await db.commit()

    return {"status": "ok"}
