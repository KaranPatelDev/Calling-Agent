import hashlib
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import get_settings
from app.models.tts_cache import TTSCache

settings = get_settings()


class TTSService:
    def __init__(self):
        self.cache_dir = Path(settings.UPLOAD_DIR) / "tts_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _hash_key(self, text: str, language: str, voice: str) -> str:
        raw = f"{text}:{language}:{voice}"
        return hashlib.sha256(raw.encode()).hexdigest()

    async def get_cached(self, db: AsyncSession, text: str, language: str, voice: str) -> str | None:
        key = self._hash_key(text, language, voice)
        result = await db.execute(select(TTSCache).where(TTSCache.script_hash == key))
        cache_entry = result.scalar_one_or_none()
        if cache_entry:
            path = Path(cache_entry.audio_file_path)
            if path.exists():
                return str(path)
        return None

    async def save_cache(self, db: AsyncSession, text: str, language: str, voice: str, audio_path: str, file_size: int) -> None:
        key = self._hash_key(text, language, voice)
        existing = await db.execute(select(TTSCache).where(TTSCache.script_hash == key))
        cache_entry = existing.scalar_one_or_none()
        if cache_entry:
            cache_entry.audio_file_path = audio_path
            cache_entry.audio_file_size = file_size
        else:
            entry = TTSCache(
                script_hash=key,
                audio_file_path=audio_path,
                audio_file_size=file_size,
            )
            db.add(entry)
        await db.flush()

    async def generate(self, text: str, language: str, voice: str) -> str | None:
        try:
            from app.integrations.google_tts_client import google_tts_client
            output_path = str(self.cache_dir / f"{self._hash_key(text, language, voice)}.mp3")
            result = await google_tts_client.synthesize(text, language, voice, output_path)
            if result:
                return output_path
        except Exception:
            pass
        return None


tts_service = TTSService()
