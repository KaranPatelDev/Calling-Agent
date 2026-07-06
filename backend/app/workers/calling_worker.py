import asyncio
import logging
from sqlalchemy import select
from app.database import async_session_factory
from app.models.campaign import Campaign
from app.models.contact import Contact
from app.models.script import Script
from app.models.call_log import CallLog
from app.services.calling_engine import calling_engine
from app.utils.timezone_utils import is_within_calling_hours
from app.integrations.exotel_client import exotel_client
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


async def run_campaign(campaign_id: str, webhook_url: str):
    calling_engine.set_webhook_url(webhook_url)

    async with async_session_factory() as db:
        campaign = await db.get(Campaign, campaign_id)
        if not campaign:
            logger.error(f"Campaign {campaign_id} not found")
            return

        if not is_within_calling_hours(campaign.calling_hours_start, campaign.calling_hours_end):
            logger.warning(f"Outside calling hours for campaign {campaign_id}")
            campaign.status = "paused"
            await db.commit()
            return

        script = await db.get(Script, campaign.script_id)
        if not script:
            logger.error(f"Script {campaign.script_id} not found for campaign {campaign_id}")
            return

        result = await db.execute(
            select(Contact).where(Contact.list_id == campaign.list_id, Contact.dnd_registered == False)
        )
        contacts = list(result.scalars().all())

        logger.info(f"Starting campaign {campaign_id} with {len(contacts)} contacts")

        for contact in contacts:
            if not is_within_calling_hours(campaign.calling_hours_start, campaign.calling_hours_end):
                logger.info("Outside calling hours, pausing campaign")
                campaign.status = "paused"
                await db.commit()
                return

            audio_url = calling_engine.resolve_audio_url(script, contact)
            if not audio_url:
                logger.warning(f"No audio for contact {contact.id}, skipping")
                continue

            call_log = CallLog(
                campaign_id=campaign_id,
                contact_id=contact.id,
                status="dialing",
            )
            db.add(call_log)
            await db.flush()

            call_result = await exotel_client.make_call(
                to=contact.phone,
                audio_url=audio_url,
                webhook_url=webhook_url,
            )

            call_log.exotel_call_id = call_result.get("call_sid")
            call_log.status = call_result.get("status", "failed")
            if not call_result.get("success"):
                call_log.error_message = call_result.get("error")

            contact.last_called_at = call_log.created_at

            campaign.completed_contacts += 1
            if call_result.get("status") == "completed":
                campaign.successful_contacts += 1
            elif call_result.get("status") in ("failed", "busy"):
                campaign.failed_contacts += 1
            elif call_result.get("status") == "no-answer":
                campaign.no_answer_contacts += 1

            await db.commit()

            await asyncio.sleep(1)

        campaign.status = "completed"
        await db.commit()
        logger.info(f"Campaign {campaign_id} completed")
