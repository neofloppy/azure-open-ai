"""Personality and mood logic for Nova Personal Assistant."""

import random

from .const import DEFAULT_PERSONALITY, DEFAULT_MOOD

PERSONALITIES = {
    "friendly": "You are a friendly and helpful assistant.",
    "professional": "You are a professional and concise assistant.",
    "humorous": "You are a witty and humorous assistant.",
    "empathetic": "You are an empathetic and caring assistant.",
}

MOODS = [
    "neutral",
    "happy",
    "sad",
    "excited",
    "angry",
    "curious",
    "bored",
]

class PersonalityManager:
    def __init__(self, personality=DEFAULT_PERSONALITY, mood=DEFAULT_MOOD):
        self.personality = personality
        self.mood = mood

    def set_personality(self, personality):
        if personality in PERSONALITIES:
            self.personality = personality

    def set_mood(self, mood):
        if mood in MOODS:
            self.mood = mood

    def get_system_prompt(self):
        """Generate a system prompt based on current personality and mood."""
        base = PERSONALITIES.get(self.personality, PERSONALITIES[DEFAULT_PERSONALITY])
        mood_text = f"Current mood: {self.mood}."
        return f"{base} {mood_text}"

    def randomize_mood(self):
        self.mood = random.choice(MOODS)
        return self.mood