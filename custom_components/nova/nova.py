"""Azure AI API communication logic."""

import aiohttp
import async_timeout
import logging

from .const import CONF_API_KEY, CONF_ENDPOINT, AZURE_API_TIMEOUT

_LOGGER = logging.getLogger(__name__)

class AzureAIClient:
    def __init__(self, api_key: str, endpoint: str):
        self.api_key = api_key
        self.endpoint = endpoint

    async def ask(self, prompt: str, session: aiohttp.ClientSession, **kwargs) -> str:
        """Send a prompt to Azure AI and return the response."""
        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key,
        }
        payload = {
            "prompt": prompt,
            **kwargs
        }
        try:
            with async_timeout.timeout(AZURE_API_TIMEOUT):
                async with session.post(self.endpoint, json=payload, headers=headers) as resp:
                    if resp.status != 200:
                        _LOGGER.error("Azure AI API error: %s", await resp.text())
                        return ""
                    data = await resp.json()
                    return data.get("choices", [{}])[0].get("text", "")
        except Exception as e:
            _LOGGER.error("Azure AI API request failed: %s", e)
            return ""