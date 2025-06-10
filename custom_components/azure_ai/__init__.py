"""Azure AI Assistant Home Assistant Integration"""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    DOMAIN,
    CONF_API_KEY,
    CONF_ENDPOINT,
    CONF_PERSONALITY,
    CONF_MOOD,
)
from .azure_ai import AzureAIClient
from .personality import PersonalityManager
from .memory import MemoryManager
from .random_events import RandomEventManager
import aiohttp

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Azure AI Assistant component."""
    _LOGGER.debug("Setting up Azure AI Assistant (legacy setup)")
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Azure AI Assistant from a config entry."""
    _LOGGER.debug("Setting up Azure AI Assistant from config entry")
    hass.data.setdefault(DOMAIN, {})
    # Initialize managers
    config = entry.data
    api_key = config[CONF_API_KEY]
    endpoint = config[CONF_ENDPOINT]
    personality = config.get(CONF_PERSONALITY, "friendly")
    mood = config.get(CONF_MOOD, "neutral")

    hass.data[DOMAIN][entry.entry_id] = {}

    # Azure AI client
    client = AzureAIClient(api_key, endpoint)
    hass.data[DOMAIN][entry.entry_id]["client"] = client

    # Personality manager
    personality_mgr = PersonalityManager(personality, mood)
    hass.data[DOMAIN][entry.entry_id]["personality"] = personality_mgr

    # Memory manager
    memory_mgr = MemoryManager(hass)
    await memory_mgr.load()
    hass.data[DOMAIN][entry.entry_id]["memory"] = memory_mgr

    # Random event manager
    async def random_event_callback(event_type):
        _LOGGER.info("Random event: %s", event_type)
        # Example: change mood or ask a random question
        if event_type == "change_mood":
            new_mood = personality_mgr.randomize_mood()
            _LOGGER.info("Mood changed to %s", new_mood)
        # Extend with more event logic as needed

    random_mgr = RandomEventManager(hass, random_event_callback)
    hass.data[DOMAIN][entry.entry_id]["random"] = random_mgr
    await random_mgr.start()

    # Register services
    async def handle_ask_question(call):
        question = call.data.get("question")
        system_prompt = personality_mgr.get_system_prompt()
        memories = memory_mgr.get_memories()
        prompt = f"{system_prompt}\nMemory: {memories}\nUser: {question}"
        async with aiohttp.ClientSession() as session:
            answer = await client.ask(prompt, session)
        memory_mgr.add_memory(f"Q: {question} A: {answer}")
        await memory_mgr.save()
        hass.bus.async_fire(f"{DOMAIN}_response", {"question": question, "answer": answer})

    hass.services.async_register(DOMAIN, "ask_question", handle_ask_question)

    async def handle_set_mood(call):
        mood = call.data.get("mood")
        personality_mgr.set_mood(mood)
        _LOGGER.info("Mood set to %s", mood)

    hass.services.async_register(DOMAIN, "set_mood", handle_set_mood)

    async def handle_set_personality(call):
        personality = call.data.get("personality")
        personality_mgr.set_personality(personality)
        _LOGGER.info("Personality set to %s", personality)

    hass.services.async_register(DOMAIN, "set_personality", handle_set_personality)

    async def handle_clear_memory(call):
        memory_mgr.clear()
        await memory_mgr.save()
        _LOGGER.info("Memory cleared")

    hass.services.async_register(DOMAIN, "clear_memory", handle_clear_memory)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload Azure AI Assistant config entry."""
    _LOGGER.debug("Unloading Azure AI Assistant config entry")
    data = hass.data[DOMAIN].pop(entry.entry_id, {})
    random_mgr = data.get("random")
    if random_mgr:
        random_mgr.stop()
    return True