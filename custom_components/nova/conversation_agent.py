"""Nova AI Assistant Conversation Agent for Home Assistant Assist."""

import logging
import aiohttp
from typing import Optional

from homeassistant.components.conversation import (
    AbstractConversationAgent,
    async_register_conversation_agent,
    ConversationInput,
    ConversationResult,
)
from homeassistant.core import HomeAssistant

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class NovaConversationAgent(AbstractConversationAgent):
    """Nova AI conversation agent for Home Assistant Assist."""
    
    def __init__(self, hass: HomeAssistant):
        self.hass = hass
    
    @property
    def supported_languages(self) -> list[str]:
        return ["en"]

    @property
    def attribution(self) -> dict:
        return {"name": "Nova AI Assistant", "url": "https://github.com/neofloppy/nova"}

    async def async_process(
        self, user_input: ConversationInput, context: Optional[dict] = None
    ) -> ConversationResult:
        """Process a conversation input and return a result."""
        if not user_input.text or not user_input.text.strip():
            return ConversationResult(
                response="I didn't understand that. Could you please try again?"
            )
        
        try:
            # Get the first Nova entry (assuming only one is configured)
            if DOMAIN not in self.hass.data or not self.hass.data[DOMAIN]:
                return ConversationResult(
                    response="Nova AI Assistant is not configured. Please check your configuration."
                )
            
            entry_id = next(iter(self.hass.data[DOMAIN]))
            data = self.hass.data[DOMAIN][entry_id]
            
            personality_mgr = data.get("personality")
            memory_mgr = data.get("memory")
            client = data.get("client")
            
            if not client:
                return ConversationResult(
                    response="Nova AI client is not available. Please check your configuration."
                )
            
            # Build the prompt
            system_prompt = personality_mgr.get_system_prompt() if personality_mgr else "You are a helpful assistant."
            memories = memory_mgr.get_memories() if memory_mgr else []
            memory_context = "\n".join(memories[-5:]) if memories else "No previous context."
            
            prompt = f"{system_prompt}\n\nPrevious context:\n{memory_context}\n\nUser: {user_input.text}"
            
            # Get response from Nova AI
            async with aiohttp.ClientSession() as session:
                response = await client.ask(prompt, session)
            
            if not response:
                response = "I'm sorry, I couldn't process that request right now. Please try again later."
            
            # Store in memory
            if memory_mgr:
                memory_mgr.add_memory(f"Q: {user_input.text} A: {response}")
                await memory_mgr.save()
            
            return ConversationResult(response=response)
            
        except Exception as e:
            _LOGGER.error("Error processing conversation input: %s", e)
            return ConversationResult(
                response="I encountered an error while processing your request. Please try again."
            )

async def async_setup(hass: HomeAssistant, config: Optional[dict] = None) -> bool:
    """Set up the Nova conversation agent."""
    agent = NovaConversationAgent(hass)
    async_register_conversation_agent(hass, DOMAIN, agent)
    _LOGGER.info("Nova conversation agent registered successfully")
    return True
