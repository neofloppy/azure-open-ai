"""Nova AI Assistant Conversation Agent for Home Assistant Assist."""

from homeassistant.components.conversation import (
    AbstractConversationAgent,
    async_register_conversation_agent,
    ConversationInput,
    ConversationResult,
)
from homeassistant.core import HomeAssistant
from typing import Optional

class NovaAgent(AbstractConversationAgent):
    @property
    def supported_languages(self) -> list[str]:
        return ["en"]

    @property
    def attribution(self) -> dict:
        return {"name": "Nova AI Assistant"}

    async def async_process(
        self, user_input: ConversationInput, context: Optional[dict] = None
    ) -> ConversationResult:
        prompt = user_input.text
        response = f"Nova whispers back: '{prompt}'"
        return ConversationResult(response=response)

async def async_setup(hass: HomeAssistant, config: Optional[dict] = None) -> bool:
    agent = NovaAgent()
    async_register_conversation_agent(hass, "nova", agent)
    return True