"""Random events logic for Azure AI Assistant."""

import asyncio
import random
import logging

from homeassistant.helpers.event import async_call_later
from .const import DEFAULT_RANDOM_EVENT_INTERVAL

_LOGGER = logging.getLogger(__name__)

RANDOM_EVENTS = [
    "tell_joke",
    "share_fact",
    "ask_question",
    "change_mood",
]

class RandomEventManager:
    def __init__(self, hass, callback, interval=DEFAULT_RANDOM_EVENT_INTERVAL):
        self.hass = hass
        self.callback = callback  # Function to call on event
        self.interval = interval
        self._unsub = None

    async def start(self):
        """Start scheduling random events."""
        await self._schedule_next()

    async def _schedule_next(self):
        self._unsub = async_call_later(
            self.hass, self.interval, self._fire_event
        )

    async def _fire_event(self, _now):
        event_type = random.choice(RANDOM_EVENTS)
        _LOGGER.debug("Firing random event: %s", event_type)
        await self.callback(event_type)
        await self._schedule_next()

    def stop(self):
        """Stop scheduling random events."""
        if self._unsub:
            self._unsub()
            self._unsub = None