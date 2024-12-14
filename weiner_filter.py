import numpy as np
from scipy.io import wavfile
from scipy.signal import stft, istft
import soundfile as sf
import tempfile
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QUrl
import sys
import os

class WeinerFilter:
    def __init__(self):
        super().__init__()

    def apply_wiener_filter(self, noisy_signal, noise_signal, fs, n_fft=1024, overlap=None, iterations=3, spectral_floor=0.1):
        if overlap is None or overlap >= n_fft:
            overlap = n_fft // 2

        # Compute STFT - Short Time Fourier Transform
        _, _, noisy_stft = stft(noisy_signal, fs, nperseg=n_fft, noverlap=overlap)
        _, _, noise_stft = stft(noise_signal, fs, nperseg=n_fft, noverlap=overlap)

        # Estimate noise PSD
        noise_psd = np.mean(np.abs(noise_stft) ** 2, axis=-1, keepdims=True)

        # Iterative Wiener filtering
        filtered_stft = noisy_stft
        for _ in range(iterations):
            noisy_psd = np.abs(filtered_stft) ** 2
            wiener_filter = np.maximum(noisy_psd / (noisy_psd + noise_psd), spectral_floor)
            filtered_stft = wiener_filter * noisy_stft

        # Inverse STFT
        _, denoised_signal = istft(filtered_stft, fs, nperseg=n_fft, noverlap=overlap)

        # save to file
        temp_audio_file = tempfile.mktemp(suffix=".wav")
        real_signal = np.real(denoised_signal)
        real_signal /= np.max(np.abs(real_signal))  # Normalize
        sf.write(temp_audio_file, real_signal.astype(np.float32), fs)
        return temp_audio_file, real_signal


if __name__ == "__main__":
    app = QApplication(sys.argv)
    weiner = WeinerFilter()

    fs, noisy_signal = wavfile.read('Signals/weiner/anne_ship.wav')
    fs, noise_signal = wavfile.read('Signals/weiner/ship.wav')
    print(noisy_signal)

    # Ensure signals are mono
    if noisy_signal.ndim > 1:
        noisy_signal = noisy_signal[:, 0]
    if noise_signal.ndim > 1:
        noise_signal = noise_signal[:, 0]

    denoised_signal_path,_ = weiner.apply_wiener_filter(noisy_signal, noise_signal, fs)

    if os.path.exists(denoised_signal_path):
        print(f"Denoised signal saved at: {denoised_signal_path}")

        player = QMediaPlayer()
        player.setMedia(QMediaContent(QUrl.fromLocalFile(denoised_signal_path)))

        player.setVolume(100)
        player.play()

        sys.exit(app.exec_())
    else:
        print("Failed to generate the denoised audio file.")
        
        
        
        
        
"""
Apply an iterative Wiener filter for enhanced noise removal.

Parameters:
    noisy_signal (numpy array): The noisy audio signal.
    noise_signal (numpy array): A noise-only segment for estimation.
    fs (int): Sampling frequency of the signals.
    n_fft (int): Number of FFT points.
    overlap (int): Overlap between segments. If None, set to half of n_fft.
    iterations (int): Number of iterative filtering steps.
    spectral_floor (float): Minimum filter gain to preserve weak signal components.

Returns:
    str: Path to the denoised audio file.
"""        
