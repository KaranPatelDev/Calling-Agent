import os
import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException
from app.config import get_settings

settings = get_settings()

ALLOWED_AUDIO_TYPES = {
    "audio/mpeg": ".mp3",
    "audio/wav": ".wav",
    "audio/x-wav": ".wav",
    "audio/ogg": ".ogg",
}


class AudioUploadService:
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR) / "audio"
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def get_user_dir(self, user_id: str) -> Path:
        user_dir = self.upload_dir / user_id
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir

    async def upload(self, file: UploadFile, user_id: str) -> tuple[str, int, str]:
        if file.content_type not in ALLOWED_AUDIO_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported audio format. Allowed: MP3, WAV, OGG"
            )

        content = await file.read()
        max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if len(content) > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE_MB}MB"
            )

        ext = ALLOWED_AUDIO_TYPES[file.content_type]
        filename = f"{uuid.uuid4().hex}{ext}"
        file_path = self.get_user_dir(user_id) / filename

        with open(file_path, "wb") as f:
            f.write(content)

        return str(file_path), len(content), file.content_type

    def delete(self, file_path: str) -> bool:
        try:
            p = Path(file_path)
            if p.exists():
                p.unlink()
                return True
            return False
        except Exception:
            return False

    def get_file_path(self, relative_path: str) -> Path:
        return Path(relative_path)


audio_upload_service = AudioUploadService()
