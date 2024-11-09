from gui1 import Ui_MainWindow
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from scipy.signal import butter, lfilter
import pyqtgraph as pg
import sys
from pathlib import Path
import numpy as np
import scipy.io.wavfile as wav
import pyaudio

def bandpass_filter(data, lowcut, highcut, fs, order=5):
    """
    Apply a bandpass filter to the given data.
    
    Parameters:
    - data: The input signal data to be filtered.
    - lowcut: The low cutoff frequency of the bandpass filter.
    - highcut: The high cutoff frequency of the bandpass filter.
    - fs: The sampling rate of the data.
    - order: The order of the filter (higher order means a sharper cutoff).
    
    Returns:
    - The filtered data.
    """
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    y = lfilter(b, a, data)
    return y

class Equilizer(QMainWindow):
   def __init__(self):
       super().__init__()
       self.ui = Ui_MainWindow()
       self.ui.setupUi(self)
       self.ecg_mode_selected = False

       # musical mode
       self.timer = QTimer(self)
       self.state=False
       self.timer.timeout.connect(self.update_plot)
       self.audio_stream = None
       self.play_equalized_audio=True
       self.data = None  # Holds the audio data
       self.index = 0 
       self.chunk_size = 3000
       self.ui.Violin_slider.setRange(0, 300)
       self.ui.guitar_slider.setRange(0, 200)
       self.ui.drums_slider.setRange(0, 100)
       self.ui.Saxophone_slider.setRange(0, 150)

       self.ui.Saxophone_slider.setRange(200,1000)
       self.ui.guitar_slider.valueChanged.connect(lambda:self.update_instrument("Guitar"))
       self.ui.Violin_slider.valueChanged.connect(lambda:self.update_instrument("Violin"))
       self.ui.drums_slider.valueChanged.connect(lambda:self.update_instrument("Drums"))
       self.ui.Saxophone_slider.valueChanged.connect(lambda:self.update_instrument("Saxophone"))
       
       self.ui.open_btn.clicked.connect(self.open_file)
       self.ui.original_sound_btn.clicked.connect(lambda:self.control_sound("original_btn"))
       self.ui.equalized_sound_btn.clicked.connect(lambda: self.control_sound("equalized_btn"))
       self.sliders = {
            "Guitar": self.ui.guitar_slider,
            "Saxophone": self.ui.Saxophone_slider,
            "Drums":self.ui.drums_slider,
            "Violin": self.ui.Violin_slider
        }
       #end
    
       self.sliders_frames = {
            "Uniform Mode": self.ui.uniform_sliders_frame,
            "Animal Mode": self.ui.animals_sliders_frame,
            "Musical Mode": self.ui.music_sliders_frame,
            "ECG Mode": self.ui.ecg_sliders_frame
        }

       for sliders_frame in self.sliders_frames:
            self.sliders_frames[sliders_frame].setVisible(False)
       self.sliders_frames["Uniform Mode"].setVisible(True)
       self.ranges_sliders = {
            self.ui.uniform_slider_1: (0, 200),
            self.ui.uniform_slider_2: (200, 400),
            self.ui.uniform_slider_3: (400, 600),
            self.ui.uniform_slider_4: (600, 800),
            self.ui.uniform_slider_5: (800, 1000),
            self.ui.uniform_slider_6: (1000, 1200),
            self.ui.uniform_slider_7: (1200, 1400),
            self.ui.uniform_slider_8: (1400, 1600),
            self.ui.uniform_slider_9: (1600, 1800),
            self.ui.uniform_slider_10: (1800, 2000),
        }
       self.ecg_sliders = {
        self.ui.p_wave_arrhythmia_slider: (5, 10),
        self.ui.sv_arrhythmia_slider: (6, 22),
        self.ui.nr_arrhythmia_slider: (0, 10)
    }
       self.slices_sliders = {
        self.ui.wolf_slider: "wolf",
        self.ui.horse_slider: "horse",
        self.ui.cow_slider: "cow",
        self.ui.dolphin_slider: "dolphin",
        self.ui.elephant_slider: "elephant",
        self.ui.frog_slider: "frog",

        # self.trumpet_slider: "trumpet",
        self.ui.Saxophone_slider: "Saxophone",
        self.ui.drums_slider: "drums",
        self.ui.guitar_slider: "Guitar",
        self.ui.Violin_slider: "Violin"
    }
       self.ecg_arrs_max_f_dict = {

        0.96: self.ui.p_wave_arrhythmia_slider,
        0.96459: self.ui.sv_arrhythmia_slider,
        0.38376: self.ui.nr_arrhythmia_slider
    }

       self.ui.mode_comboBox.currentTextChanged.connect(self.change_sliders_for_modes)

   def set_home_view(self):
        if self.ecg_mode_selected:
            self.original_signal_viewer.xRange = [0, 1e3]
            self.original_signal_viewer.yRange = [-2, 2]
            self.equalized_signal_viewer.xRange = [0, 1e3]
            self.equalized_signal_viewer.yRange = [-2, 2]
        else:
            self.original_signal_viewer.home_view()
            self.equalized_signal_viewer.home_view()

   def change_sliders_for_modes(self, text):
        for sliders_frame in self.sliders_frames:
            self.sliders_frames[sliders_frame].setVisible(False)
        self.sliders_frames[text].setVisible(True)
        if text == 'ECG Mode':
            self.ecg_mode_selected = True
            self.original_signal_viewer.xRange = [0, 1e3]
            self.original_signal_viewer.yRange = [-2, 2]
            self.equalized_signal_viewer.xRange = [0, 1e3]
            self.equalized_signal_viewer.yRange = [-2, 2]
        else:
            self.ecg_mode_selected = False
   def open_file(self):
    file_name, _ = QFileDialog.getOpenFileName(self, "Open WAV", "", "WAV Files (*.wav);;All Files (*)")
    
    if file_name:
        self.from_file = True 
        self.plot_original_data(file_name)   
        self.index = 0
        self.play_audio=True
        self.timer.start(50)  
        print(file_name)  

   def plot_original_data(self, file_name):
        self.fs, self.data = wav.read(file_name)  # Read the WAV file
        if len(self.data.shape) > 1:
            self.data = self.data[:, 0]
        self.ui.original_graphics_view.plot(self.data[:self.chunk_size], clear=True)
        self.audio_stream = pyaudio.PyAudio()
        self.stream = self.audio_stream.open(format=pyaudio.paInt16,
                                             channels=1,
                                             rate=self.fs,
                                             output=True)
        self.instruments = {
            "Drums": (100, 1000),
            "Guitar": (80, 1200),
            "Saxophone": (250, 1200),
            "Violin": (200, 3500)
        }
        self.filtered_data = {}
        for instrument, (low, high) in self.instruments.items():
            self.filtered_data[instrument] = bandpass_filter(self.data, low, high, self.fs)
            print(self.filtered_data)
        self.ui.equalized_graphics_view.plot(self.data[:self.chunk_size], clear=True)
    

 
       
   def update_plot(self):
        if self.index + self.chunk_size <= len(self.data):
            # Get the next chunk of the original data
            chunk = self.data[self.index:self.index + self.chunk_size]
            # Plot the original signal
            self.ui.original_graphics_view.plot(chunk, clear=True)
            if self.state==False:
             self.ui.equalized_graphics_view.plot(chunk, clear=True)
            else:
                chunk_equalized=self.equalized_signal[self.index:self.index + self.chunk_size]
                self.ui.equalized_graphics_view.plot(chunk_equalized ,clear=True)
                if self.play_equalized_audio:
                    self.stream.write(chunk_equalized.astype(np.int16).tobytes())
            if self.play_audio:
                self.stream.write(chunk.astype(np.int16).tobytes())
            self.index += self.chunk_size
        else:
            # Stop the timer and audio stream when the end of the file is reached
            self.timer.stop()
            self.stream.stop_stream()
            self.stream.close()
            self.audio_stream.terminate()
    

   def update_instrument(self, instrument):
        slider_value = self.sliders[instrument].value() / 100
        self.equalized_signal = np.zeros_like(self.data, dtype=np.float32)
        
        # Sum up the filtered signals with their respective slider values
        for inst, _ in self.instruments.items():
            instrument_slider_value = self.sliders[inst].value() / 100
            self.equalized_signal += instrument_slider_value * self.filtered_data[inst]
        self.state=True
        

        
   def control_sound(self,btn):
       if btn=="equalized_btn":
           self.play_equalized_audio=False
       else:
        self.play_audio=False
        


if __name__ == "__main__":
    app = QApplication([])
    ui = Equilizer()
    ui.showMaximized()
    app.exec_()        