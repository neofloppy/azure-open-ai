"""Azure Text-to-Speech (TTS) support for Nova."""

import aiohttp
import async_timeout
import logging
import xml.sax.saxutils as xml_escape

from .const import AZURE_API_TIMEOUT

_LOGGER = logging.getLogger(__name__)

class AzureTTSClient:
    def __init__(self, api_key: str, region: str, voice: str = "en-US-JennyNeural"):
        self.api_key = api_key
        self.region = region
        self.voice = voice
        self.endpoint = f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1"

    async def synthesize(self, text: str) -> bytes:
        """Synthesize speech from text using Azure TTS."""
        if not text or not text.strip():
            _LOGGER.warning("Empty text provided for TTS synthesis")
            return b""
            
        # Escape XML entities in the text
        escaped_text = xml_escape.escape(text.strip())
        
        headers = {
            "Ocp-Apim-Subscription-Key": self.api_key,
            "Content-Type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": "audio-16khz-32kbitrate-mono-mp3",
            "User-Agent": "nova-home-assistant/1.0"
        }
        
        ssml = f"""<?xml version="1.0" encoding="utf-8"?>
<speak version="1.0" xml:lang="en-US" xmlns="http://www.w3.org/2001/10/synthesis">
    <voice xml:lang="en-US" name="{self.voice}">
        {escaped_text}
    </voice>
</speak>"""
        
        try:
            async with aiohttp.ClientSession() as session:
                async with async_timeout.timeout(AZURE_API_TIMEOUT):
                    async with session.post(
                        self.endpoint, 
                        data=ssml, 
                        headers=headers
                    ) as resp:
                        if resp.status == 401:
                            _LOGGER.error("Azure TTS authentication failed. Check your API key.")
                            return b""
                        elif resp.status == 429:
                            _LOGGER.error("Azure TTS rate limit exceeded.")
                            return b""
                        elif resp.status != 200:
                            error_text = await resp.text()
                            _LOGGER.error("Azure TTS error (status %d): %s", resp.status, error_text)
                            return b""
                        
                        audio_data = await resp.read()
                        if len(audio_data) == 0:
                            _LOGGER.warning("Azure TTS returned empty audio data")
                        return audio_data
                        
        except aiohttp.ClientError as e:
            _LOGGER.error("Azure TTS client error: %s", e)
            return b""
        except Exception as e:
            _LOGGER.error("Azure TTS synthesis failed: %s", e)
            return b""
