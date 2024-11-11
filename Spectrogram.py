from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
import matplotlib.pyplot as plt
import numpy as np
import warnings

class MplCanvas(Canvas):
    def __init__(self):
        # Configure Matplotlib to match dark theme
        plt.rcParams['axes.facecolor'] = '#19232D'  # Background color
        plt.rc('axes', edgecolor='w')  # Axis color
        plt.rc('xtick', color='w')  # X-tick color
        plt.rc('ytick', color='w')  # Y-tick color
        plt.rcParams['savefig.facecolor'] = '#19232D'  # Background for saved figures
        plt.rcParams["figure.autolayout"] = True

        # Initialize the figure and axes for the spectrogram
        self.figure = plt.figure()
        self.figure.patch.set_facecolor('#19232D')  # Set background color for the figure
        self.axes = self.figure.add_subplot()
        super().__init__(self.figure)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.updateGeometry()

    def plot_spectrogram(self, signal, fs):
        """Plots the spectrogram of the signal with the specified sampling frequency."""
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning)
            warnings.filterwarnings("ignore", category=RuntimeWarning)
            self.axes.cla()  # Clear any previous plot
            
            # Use 'viridis' colormap for greens and blues
            Pxx, freqs, bins, im = self.axes.specgram(signal, Fs=fs, cmap='viridis', NFFT=1024, noverlap=512)
            self.axes.set_ylim(0, 1000)  # Set y-axis limit to 0-1000 Hz

            # Set specific y-axis ticks at 0, 500, and 1000 Hz
            self.axes.set_yticks([0, 500, 1000])

            # Set axis labels with color for visibility on dark background
            self.axes.set_xlabel("Time (s)", color='w', fontsize=10)
            self.axes.set_ylabel("Frequency (Hz)", color='w', fontsize=10)

            # Adjust tick parameters for both axes
            self.axes.tick_params(axis='x', colors='w', labelsize=8)
            self.axes.tick_params(axis='y', colors='w', labelsize=8)

            # Force a redraw of the figure to apply changes
            self.draw()

class SpectrogramViewer(QtWidgets.QWidget):
    def __init__(self, parent=None, sampling_rate=44100):
        super().__init__(parent)
        self.sampling_rate = sampling_rate

        # Create and embed the MplCanvas within a widget layout
        self.canvas = MplCanvas()
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)

    def update_spectrogram(self, signal):
        """Update the spectrogram plot with the new signal."""
        self.canvas.plot_spectrogram(signal, self.sampling_rate)

    def clear_spectrogram(self):
        """Clear the spectrogram plot."""
        self.canvas.axes.cla()  # Clear the axes
        self.canvas.draw()  # Redraw the canvas to reflect the cleared state
