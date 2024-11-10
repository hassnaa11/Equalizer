import numpy as np
import matplotlib.pyplot as plt

# Example parameters
sampling_rate = 44100  # Sampling rate in Hz
duration = 1         # Duration in seconds
frequencies = [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000]  # Frequencies of the sine waves in Hz
amplitude = 1.0

# Generate a sample signal: sum of three sine waves
t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)
signal = sum(amplitude * np.sin(2 * np.pi * f * t) for f in frequencies)

# Perform FFT
fft_result = np.fft.fft(signal)
fft_magnitude = np.abs(fft_result) / len(signal)  # Normalize the magnitude

# Calculate frequency bins
freqs = np.fft.fftfreq(len(signal), 1 / sampling_rate)

# Only take the positive half of the spectrum for plotting
positive_freqs = freqs[:len(freqs) // 2]
positive_magnitude = fft_magnitude[:len(freqs) // 2]

# Plot the frequency domain (magnitude spectrum)
plt.figure(figsize=(10, 6))
plt.plot(positive_freqs, positive_magnitude)
plt.title("Frequency Domain of the Signal")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude")
plt.grid()
plt.show()
