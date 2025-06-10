"""Azure Text-to-Speech (TTS) support for Nova."""

import aiohttp
import logging

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class AzureTTSClient:
    def __init__(self, api_key: str, region: str, voice: str = "en-US-JennyNeural"):
        self.api_key = api_key
        self.region = region
        self.voice = voice
        self.endpoint = f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1"

    async def synthesize(self, text: str) -> bytes:
        """Synthesize speech from text using Azure TTS."""
        headers = {
            "Ocp-Apim-Subscription-Key": self.api_key,
            "Content-Type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": "audio-16khz-32kbitrate-mono-mp3",
            "User-Agent": "nova-home-assistant"
        }
        ssml = f"""
        <speak version='1.0' xml:lang='en-US'>
            <voice xml:lang='en-US' xml:gender='Female' name='{self.voice}'>
                {text}
            </voice>
        </speak>
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(self.endpoint, data=ssml, headers=headers) as resp:
                if resp.status != 200:
                    _LOGGER.error("Azure TTS error: %s", await resp.text())
                    return b""
                return await resp.read()