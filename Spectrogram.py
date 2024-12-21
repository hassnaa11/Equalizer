from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
import matplotlib.pyplot as plt
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize
import numpy as np
import warnings

class MplCanvas(Canvas):
    def __init__(self):
        plt.rcParams['axes.facecolor'] = '#000000'
        plt.rc('axes', edgecolor='w')
        plt.gca().spines['top'].set_color('black')
        plt.gca().spines['right'].set_color('black')
        plt.rc('xtick', color='w')
        plt.rc('ytick', color='w')
        plt.rcParams['savefig.facecolor'] = '#000000'
        # plt.rcParams["figure.autolayout"] = True

        # Set the figure size (width, height). Adjust the height here.
        self.figure = plt.figure(figsize=(5.11, 2))  # Decrease height (e.g., 6x4 inches)
        self.figure.patch.set_facecolor('#000000')
        self.axes = self.figure.add_subplot()
        super().__init__(self.figure)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.updateGeometry()
        
        norm = Normalize(vmin=0, vmax=1)  # Set the range of the colorbar
        cmap = 'viridis'  # Choose a colormap
        # mappable = ScalarMappable(norm=norm, cmap=cmap)

        # Add the colorbar to the figure
        # colorbar = self.figure.colorbar(mappable, ax=self.axes, orientation='vertical', pad=0.02)
        # colorbar.ax.yaxis.set_tick_params(color='w')  # Set the color of the ticks on the colorbar
        # colorbar.outline.set_edgecolor('w')  # Set the edge color of the colorbar
        # # colorbar.set_label('Amplitude', color='w')  # Set label for colorbar

        # Update tick label colors to match the dark theme
        self.axes.tick_params(axis='x', colors='w')
        self.axes.tick_params(axis='y', colors='w')
        # colorbar.ax.tick_params(colors='w')  # Set tick colors for the color bar

        # Hide the right and top axes
        self.axes.spines['right'].set_visible(False)
        self.axes.spines['top'].set_visible(False)
        self.axes.spines['bottom'].set_color('w')

    def plot_spectrogram(self, signal, fs, mode="Uniform Mode"):
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning)
            warnings.filterwarnings("ignore", category=RuntimeWarning)
            self.axes.cla()  # Clear the axes for re-plotting
            
            if signal.ndim > 1:
                signal = signal.flatten()  # Flatten multi-dimensional arrays to 1D

            # Set frequency axis limits based on the mode
            if mode == "Uniform Mode":
                y_min, y_max = 1050, 2100
            elif mode == "Musical Mode":
                y_min, y_max = 0, 8000
            elif mode == "Weiner Filter":
                y_min, y_max = 0, 8000
            elif mode == "Animal Mode":
                y_min, y_max = 0, 6000
            else:
                y_min, y_max = 0, 8000

            # Define spectrogram parameters
            NFFT = 768  # FFT size
            noverlap = NFFT // 2  # Overlap size

            # Plot the spectrogram
            Pxx, freqs, bins, im = self.axes.specgram(
                signal,
                Fs=fs,
                cmap="plasma",
                NFFT=NFFT,
                noverlap=noverlap,
            )

            # Check if the color bar already exists
            if hasattr(self, "cbar") and self.cbar is not None:
                # Update the color bar with the new image
                self.cbar.ax.clear()
                self.figure.colorbar(im, cax=self.cbar.ax, ax=self.axes, orientation="vertical")
            else:
                # Create the color bar if it doesn't exist
                self.cbar = self.figure.colorbar(im, ax=self.axes, orientation="vertical")

            # Customize the color bar
            self.cbar.set_label("Intensity (dB)", color="w", fontsize=10)
            self.cbar.ax.tick_params(colors="w")  # Set tick colors for the color bar

            # Set frequency axis limits
            self.axes.set_ylim(y_min, y_max)

            # Customize x-axis and y-axis
            self.axes.set_xlabel("Time (s)", color="w", fontsize=10)  # Add the x-axis label
            self.axes.set_ylabel("Frequency (Hz)", color="w", fontsize=9)
            self.axes.tick_params(axis="x", colors="w", labelsize=8)  # Set x-axis ticks to white
            self.axes.tick_params(axis="y", colors="w", labelsize=8)

            # Adjust visualization for small frequency ranges
            if mode == "ECG Mode" or y_max - y_min < 100:
                self.axes.set_yticks(np.arange(y_min, y_max + 1, 10))  # Fine y-ticks
            else:
                self.axes.set_yticks(np.linspace(y_min, y_max, num=5))

            self.draw()



class SpectrogramViewer(QtWidgets.QWidget):
    def __init__(self, parent=None, sampling_rate=44100):
        super().__init__(parent)
        self.sampling_rate = sampling_rate

        self.canvas = MplCanvas()
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)

    def update_spectrogram(self, signal, mode="Uniform Mode"):
        self.canvas.plot_spectrogram(signal, self.sampling_rate, mode)

    def clear_spectrogram(self):
        self.canvas.axes.cla()  
        self.canvas.draw()  

    def close_spectrogram(self):
        self.canvas.close()

    def show_spectrogram(self):
        self.canvas.show()