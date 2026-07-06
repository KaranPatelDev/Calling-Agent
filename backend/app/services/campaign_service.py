from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.campaign import Campaign
from app.models.contact_list import ContactList
from app.models.script import Script


class CampaignService:
    async def get_by_id(self, db: AsyncSession, campaign_id: str, user_id: str) -> Campaign | None:
        result = await db.execute(
            select(Campaign).where(Campaign.id == campaign_id, Campaign.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def list_campaigns(self, db: AsyncSession, user_id: str, status: str | None = None, page: int = 1, limit: int = 20) -> tuple[list[Campaign], int]:
        q = select(Campaign).where(Campaign.user_id == user_id)
        if status:
            q = q.where(Campaign.status == status)

        count_q = select(func.count()).select_from(q.subquery())
        total = (await db.execute(count_q)).scalar() or 0

        q = q.order_by(Campaign.created_at.desc()).offset((page - 1) * limit).limit(limit)
        result = await db.execute(q)
        return list(result.scalars().all()), total

    async def create(self, db: AsyncSession, user_id: str, **kwargs) -> Campaign:
        script = await db.get(Script, kwargs["script_id"])
        contact_list = await db.get(ContactList, kwargs["list_id"])
        if not script:
            raise ValueError("Script not found")
        if not contact_list:
            raise ValueError("Contact list not found")

        kwargs["total_contacts"] = contact_list.contact_count
        campaign = Campaign(user_id=user_id, **kwargs)
        db.add(campaign)
        await db.flush()
        return campaign

    async def update(self, db: AsyncSession, campaign: Campaign, **kwargs) -> Campaign:
        for key, value in kwargs.items():
            if value is not None and hasattr(campaign, key):
                setattr(campaign, key, value)
        await db.flush()
        return campaign

    async def delete(self, db: AsyncSession, campaign: Campaign) -> None:
        await db.delete(campaign)
        await db.flush()

    async def update_status(self, db: AsyncSession, campaign: Campaign, status: str) -> Campaign:
        campaign.status = status
        await db.flush()
        return campaign

    async def increment_counters(self, db: AsyncSession, campaign: Campaign, status: str) -> None:
        campaign.completed_contacts += 1
        if status == "completed":
            campaign.successful_contacts += 1
        elif status in ("failed", "busy"):
            campaign.failed_contacts += 1
        elif status == "no-answer":
            campaign.no_answer_contacts += 1
        await db.flush()


campaign_service = CampaignService()
