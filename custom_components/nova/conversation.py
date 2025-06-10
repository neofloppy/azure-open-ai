"""Nova AI Assistant Conversation Platform."""

import logging
from homeassistant.components.conversation import (
    AbstractConversationAgent,
    ConversationInput,
    ConversationResult,
    AgentResponseType,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.typing import ConfigType, HomeAssistantType

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_get_agent(hass: HomeAssistantType, config: ConfigType):
    return NovaConversationAgent(hass)

class NovaConversationAgent(AbstractConversationAgent):
    type = DOMAIN
    name = "Nova AI Assistant"

    def __init__(self, hass: HomeAssistant):
        self.hass = hass

    @property
    def supported_languages(self):
        return ["en"]

    @property
    def supported_response_types(self):
        return [AgentResponseType.FREE_TEXT]

    async def async_process(self, user_input: ConversationInput) -> ConversationResult:
        # Use Nova's ask service logic
        question = user_input.text
        # Use the same logic as the ask_question service
        entry_id = next(iter(self.hass.data[DOMAIN]))
        data = self.hass.data[DOMAIN][entry_id]
        personality_mgr = data["personality"]
        memory_mgr = data["memory"]
        client = data["client"]

        system_prompt = personality_mgr.get_system_prompt()
        memories = memory_mgr.get_memories()
        prompt = f"{system_prompt}\nMemory: {memories}\nUser: {question}"

        import aiohttp
        async with aiohttp.ClientSession() as session:
            answer = await client.ask(prompt, session)
        memory_mgr.add_memory(f"Q: {question} A: {answer}")
        await memory_mgr.save()

        return ConversationResult(
            response=answer,
            response_type=AgentResponseType.FREE_TEXT,
        )