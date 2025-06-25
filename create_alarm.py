import numpy as np
from scipy.io import wavfile

# Generate a simple alarm sound
duration = 1.0  # seconds
sample_rate = 44100
t = np.linspace(0, duration, int(sample_rate * duration))

# Create a beeping sound (440 Hz)
frequency = 440
signal = np.sin(2 * np.pi * frequency * t)

# Make it louder
signal = np.int16(signal * 32767)

# Save to file
wavfile.write('alarm.wav', sample_rate, signal) 