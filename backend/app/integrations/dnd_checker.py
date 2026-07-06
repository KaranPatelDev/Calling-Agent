import httpx
from app.config import get_settings

settings = get_settings()


class DNDChecker:
    async def check_number(self, phone: str) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://www.dndcheck.in/api/check/{phone}",
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("dnd_registered", False)
        except Exception:
            pass
        return False

    async def scrub_contacts(self, contacts: list) -> list:
        eligible = []
        for contact in contacts:
            if not contact.dnd_registered:
                eligible.append(contact)
        return eligible


dnd_checker = DNDChecker()
