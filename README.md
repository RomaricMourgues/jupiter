# Jupiter Voice Assistant

Jupiter is a voice assistant that runs on a Raspberry Pi and interfaces with a vintage Minitel terminal. It uses wake word detection, speech recognition, and text-to-speech capabilities to create an interactive experience. **Response time is about 500ms!**. I'll publish a video soon.

## Minitel ?

I own a 1200 baud Minitel, more informations in [MINITEL.md](MINITEL.md). Also https://en.wikipedia.org/wiki/Minitel .

## Features

- 🗣️ Wake word detection ("Jupiter") using Picovoice Porcupine
- 🎙️ Voice activity detection using Picovoice Cobra
- 💬 Speech-to-text via ElevenLabs API
- 🧠 AI-powered responses using Mistral AI
- 🔊 Text-to-speech via ElevenLabs API
- 📺 Display on vintage Minitel terminal via serial connection

## Requirements

- Raspberry Pi (or similar Linux device)
- ReSpeaker microphone array (or another compatible microphone)
- Minitel terminal connected via USB-to-serial adapter
- Python 3.7+
- Internet connection for API access

## Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Copy `config.dist.py` to `config.py` and add your API keys:
   ```
   cp config.dist.py config.py
   nano config.py
   ```

## Configuration

You'll need to obtain API keys for:
- Picovoice (for wake word detection and VAD)
- ElevenLabs (for speech recognition and synthesis)
- Mistral AI (for natural language processing)

## Usage

1. Connect your Minitel to the serial port (default: `/dev/ttyUSB0`)
2. Connect your microphone
3. Run the main script:
   ```
   python main.py
   ```
4. Say "Jupiter" to wake the assistant, then speak your query

## Project Structure

- `main.py`: Entry point that initializes audio capture and processing
- `wake.py`: Wake word detection system
- `vad.py`: Voice activity detection for capturing speech
- `brain.py`: AI processing using Mistral AI
- `transcribe.py`: Speech-to-text and text-to-speech using ElevenLabs
- `minitel.py`: Interface with the Minitel terminal

## License

MIT
