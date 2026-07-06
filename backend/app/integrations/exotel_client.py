import httpx
from app.config import get_settings

settings = get_settings()


class ExotelClient:
    def __init__(self):
        self.base_url = settings.EXOTEL_BASE_URL
        self.account_sid = settings.EXOTEL_ACCOUNT_SID
        self.api_key = settings.EXOTEL_API_KEY
        self.api_token = settings.EXOTEL_API_TOKEN
        self.caller_id = settings.EXOTEL_CALLER_ID
        self.auth = (self.api_key, self.api_token)

    def _url(self, path: str) -> str:
        return f"{self.base_url}/Accounts/{self.account_sid}{path}"

    async def make_call(
        self,
        to: str,
        audio_url: str,
        from_number: str | None = None,
        webhook_url: str | None = None,
        record: bool = True,
    ) -> dict:
        async with httpx.AsyncClient() as client:
            data = {
                "From": from_number or self.caller_id,
                "To": to,
                "CallerId": self.caller_id,
                "CallType": "trans",
                "StartPlaybackToNew": "Callee",
                "StartPlaybackValueNew": audio_url,
            }
            if webhook_url:
                data["StatusCallback"] = webhook_url
                data["StatusCallbackEvents"] = "terminal"
                data["StatusCallbackContentType"] = "application/json"
            if record:
                data["Record"] = "true"

            response = await client.post(
                self._url("/Calls/connect"),
                auth=self.auth,
                data=data,
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()

    async def get_call_details(self, call_sid: str) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self._url(f"/Calls/{call_sid}"),
                auth=self.auth,
                timeout=15.0,
            )
            response.raise_for_status()
            return response.json()


exotel_client = ExotelClient()
