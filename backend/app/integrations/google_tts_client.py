import os
from pathlib import Path
from app.config import get_settings

settings = get_settings()


class GoogleTTSClient:
    def __init__(self):
        self.credentials_path = settings.GOOGLE_APPLICATION_CREDENTIALS
        self.language_code = settings.TTS_LANGUAGE_CODE
        self.voice_name = settings.TTS_VOICE_NAME

    async def synthesize(self, text: str, language: str, voice: str, output_path: str) -> bool:
        try:
            from google.cloud import texttospeech

            if self.credentials_path:
                client = texttospeech.TextToSpeechClient.from_service_account_file(self.credentials_path)
            else:
                client = texttospeech.TextToSpeechClient()

            synthesis_input = texttospeech.SynthesisInput(text=text)

            voice_params = texttospeech.VoiceSelectionParams(
                language_code=language or self.language_code,
                name=voice or self.voice_name,
            )

            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                sample_rate_hertz=8000,
            )

            response = client.synthesize_speech(
                input=synthesis_input, voice=voice_params, audio_config=audio_config
            )

            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as out:
                out.write(response.audio_content)

            return True
        except Exception as e:
            print(f"TTS generation failed: {e}")
            return False


google_tts_client = GoogleTTSClient()
