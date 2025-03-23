import numpy as np
import pvporcupine
import threading
import queue
import wave
import pyaudio
import time
import serial
import collections

# Minitel serial port setup
SERIAL_PORT = "/dev/ttyUSB0"
BAUD_RATE = 1200
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, bytesize=7, parity=serial.PARITY_EVEN, stopbits=1, timeout=0.1)

def minitel(str):
    try:
        ser.write(str.encode('latin1'))
    except:
        print("Error writing to Minitel")
    return

def minitel_clear():
    ser.write(b"\x0C")  # Form Feed clears the screen
