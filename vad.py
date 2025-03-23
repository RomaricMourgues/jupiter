import pyaudio
import collections
import time
import wave
import os
from datetime import datetime
from transcribe import stt as eleven_stt
import io
import asyncio
from brain import ask
import pvcobra
import numpy as np
import queue
import threading
from wake import start_process_wake_word, get_last_wake_word_at
from config import PICOVOICE_ACCESS_KEY

# Config
channels = 1
sample_rate = 16000
frame_size = 512
frame_duration = frame_size / sample_rate * 1000  # ms
end_silence_time = 0.4  # silence duration to detect end
min_speech_time = 1.0  # seconds minimum to save

# Audio buffer and processing variables
speech_detect_buffer = queue.Queue()


# status
is_answering = False

# Placeholder STT function
async def stt(audio_file):
    global is_answering
    res = eleven_stt(audio_file)
    txt = res.text
    is_answering = True
    if txt.strip() != "":
        await ask(txt)
    is_answering = False

def stt_thread(audio_file):
    asyncio.run(stt(audio_file))

def get_is_answering():
    global is_answering
    return is_answering

vad = pvcobra.create(access_key=PICOVOICE_ACCESS_KEY)

def process_speech_detection():
    p = pyaudio.PyAudio()
    while True:
        speaking = False
        ring_buffer = collections.deque(maxlen=int(end_silence_time * 1000 / frame_duration))
        speech_frames = []
        speech_start_time = None

        if get_is_answering():
            print("Answering...")
            while get_is_answering():
                if not speech_detect_buffer.empty():
                    speech_detect_buffer.get()
                else:
                    time.sleep(0.1)
            continue

        print("👂 Listening... (reset)")

        while True:
            if not speech_detect_buffer.empty():
                audio_chunk = speech_detect_buffer.get()
                frame = np.frombuffer(audio_chunk, dtype=np.int16)
                is_speech = vad.process(frame) > 0.5 and not get_is_answering()
                ring_buffer.append(is_speech)

                buffer_size = speech_detect_buffer.qsize()
                if buffer_size > 50:
                    print(f"Speech Buffer size: {buffer_size}")
                    break

                if get_is_answering():
                    break

                speech_frames.append(frame)

                if is_speech:
                    print(".", end="", flush=True)
                    if not speaking:
                        speaking = True
                        speech_start_time = time.time()
                        speech_frames = []
                elif speaking:
                    if not any(ring_buffer):
                        #print("🛑 End of speech")
                        speech_duration = time.time() - speech_start_time
                        speaking = False

                        if speech_duration >= min_speech_time:
                            print("🛑 End of speech")

                            buffer = io.BytesIO()
                            wf = wave.open(buffer, 'wb')
                            wf.setnchannels(channels)
                            wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
                            wf.setframerate(sample_rate)
                            wf.writeframes(b''.join(speech_frames))
                            wf.close()

                            speech_frames = []
                            
                            if get_last_wake_word_at() < time.time() - 10:
                                print("X Jupiter not called first")
                                break

                            binary_audio = buffer.getvalue()

                            # Call STT but don't wait for it
                            threading.Thread(target=stt_thread, args=(io.BytesIO(binary_audio),)).start()
                            print("🎤 Speech detected")

                        break

def start_speech_detect():
    global speech_detect_buffer
    processing_thread = threading.Thread(target=process_speech_detection)
    processing_thread.daemon = True
    processing_thread.start()
    return speech_detect_buffer
