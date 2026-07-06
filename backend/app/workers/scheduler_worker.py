import logging
from datetime import datetime
from sqlalchemy import select
from app.database import async_session_factory
from app.models.scheduled_job import ScheduledJob

logger = logging.getLogger(__name__)


async def start_scheduler():
    from app.services.scheduler_service import scheduler_service
    from app.workers.calling_worker import run_campaign
    from app.config import get_settings

    settings = get_settings()
    scheduler = scheduler_service.get_scheduler()

    scheduler.add_job(
        run_campaign,
        trigger='interval',
        hours=1,
        id='heartbeat_check',
        replace_existing=True,
    )

    scheduler_service.start()
    logger.info("Scheduler started")

    async with async_session_factory() as db:
        recovered = await scheduler_service.recover_missed_jobs(db)
        if recovered:
            logger.info(f"Recovered {recovered} missed jobs")
