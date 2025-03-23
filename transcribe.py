import pyaudio
import wave
import requests
from elevenlabs import ElevenLabs
import io
from pydub import AudioSegment
import sounddevice as sd
import asyncio
import numpy as np
from config import ELEVEN_ACCESS_KEY

client = ElevenLabs(
    api_key=ELEVEN_ACCESS_KEY,
)

# Function to transcribe audio using ElevenLabs' STT API
def stt(audio_data):
    return client.speech_to_text.convert(
        file=audio_data,
        model_id="scribe_v1", # Model to use, for now only "scribe_v1" is supported
        tag_audio_events=False, # Tag audio events like laughter, applause, etc.
        language_code="fra", # Language of the audio file. If set to None, the model will detect the language automatically.
        diarize=False, # Whether to annotate who is speaking
    )

audio_buffer = bytearray()

async def tts(text):
    global audio_buffer
    print(f"Jupiter dit : {text} ...")

    audio_stream = client.generate(
        text=text,
        voice="N2lVS1w4EtoT3dr4eOWO",
        model="eleven_flash_v2_5",
        output_format="pcm_16000",
        stream=True
    )

    sample_rate = 16000
    channels = 1
    bytes_per_sample = 2  # 16-bit PCM

    def callback(outdata, frames, time, status):
        if status:
            print("⚠️ Status:", status)
        bytes_needed = frames * bytes_per_sample
        if len(audio_buffer) >= bytes_needed:
            data = audio_buffer[:bytes_needed]
            del audio_buffer[:bytes_needed]
            outdata[:] = np.frombuffer(data, dtype='int16').reshape(-1, 1)
        else:
            outdata[:] = np.zeros((frames, 1), dtype='int16')  # Fill with silence

    # 🧠 Start the stream first, keep it alive throughout
    with sd.OutputStream(
        samplerate=sample_rate,
        channels=channels,
        dtype='int16',
        callback=callback
    ):
        # Fill the buffer as the stream plays
        for chunk in audio_stream:
            audio_buffer.extend(chunk)
            await asyncio.sleep(0.001)  # Let the loop breathe
        # 💤 Wait until the buffer is empty before exiting
        while len(audio_buffer) > 0:
            await asyncio.sleep(0.5)
