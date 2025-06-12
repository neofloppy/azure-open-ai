"""Config flow for Nova AI Assistant integration."""

import logging
from typing import Any, Dict, Optional

from homeassistant import config_entries
import voluptuous as vol
import aiohttp
import async_timeout

from .const import (
    DOMAIN,
    CONF_API_KEY,
    CONF_ENDPOINT,
    CONF_PERSONALITY,
    CONF_MOOD,
    CONF_TTS_API_KEY,
    CONF_TTS_REGION,
    CONF_TTS_VOICE,
    DEFAULT_PERSONALITY,
    DEFAULT_MOOD,
    DEFAULT_TTS_VOICE,
    AZURE_API_TIMEOUT,
)

_LOGGER = logging.getLogger(__name__)

class NovaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Nova AI Assistant."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            # Validate API configuration
            api_key = user_input[CONF_API_KEY]
            endpoint = user_input[CONF_ENDPOINT]
            
            if not api_key or not api_key.strip():
                errors[CONF_API_KEY] = "invalid_api_key"
            
            if not endpoint or not endpoint.strip():
                errors[CONF_ENDPOINT] = "invalid_endpoint"
            elif not (endpoint.startswith("http://") or endpoint.startswith("https://")):
                errors[CONF_ENDPOINT] = "invalid_endpoint_format"
            
            # Test API connection if basic validation passes
            if not errors:
                api_test_result = await self._test_api_connection(api_key, endpoint)
                if not api_test_result:
                    errors["base"] = "cannot_connect"
            
            # Validate TTS configuration if provided
            tts_api_key = user_input.get(CONF_TTS_API_KEY)
            tts_region = user_input.get(CONF_TTS_REGION)
            
            if tts_api_key and not tts_region:
                errors[CONF_TTS_REGION] = "tts_region_required"
            elif tts_region and not tts_api_key:
                errors[CONF_TTS_API_KEY] = "tts_api_key_required"
            
            if not errors:
                return self.async_create_entry(title="Nova AI Assistant", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_API_KEY): str,
                vol.Required(CONF_ENDPOINT): str,
                vol.Optional(CONF_PERSONALITY, default=DEFAULT_PERSONALITY): vol.In(["friendly", "professional", "humorous", "empathetic"]),
                vol.Optional(CONF_MOOD, default=DEFAULT_MOOD): vol.In(["neutral", "happy", "sad", "excited", "angry", "curious", "bored"]),
                vol.Optional(CONF_TTS_API_KEY): str,
                vol.Optional(CONF_TTS_REGION): str,
                vol.Optional(CONF_TTS_VOICE, default=DEFAULT_TTS_VOICE): str,
            }),
            errors=errors,
        )
    
    async def _test_api_connection(self, api_key: str, endpoint: str) -> bool:
        """Test the API connection."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "nova-home-assistant-config/1.0"
        }
        
        test_payload = {
            "messages": [
                {"role": "user", "content": "Hello"}
            ],
            "max_tokens": 5
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with async_timeout.timeout(AZURE_API_TIMEOUT):
                    test_endpoint = endpoint.rstrip('/') + '/chat/completions'
                    async with session.post(
                        test_endpoint, 
                        json=test_payload, 
                        headers=headers
                    ) as resp:
                        # Accept any response that indicates the API is reachable
                        # Even error responses show the API is working
                        return resp.status in [200, 400, 401, 429]
        except Exception as e:
            _LOGGER.error("API connection test failed: %s", e)
            return False
