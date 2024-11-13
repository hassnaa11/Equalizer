from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
import matplotlib.pyplot as plt
import numpy as np
import warnings

class MplCanvas(Canvas):
    def __init__(self):
        # Configure Matplotlib to match dark theme
        plt.rcParams['axes.facecolor'] = '#19232D'
        plt.rc('axes', edgecolor='w')
        plt.rc('xtick', color='w')
        plt.rc('ytick', color='w')
        plt.rcParams['savefig.facecolor'] = '#19232D'
        plt.rcParams["figure.autolayout"] = True

        # Initialize the figure and axes for the spectrogram
        self.figure = plt.figure()
        self.figure.patch.set_facecolor('#19232D')
        self.axes = self.figure.add_subplot()
        super().__init__(self.figure)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.updateGeometry()

    def plot_spectrogram(self, signal, fs, mode="Uniform Mode"):
        """Plots the spectrogram of the signal with the specified sampling frequency and mode."""
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning)
            warnings.filterwarnings("ignore", category=RuntimeWarning)
            self.axes.cla()  # Clear any previous plot

            # Set y-axis limits based on mode
            if mode == "Uniform Mode":
                y_min, y_max = 1050, 2100
            elif mode == "Musical Mode":
                y_min, y_max = 80, 7999
            elif mode == "ECG Mode":
                y_min, y_max = 0, 50
            else:
                y_min, y_max = 0, 1000  # Default range

            # Use 'viridis' colormap for greens and blues
            self.axes.specgram(signal, Fs=fs, cmap='viridis')  
            self.axes.set_ylim(y_min, y_max)  # Apply the y-axis limits

            # Set specific y-axis ticks based on y_min and y_max
            self.axes.set_yticks(np.linspace(y_min, y_max, num=3))  # Adjust the number of ticks as needed

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

    def update_spectrogram(self, signal, mode="Uniform Mode"):
        """Update the spectrogram plot with the new signal and mode."""
        self.canvas.plot_spectrogram(signal, self.sampling_rate, mode)

    def clear_spectrogram(self):
        """Clear the spectrogram plot."""
        self.canvas.axes.cla()  # Clear the axes
        self.canvas.draw()  # Redraw the canvas to reflect the cleared state
