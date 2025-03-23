import numpy as np
import pvporcupine
import pvcobra
import threading
import queue
import wave
import pyaudio
import time
import collections
from config import PICOVOICE_ACCESS_KEY

# Initialize Porcupine
file = False #"./test-a.wav"

if file:
    wf = wave.open(file, 'rb')
    SAMPLE_RATE = wf.getframerate()
    CHANNELS = wf.getnchannels()
else:
    SAMPLE_RATE = 16000
    CHANNELS = 1

# Audio parameters
CHUNK_SIZE = 512  # 100ms chunks at 16kHz
FAKE_PAUSES_LENGHT = 10
FAKE_PAUSES_DISTANCE = 48
FORMAT = pyaudio.paInt16
DEVICE_NAME = "hw:2,0"

# Audio buffer and processing variables
audio_buffer = queue.Queue()

# Create a map of Porcupine instances with different offsets
offsets = [0, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45]
porcupines = {offset: pvporcupine.create(access_key=PICOVOICE_ACCESS_KEY, keyword_paths=["./models/jupiter_wake_porcupine.ppn"], model_path="./models/porcupine_params_fr.pv", sensitivities=[0.95]) for offset in offsets}
vad = pvcobra.create(access_key=PICOVOICE_ACCESS_KEY)

last_wake_word_at = 0

# Add circular buffer to store last 5 seconds of audio
SECONDS_TO_KEEP = 5
BUFFERS_TO_KEEP = int(SAMPLE_RATE * SECONDS_TO_KEEP / CHUNK_SIZE)
PREVIOUS_FRAMES_TO_CHECK = 5  # Number of previous frames to check for wake word

# Silence detection parameters
SILENCE_THRESHOLD = 500  # Threshold for silence detection
SILENCE_DURATION = 0.5  # Duration of silence to mark end of speech
MIN_RECORDING_TIME = 1.0  # Minimum recording time after wake word
MAX_RECORDING_TIME = 5.0
last_speech = 0

def calculate_amplitude(audio_data):
    """Calculate the amplitude/energy of the audio data"""
    return np.sqrt(np.mean(np.square(audio_data.astype(np.float32))))

def get_last_wake_word_at():
    global last_wake_word_at
    #return last_wake_word_at # For now it's too slow for an unknown reason
    return time.time()

def has_wake_word(frame_count, audio_int16):
    global last_wake_word_at
    for offset, porcupine_instance in porcupines.items():
        # Set volume to zero when in fake pauses
        if (frame_count + offset) % FAKE_PAUSES_DISTANCE < FAKE_PAUSES_LENGHT:
            audio_int16_copy = np.zeros(len(audio_int16), dtype=np.int16)
        else:
            audio_int16_copy = audio_int16.copy()

        if audio_int16_copy.size == 512:
            keyword_index = porcupine_instance.process(audio_int16_copy)

            if keyword_index >= 0 and last_wake_word_at < time.time() - 1:
                print("Wake word detected!")
                last_wake_word_at = time.time()
                return True
        else:
            break
    return False


def process_wake_word():
    global last_wake_word_at, last_speech
    frame_count = 0
    
    # Create a ring buffer to store previous frames
    previous_frames = collections.deque(maxlen=PREVIOUS_FRAMES_TO_CHECK)
    
    while True:
        if not audio_buffer.empty():
            audio_chunk = audio_buffer.get()
            audio_int16 = np.frombuffer(audio_chunk, dtype=np.int16)
            
            # Get current size of audio_buffer
            buffer_size = audio_buffer.qsize()
            if buffer_size > 50:
                print(f"Wake buffer size: {buffer_size}")
                continue

            # Add current frame to ring buffer
            previous_frames.append(audio_int16)
            
            is_speech = vad.process(audio_int16) > 0.5

            if is_speech:
                last_speech = time.time()
                # Check previous frames for wake word when speech is detected
                for prev_frame in list(previous_frames):
                    if has_wake_word(frame_count, prev_frame):
                        break
            
            if last_wake_word_at > time.time() - 1:
                continue

            if last_speech < time.time() - 1:
                continue

            # Process audio through Porcupine instances for wake word detection
            has_wake_word(frame_count, audio_int16)

            frame_count += 1
            frame_count = frame_count % FAKE_PAUSES_DISTANCE

# Returns the audio buffer we need to add chunk to
def start_process_wake_word():
    global audio_buffer
    # Start audio processing
    processing_thread = threading.Thread(target=process_wake_word)
    processing_thread.daemon = True
    processing_thread.start()
    return audio_buffer
