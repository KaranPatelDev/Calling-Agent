from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.schemas.campaign import CampaignCreate, CampaignUpdate, CampaignResponse
from app.schemas.call_log import CallLogResponse
from app.schemas.common import PaginatedResponse, MessageResponse
from app.services.campaign_service import campaign_service
from sqlalchemy import select, func
from app.models.call_log import CallLog

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.get("", response_model=PaginatedResponse)
async def list_campaigns(
    status_filter: str | None = None,
    page: int = 1,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items, total = await campaign_service.list_campaigns(db, current_user.id, status_filter, page, limit)
    return PaginatedResponse(
        items=[CampaignResponse.model_validate(i) for i in items],
        total=total,
        page=page,
        pages=(total + limit - 1) // limit,
    )


@router.post("", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    body: CampaignCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        campaign = await campaign_service.create(db, current_user.id, **body.model_dump())
        return campaign
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    campaign = await campaign_service.get_by_id(db, campaign_id, current_user.id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: str,
    body: CampaignUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    campaign = await campaign_service.get_by_id(db, campaign_id, current_user.id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if campaign.status not in ("draft", "scheduled"):
        raise HTTPException(status_code=400, detail="Cannot modify running/completed campaign")
    updated = await campaign_service.update(db, campaign, **body.model_dump(exclude_unset=True))
    return updated


@router.delete("/{campaign_id}", response_model=MessageResponse)
async def delete_campaign(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    campaign = await campaign_service.get_by_id(db, campaign_id, current_user.id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if campaign.status == "running":
        raise HTTPException(status_code=400, detail="Cannot delete running campaign")
    await campaign_service.delete(db, campaign)
    return MessageResponse(message="Campaign deleted")


@router.post("/{campaign_id}/start", response_model=MessageResponse)
async def start_campaign(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    campaign = await campaign_service.get_by_id(db, campaign_id, current_user.id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if campaign.status not in ("draft", "paused"):
        raise HTTPException(status_code=400, detail="Campaign cannot be started")
    if campaign.total_contacts == 0:
        raise HTTPException(status_code=400, detail="Campaign has no contacts")

    await campaign_service.update_status(db, campaign, "running")
    return MessageResponse(message="Campaign started")


@router.post("/{campaign_id}/pause", response_model=MessageResponse)
async def pause_campaign(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    campaign = await campaign_service.get_by_id(db, campaign_id, current_user.id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if campaign.status != "running":
        raise HTTPException(status_code=400, detail="Campaign is not running")
    await campaign_service.update_status(db, campaign, "paused")
    return MessageResponse(message="Campaign paused")


@router.post("/{campaign_id}/resume", response_model=MessageResponse)
async def resume_campaign(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    campaign = await campaign_service.get_by_id(db, campaign_id, current_user.id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if campaign.status != "paused":
        raise HTTPException(status_code=400, detail="Campaign is not paused")
    await campaign_service.update_status(db, campaign, "running")
    return MessageResponse(message="Campaign resumed")


@router.get("/{campaign_id}/call-logs", response_model=PaginatedResponse)
async def get_call_logs(
    campaign_id: str,
    status_filter: str | None = None,
    page: int = 1,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    campaign = await campaign_service.get_by_id(db, campaign_id, current_user.id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    q = select(CallLog).where(CallLog.campaign_id == campaign_id)
    if status_filter:
        q = q.where(CallLog.status == status_filter)

    count_q = select(func.count()).select_from(q.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    q = q.order_by(CallLog.created_at.desc()).offset((page - 1) * limit).limit(limit)
    result = await db.execute(q)
    items = list(result.scalars().all())

    return PaginatedResponse(
        items=[CallLogResponse.model_validate(i) for i in items],
        total=total,
        page=page,
        pages=(total + limit - 1) // limit,
    )
