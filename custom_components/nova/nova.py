"""Nova AI API communication logic."""

import asyncio
import aiohttp
import async_timeout
import logging
import json

from .const import AZURE_API_TIMEOUT

_LOGGER = logging.getLogger(__name__)

class NovaAIClient:
    """Client for communicating with Nova AI API."""
    
    def __init__(self, api_key: str, endpoint: str):
        self.api_key = api_key
        self.endpoint = endpoint.rstrip('/')

    async def ask(self, prompt: str, session: aiohttp.ClientSession, **kwargs) -> str:
        """Send a prompt to Nova AI and return the response."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": "nova-home-assistant/1.0"
        }
        
        # Support multiple API formats
        payload = {
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": kwargs.get("max_tokens", 150),
            "temperature": kwargs.get("temperature", 0.7),
            **{k: v for k, v in kwargs.items() if k not in ["max_tokens", "temperature"]}
        }
        
        try:
            async with async_timeout.timeout(AZURE_API_TIMEOUT):
                async with session.post(
                    f"{self.endpoint}/chat/completions", 
                    json=payload, 
                    headers=headers
                ) as resp:
                    if resp.status == 401:
                        _LOGGER.error("Nova AI API authentication failed. Check your API key.")
                        return "Authentication failed. Please check your API key."
                    elif resp.status == 429:
                        _LOGGER.error("Nova AI API rate limit exceeded.")
                        return "Rate limit exceeded. Please try again later."
                    elif resp.status != 200:
                        error_text = await resp.text()
                        _LOGGER.error("Nova AI API error (status %d): %s", resp.status, error_text)
                        return f"API error: {resp.status}"
                    
                    try:
                        data = await resp.json()
                    except json.JSONDecodeError as e:
                        _LOGGER.error("Failed to parse Nova AI API response: %s", e)
                        return "Failed to parse API response."
                    
                    # Handle different response formats
                    if "choices" in data and data["choices"]:
                        choice = data["choices"][0]
                        if "message" in choice:
                            return choice["message"].get("content", "")
                        elif "text" in choice:
                            return choice["text"]
                    elif "response" in data:
                        return data["response"]
                    elif "content" in data:
                        return data["content"]
                    
                    _LOGGER.warning("Unexpected Nova AI API response format: %s", data)
                    return "Received unexpected response format from API."
                    
        except asyncio.TimeoutError:
            _LOGGER.error("Nova AI API request timed out after %d seconds", AZURE_API_TIMEOUT)
            return "Request timed out. Please try again."
        except aiohttp.ClientError as e:
            _LOGGER.error("Nova AI API client error: %s", e)
            return "Connection error. Please check your network and try again."
        except Exception as e:
            _LOGGER.error("Nova AI API request failed: %s", e)
            return "An unexpected error occurred. Please try again."
