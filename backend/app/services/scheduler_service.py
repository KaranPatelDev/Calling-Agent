import uuid
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import get_settings
from app.models.scheduled_job import ScheduledJob
from app.models.campaign import Campaign

settings = get_settings()


class SchedulerService:
    _scheduler = None

    def get_scheduler(self):
        if self._scheduler is None:
            from apscheduler.schedulers.asyncio import AsyncIOScheduler
            from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

            self._scheduler = AsyncIOScheduler(
                jobstores={
                    'default': SQLAlchemyJobStore(url=settings.DATABASE_URL_SYNC)
                },
                job_defaults={
                    'coalesce': True,
                    'max_instances': 1,
                    'misfire_grace_time': 3600,
                }
            )
        return self._scheduler

    def start(self):
        scheduler = self.get_scheduler()
        if not scheduler.running:
            scheduler.start()

    def shutdown(self):
        if self._scheduler and self._scheduler.running:
            self._scheduler.shutdown(wait=False)

    async def schedule_campaign(self, db: AsyncSession, campaign: Campaign, run_date: datetime) -> str:
        job_id = f"campaign_{campaign.id}_{uuid.uuid4().hex[:8]}"

        scheduler = self.get_scheduler()
        if not scheduler.running:
            self.start()

        from app.workers.calling_worker import run_campaign
        from app.config import get_settings
        _settings = get_settings()
        webhook_url = f"http://localhost:8000/api/v1/webhooks/exotel/status"

        scheduler.add_job(
            run_campaign,
            trigger='date',
            run_date=run_date,
            args=[campaign.id, webhook_url],
            id=job_id,
            replace_existing=True,
        )

        scheduled_job = ScheduledJob(
            campaign_id=campaign.id,
            apscheduler_job_id=job_id,
            job_type="campaign_start",
            status="pending",
            scheduled_at=run_date,
        )
        db.add(scheduled_job)
        await db.flush()

        return job_id

    async def cancel_job(self, db: AsyncSession, campaign_id: str):
        result = await db.execute(
            select(ScheduledJob).where(
                ScheduledJob.campaign_id == campaign_id,
                ScheduledJob.status == "pending"
            )
        )
        jobs = result.scalars().all()
        scheduler = self.get_scheduler()
        for job in jobs:
            try:
                scheduler.remove_job(job.apscheduler_job_id)
            except Exception:
                pass
            job.status = "cancelled"
        await db.flush()

    async def recover_missed_jobs(self, db: AsyncSession):
        result = await db.execute(
            select(ScheduledJob).where(
                ScheduledJob.status == "pending",
                ScheduledJob.scheduled_at < datetime.utcnow()
            )
        )
        missed = result.scalars().all()
        for job in missed:
            job.status = "missed"
        await db.flush()
        return len(missed)


scheduler_service = SchedulerService()
