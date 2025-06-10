"""Memory management for Nova AI Assistant."""

import logging
from homeassistant.helpers.storage import Store

from .const import DEFAULT_MEMORY_SIZE, DOMAIN

_LOGGER = logging.getLogger(__name__)

class MemoryManager:
    def __init__(self, hass, max_size=DEFAULT_MEMORY_SIZE):
        self.hass = hass
        self.max_size = max_size
        self.memories = []

    async def load(self):
        """Load memories from Home Assistant storage."""
        store = Store(self.hass, 1, f"{DOMAIN}_memory")
        data = await store.async_load()
        if data and "memories" in data:
            self.memories = data["memories"]
        else:
            self.memories = []

    async def save(self):
        """Save memories to Home Assistant storage."""
        store = Store(self.hass, 1, f"{DOMAIN}_memory")
        await store.async_save({"memories": self.memories})

    def add_memory(self, memory: str):
        """Add a memory, keeping within max size."""
        self.memories.append(memory)
        if len(self.memories) > self.max_size:
            self.memories = self.memories[-self.max_size:]

    def get_memories(self):
        """Return all memories."""
        return self.memories

    def clear(self):
        """Clear all memories."""
        self.memories = []