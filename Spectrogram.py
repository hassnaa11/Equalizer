from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
import matplotlib.pyplot as plt
import numpy as np
import warnings

class MplCanvas(Canvas):
    def __init__(self):
        plt.rcParams['axes.facecolor'] = '#000000'
        plt.rc('axes', edgecolor='w')
        plt.rc('xtick', color='w')
        plt.rc('ytick', color='w')
        plt.rcParams['savefig.facecolor'] = '#000000'
        plt.rcParams["figure.autolayout"] = True

        self.figure = plt.figure()
        self.figure.patch.set_facecolor('#000000')
        self.axes = self.figure.add_subplot()
        super().__init__(self.figure)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.updateGeometry()

    def plot_spectrogram(self, signal, fs, mode="Uniform Mode"):
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning)
            warnings.filterwarnings("ignore", category=RuntimeWarning)
            self.axes.cla() 

            if signal.ndim > 1:
                signal = signal.flatten()  

            if mode == "Uniform Mode":
                y_min, y_max = 1050, 2100
            elif mode == "Musical Mode":
                y_min, y_max = 80, 7999
            elif mode == "ECG Mode":
                y_min, y_max = 0, 50
            elif mode == "Animal Mode":
                y_min, y_max = 20, 1500
            else:
                y_min, y_max = 1050, 2100  

            # NFFT = 1300  # Larger FFT window size 1024
            # noverlap = NFFT//2  # Increase overlap for smoother transitions 768

            self.axes.specgram(signal, Fs=fs, cmap='viridis')

            self.axes.set_ylim(y_min, y_max)  

            self.axes.set_yticks(np.linspace(y_min, y_max, num=3)) 

            self.axes.set_xlabel("Time (s)", color='w', fontsize=10)
            # self.axes.set_ylabel("Frequency (Hz)", color='w', fontsize=10)

            self.axes.tick_params(axis='x', colors='w', labelsize=8)
            self.axes.tick_params(axis='y', colors='w', labelsize=8)

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