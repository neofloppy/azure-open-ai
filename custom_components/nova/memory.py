"""Memory management for Nova AI Assistant."""

import logging
from datetime import datetime
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
        """Add a memory with timestamp, keeping within max size."""
        timestamp = datetime.now().isoformat()
        memory_entry = {
            "content": memory,
            "timestamp": timestamp
        }
        self.memories.append(memory_entry)
        if len(self.memories) > self.max_size:
            self.memories = self.memories[-self.max_size:]
        _LOGGER.debug("Added memory: %s", memory[:50])

    def get_memories(self, recent_count=None):
        """Return memories as formatted strings."""
        if recent_count:
            memories_to_return = self.memories[-recent_count:]
        else:
            memories_to_return = self.memories
        
        # Convert to string format for backwards compatibility
        if memories_to_return and isinstance(memories_to_return[0], dict):
            return [mem["content"] for mem in memories_to_return]
        return memories_to_return
    
    def get_memory_count(self):
        """Return the number of stored memories."""
        return len(self.memories)

    def clear(self):
        """Clear all memories."""
        self.memories = []