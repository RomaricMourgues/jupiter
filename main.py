import pyaudio
import collections
import time
import wave
import os
from datetime import datetime
from transcribe import stt
import io
import asyncio
from brain import ask
import pvcobra
import numpy as np
import queue
import threading
from minitel import minitel_clear
from wake import start_process_wake_word
from vad import start_speech_detect

# Config
channels = 1
sample_rate = 16000
frame_size = 512
frame_duration = frame_size / sample_rate * 1000  # ms
end_silence_time = 0.4  # silence duration to detect end
min_speech_time = 1.0  # seconds minimum to save

print("🎙️ Ready to listen, mister...")
minitel_clear()


def get_respeaker_device_index(p):
    device_index = None
    for i in range(p.get_device_count()):
        dev_info = p.get_device_info_by_index(i)
        if "respeaker" in dev_info['name'].lower():
            device_index = i
            break
    return device_index

try:
    speech_detect_buffer = start_speech_detect()
    process_wake_buffer = start_process_wake_word()

    def speech_callback(in_data, frame_count, time_info, status):
        speech_detect_buffer.put(in_data)
        process_wake_buffer.put(in_data)
        return (None, pyaudio.paContinue)

    # Init
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=channels,
                    rate=sample_rate,
                    frames_per_buffer=frame_size,
                    input_device_index=get_respeaker_device_index(p),
                    input=True,
                    stream_callback=speech_callback)
    stream.start_stream()
    while stream.is_active():
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n🛑 Stopping, monsieur. À bientôt.")
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()
    print("🎩 À votre service.")
