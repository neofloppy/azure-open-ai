"""Constants for Azure AI Assistant integration."""

DOMAIN = "nova"
CONF_API_KEY = "api_key"
CONF_ENDPOINT = "endpoint"
CONF_PERSONALITY = "personality"
CONF_MOOD = "mood"
CONF_MEMORY = "memory"
CONF_RANDOM_EVENTS = "random_events"

# TTS
CONF_TTS_API_KEY = "tts_api_key"
CONF_TTS_REGION = "tts_region"
CONF_TTS_VOICE = "tts_voice"

DEFAULT_PERSONALITY = "friendly"
DEFAULT_MOOD = "neutral"
DEFAULT_MEMORY_SIZE = 100  # Number of remembered events/statements
DEFAULT_RANDOM_EVENT_INTERVAL = 3600  # seconds
DEFAULT_TTS_VOICE = "en-US-JennyNeural"

AZURE_API_TIMEOUT = 30  # seconds