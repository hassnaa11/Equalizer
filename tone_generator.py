import numpy as np
import wave

sampling_rate = 44100 
duration = 50  
frequencies = [ 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000] 
amplitude = 32767 / len(frequencies)  # scale amplitude by the number of frequencies

# time vector
t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)

# sum sins to generate the signal
combined_signal = sum(amplitude * np.sin(2 * np.pi * f * t) for f in frequencies)

# clip to int16 range to avoid overflow
combined_signal = np.clip(combined_signal, -32768, 32767).astype(np.int16)

# save to .wav file
with wave.open("synthetic_signal.wav", "w") as wav_file:
    wav_file.setnchannels(1)  
    wav_file.setsampwidth(2)
    wav_file.setframerate(sampling_rate)
    wav_file.writeframes(combined_signal.tobytes())
