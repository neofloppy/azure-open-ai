# Nova Personal Assistant for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz/)

A powerful, customizable Home Assistant addon that brings Nova Personal Assistant to your smart home. Supports personality customization, moods, random events, and persistent memory.

## Features

- **Nova AI Integration**: Connects to your Nova Personal Assistant for advanced conversational AI.
- **Customizable Personality**: Choose from friendly, professional, humorous, or empathetic.
- **Mood System**: Moods affect responses and can change randomly or via service calls.
- **Random Events**: The assistant can trigger random behaviors (jokes, facts, mood changes, etc.).
- **Memory**: Remembers previous interactions and facts for context-aware conversations.
- **Home Assistant Services**: Interact with the assistant via Home Assistant services.
- **HACS Compatible**: Easily install and update via [HACS](https://hacs.xyz/).

## Installation

### HACS (Recommended)
1. In Home Assistant, go to HACS > Integrations > Custom repositories.
2. Add this repository URL: `https://github.com/neofloppy/nova` as a custom integration.
3. Search for "Nova Personal Assistant" in HACS and install.
4. Restart Home Assistant.

### Manual
1. Copy the `custom_components/nova` directory into your Home Assistant `custom_components` folder.
2. Restart Home Assistant.
3. Add the integration via the Home Assistant UI (Configuration > Integrations > Add Integration > Nova Personal Assistant).

## Configuration

During setup, you will be prompted for:
- **API Key**: Your Nova Personal Assistant API key.
- **API Endpoint**: The endpoint for your Nova Personal Assistant deployment.
- **Personality**: (Optional) Initial personality (`friendly`, `professional`, `humorous`, `empathetic`).
- **Mood**: (Optional) Initial mood (`neutral`, `happy`, `sad`, `excited`, `angry`, `curious`, `bored`).

You can change personality and mood later using services.

## Services

The following services are available:

### `nova.ask_question`
Ask the assistant a question. The answer is fired as an event (`nova_response`).

**Fields:**
- `question` (string): The question to ask.

**Example:**
```yaml
service: nova.ask_question
data:
  question: "What's the weather like today?"
```

### `nova.set_mood`
Set the assistant's mood.

**Fields:**
- `mood` (string): One of `neutral`, `happy`, `sad`, `excited`, `angry`, `curious`, `bored`.

### `nova.set_personality`
Set the assistant's personality.

**Fields:**
- `personality` (string): One of `friendly`, `professional`, `humorous`, `empathetic`.

### `nova.clear_memory`
Clear the assistant's memory.

## How It Works

- **Memory**: The assistant stores a configurable number of past interactions, which are included in prompts for context.
- **Moods**: Affect the tone and style of responses. Moods can change randomly or be set manually.
- **Random Events**: The assistant may trigger random events (e.g., tell a joke, share a fact, change mood) at regular intervals.

## Advanced

- All configuration is stored in Home Assistant and can be updated via the UI.
- The integration is fully async and leverages Home Assistant's storage and event systems.

## Contributing

Pull requests and feature suggestions are welcome!

---

**Author:** neofloppy
**License:** MIT
