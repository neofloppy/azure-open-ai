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
    CONF_TTS_API_KEY,
    CONF_TTS_REGION,
    CONF_TTS_VOICE,
    DEFAULT_TTS_VOICE,
)
from .nova import AzureAIClient
from .personality import PersonalityManager
from .memory import MemoryManager
from .random_events import RandomEventManager
from .tts import AzureTTSClient
import aiohttp
import tempfile
import os

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
    tts_api_key = config.get(CONF_TTS_API_KEY)
    tts_region = config.get(CONF_TTS_REGION)
    tts_voice = config.get(CONF_TTS_VOICE, DEFAULT_TTS_VOICE)

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

    # TTS client
    tts_client = None
    if tts_api_key and tts_region:
        tts_client = AzureTTSClient(tts_api_key, tts_region, tts_voice)
    hass.data[DOMAIN][entry.entry_id]["tts"] = tts_client

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
        return None

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

    async def handle_speak(call):
        """Handle nova.speak service: synthesize and play speech."""
        text = call.data.get("text")
        media_player_entity_id = call.data.get("media_player_entity_id")
        if not tts_client:
            _LOGGER.error("TTS is not configured for Nova.")
            return
        audio_bytes = await tts_client.synthesize(text)
        if not audio_bytes:
            _LOGGER.error("Azure TTS returned no audio.")
            return
        # Save to a temp file
        tmp_dir = tempfile.gettempdir()
        file_path = os.path.join(tmp_dir, "nova_tts.mp3")
        with open(file_path, "wb") as f:
            f.write(audio_bytes)
        # Serve the file via media_player
        if media_player_entity_id:
            url = f"/local/nova_tts.mp3"
            # Copy to www directory for serving
            www_path = os.path.join(hass.config.path("www"), "nova_tts.mp3")
            os.makedirs(os.path.dirname(www_path), exist_ok=True)
            with open(www_path, "wb") as f:
                f.write(audio_bytes)
            await hass.services.async_call(
                "media_player",
                "play_media",
                {
                    "entity_id": media_player_entity_id,
                    "media_content_id": url,
                    "media_content_type": "music",
                },
                blocking=True,
            )
        else:
            _LOGGER.info("TTS audio saved to %s", file_path)

    hass.services.async_register(DOMAIN, "speak", handle_speak)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload Azure AI Assistant config entry."""
    _LOGGER.debug("Unloading Azure AI Assistant config entry")
    data = hass.data[DOMAIN].pop(entry.entry_id, {})
    random_mgr = data.get("random")
    if random_mgr:
        random_mgr.stop()
    return True