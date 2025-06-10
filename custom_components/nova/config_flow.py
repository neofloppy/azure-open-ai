"""Config flow for Nova AI Assistant integration."""

from homeassistant import config_entries
import voluptuous as vol

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
)

class NovaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Nova AI Assistant."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            # Validate input here if needed
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