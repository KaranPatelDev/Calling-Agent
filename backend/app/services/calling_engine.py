import hashlib
import os
from pathlib import Path
from app.config import get_settings
from app.integrations.exotel_client import exotel_client

settings = get_settings()


class CallingEngine:
    def __init__(self):
        self.max_concurrent = 5
        self.webhook_url: str | None = None

    def set_webhook_url(self, url: str):
        self.webhook_url = url

    def interpolate(self, script_content: str, contact_data: dict) -> str:
        result = script_content
        for key, value in contact_data.items():
            if value:
                result = result.replace(f"{{{key}}}", str(value))
        return result

    def resolve_audio_url(self, script, contact=None) -> str | None:
        if script.audio_type == "uploaded" and script.audio_file_path:
            return script.audio_file_path
        return None

    async def make_call(self, phone: str, audio_url: str) -> dict:
        try:
            result = await exotel_client.make_call(
                to=phone,
                audio_url=audio_url,
                webhook_url=self.webhook_url,
            )
            return {
                "success": True,
                "call_sid": result.get("Call", {}).get("Sid"),
                "status": result.get("Call", {}).get("Status"),
            }
        except Exception as e:
            return {
                "success": False,
                "call_sid": None,
                "status": "failed",
                "error": str(e),
            }


calling_engine = CallingEngine()
