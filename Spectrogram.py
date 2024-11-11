from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
import matplotlib.pyplot as plt
import numpy as np
import warnings

class MplCanvas(Canvas):
    def __init__(self):
        # Set Matplotlib parameters for a dark background and white tick colors
        plt.rcParams['axes.facecolor'] = 'black'
        plt.rc('axes', edgecolor='w')
        plt.rc('xtick', color='w')
        plt.rc('ytick', color='w')
        plt.rcParams['savefig.facecolor'] = 'black'
        plt.rcParams["figure.autolayout"] = True

        # Initialize the figure and axes for the spectrogram
        self.figure = plt.figure()
        self.figure.patch.set_facecolor('black')
        self.axes = self.figure.add_subplot()
        super().__init__(self.figure)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.updateGeometry()

    def plot_spectrogram(self, signal, fs):
        """Plots the spectrogram of the signal with the given sampling frequency."""
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning)
            warnings.filterwarnings("ignore", category=RuntimeWarning)
            self.axes.cla()  # Clear existing plot
            self.axes.specgram(signal, Fs=fs, cmap='viridis')  # Plot spectrogram with 'viridis' color map
            self.axes.set_ylim(0)  # Set y-axis limit
            self.draw()  # Update the canvas

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
