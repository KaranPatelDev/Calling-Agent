from datetime import datetime
from app.utils.timezone_utils import is_within_calling_hours, IST


class ComplianceService:
    def check_calling_hours(self, calling_hours_start: int, calling_hours_end: int) -> bool:
        return is_within_calling_hours(calling_hours_start, calling_hours_end)

    def check_dnd(self, contact) -> bool:
        return contact.dnd_registered

    def filter_eligible_contacts(self, contacts: list, calling_hours_start: int = 9, calling_hours_end: int = 21) -> list:
        eligible = []
        now = datetime.now(IST)
        within_hours = calling_hours_start <= now.hour < calling_hours_end

        for contact in contacts:
            if contact.dnd_registered:
                continue
            if not within_hours:
                continue
            eligible.append(contact)
        return eligible

    def is_valid_calling_window(self, campaign) -> tuple[bool, str]:
        now = datetime.now(IST)
        if not (campaign.calling_hours_start <= now.hour < campaign.calling_hours_end):
            return False, f"Outside calling hours ({campaign.calling_hours_start}:00 - {campaign.calling_hours_end}:00 IST)"
        return True, "OK"


compliance_service = ComplianceService()
