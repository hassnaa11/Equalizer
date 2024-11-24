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
# from arrhythmia_handler import detect_arrhythmias, apply_slider_changes
from Spectrogram import SpectrogramViewer
import scipy.signal
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl
import numpy as np, bisect, librosa, soundfile as sf
import os
import tempfile
temp_audio_file = tempfile.mktemp(suffix=".wav")
# self.audio_file = tempfile.mktemp(suffix=".wav")


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
    if not (0 < low < 1) or not (0 < high < 1):
        print(f"Invalid frequency range: low={low}, high={high}, nyquist={nyquist}")
        return data 
    b, a = butter(order, [low, high], btype="band")
    y = lfilter(b, a, data)
    return y


class Equilizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ecg_mode_selected = False
        self.ecg_signal = None  # To hold the ECG signal data
        self.equalized_signal = None  # To store modified signal
        
        # modes Combobox
        # self.ui.mode_comboBox.currentTextChanged.connect(self.replay)
        self.file_name = None

        # button functions
        self.ui.play_pause_btn.clicked.connect(self.play_pause)
        # self.ui.show_hide_btn.clicked.connect(self.toggle_spectrogram_visibility)
        self.ui.replay_btn.clicked.connect(self.replay)

        # musical mode
        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.state = False
        self.timer.timeout.connect(self.update_plot)
        self.is_timer_running = False
        self.audio_stream = None
        self.player = QMediaPlayer()
        self.play_equalized_audio = False
        self.play_audio = False
        self.data = np.array([])  # Holds the audio data
        self.index = 0
        self.chunk_size = 3000
        self.ui.pushButton_12.setIcon(QIcon(f'icons/icons/drums2.png'))
        # self.ui.Violin_slider.setRange(1, 100)
        # self.ui.guitar_slider.setRange(1, 100)
        # self.ui.drums_slider.setRange(1, 100)
        # self.ui.Saxophone_slider.setRange(1, 100)
        self.ui.guitar_slider.valueChanged.connect(
            lambda: self.update_instrument("Guitar")
        )
        self.ui.Violin_slider.valueChanged.connect(
            lambda: self.update_instrument("Violin")
        )
        self.ui.drums_slider.valueChanged.connect(
            lambda: self.update_instrument("Drums")
        )
        self.ui.Saxophone_slider.valueChanged.connect(
            lambda: self.update_instrument("Saxophone")
        )
        self.ui.open_btn.clicked.connect(self.open_file)
        self.ui.original_sound_btn.clicked.connect(
            lambda: self.control_sound("original_btn")
        )
        self.ui.equalized_sound_btn.clicked.connect(
            lambda: self.control_sound("equalized_btn")
        )
        self.sliders = {
            "Guitar": self.ui.guitar_slider,
            "Saxophone": self.ui.Saxophone_slider,
            "Drums": self.ui.drums_slider,
            "Violin": self.ui.Violin_slider,
        }
        self.instruments = {
            "Guitar": (80, 1500),
            "Violin": (1500, 3000),
            "Drums": (3000, 5000),
            "Saxophone": (5000,8000),
            
        }
        # end of music

        # animal mode
        self.animal_sliders = {
            "wolf": self.ui.wolf_slider,
            "horse": self.ui.horse_slider,
            "cow": self.ui.cow_slider,
            "dolphin": self.ui.dolphin_slider,
            "elephant": self.ui.elephant_slider,
            "frog": self.ui.frog_slider,
        }
        self.animal_ranges = {
        "wolf": (3200, 4000),        
        "horse": (2400, 3200),      
        "cow": (800,1600 ),         
        "dolphin": (4000, 5000), 
        "elephant": (0, 800),    
        "frog": (1600, 2400),      
}
        # self.ui.wolf_slider.setRange(1,100)
        # self.ui.horse_slider.setRange(1,100)
        # self.ui.cow_slider.setRange(1,100)
        # self.ui.dolphin_slider.setRange(1,100)
        # self.ui.elephant_slider.setRange(1,100)
        # self.ui.frog_slider.setRange(1,100)
        self.ui.wolf_slider.valueChanged.connect(lambda: self.update_animal("wolf"))
        self.ui.horse_slider.valueChanged.connect(lambda: self.update_animal("horse"))
        self.ui.cow_slider.valueChanged.connect(lambda: self.update_animal("cow"))
        self.ui.dolphin_slider.valueChanged.connect(lambda: self.update_animal("dolphin"))
        self.ui.elephant_slider.valueChanged.connect(lambda: self.update_animal("elephant"))
        self.ui.frog_slider.valueChanged.connect(lambda: self.update_animal("frog"))
        # end of animal mode

        self.sliders_frames = {
            "Uniform Mode": self.ui.uniform_sliders_frame,
            "Animal Mode": self.ui.animals_sliders_frame,
            "Musical Mode": self.ui.music_sliders_frame,
            "ECG Mode": self.ui.ecg_sliders_frame,
        }
        for sliders_frame in self.sliders_frames:
            self.sliders_frames[sliders_frame].setVisible(False)
        self.sliders_frames["Uniform Mode"].setVisible(True)
        self.uniform_sliders = {
            1: self.ui.uniform_slider_1,
            2: self.ui.uniform_slider_2,
            3: self.ui.uniform_slider_3,
            4: self.ui.uniform_slider_4,
            5: self.ui.uniform_slider_5,
            6: self.ui.uniform_slider_6,
            7: self.ui.uniform_slider_7,
            8: self.ui.uniform_slider_8,
            9: self.ui.uniform_slider_9,
            10: self.ui.uniform_slider_10,
        }

        self.uniform_ranges ={
            1: (1050, 1150),
            2: (1150, 1250),
            3: (1250, 1350),
            4: (1350, 1450), 
            5: (1450, 1550), 
            6: (1550, 1650),
            7: (1650, 1750), 
            8: (1750, 1850),
            9: (1850, 1950),
            10: (1950, 2050)
        }
        
        self.ui.uniform_slider_1.setValue(100)
        self.ui.uniform_slider_2.setValue(100)
        self.ui.uniform_slider_3.setValue(100)
        self.ui.uniform_slider_4.setValue(100)
        self.ui.uniform_slider_5.setValue(100)
        self.ui.uniform_slider_6.setValue(100)
        self.ui.uniform_slider_7.setValue(100)
        self.ui.uniform_slider_8.setValue(100)
        self.ui.uniform_slider_9.setValue(100)
        self.ui.uniform_slider_10.setValue(100)
        
        self.ui.uniform_slider_1.valueChanged.connect(self.update_uniform_slider)
        self.ui.uniform_slider_2.valueChanged.connect(self.update_uniform_slider)
        self.ui.uniform_slider_3.valueChanged.connect(self.update_uniform_slider)
        self.ui.uniform_slider_4.valueChanged.connect(self.update_uniform_slider)
        self.ui.uniform_slider_5.valueChanged.connect(self.update_uniform_slider)
        self.ui.uniform_slider_6.valueChanged.connect(self.update_uniform_slider)
        self.ui.uniform_slider_7.valueChanged.connect(self.update_uniform_slider)
        self.ui.uniform_slider_8.valueChanged.connect(self.update_uniform_slider)
        self.ui.uniform_slider_9.valueChanged.connect(self.update_uniform_slider)
        self.ui.uniform_slider_10.valueChanged.connect(self.update_uniform_slider)

        self.ecg_sliders = {
            "vf": self.ui.vf_arrhythmia_slider,
            "mi": self.ui.mi_arrhythmia_slider,
            "sr": self.ui.sr_arrhythmia_slider,
        }

        self.ecg_ranges = {

            "vf": (7, 50),   #venticular fibrillation
            "mi": (0.5, 20), #Premature Ventricular Contractions
            "sr": (1, 15),   #brugada syndrome

        }


        for slider in self.ecg_sliders.values():
            slider.valueChanged.connect(self.update_ecg_slider)

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
            self.ui.Violin_slider: "Violin",
        }
       
        self.ui.mode_comboBox.currentTextChanged.connect(self.change_sliders_for_modes)
        
        self.show_spectrograms = True
        self.sampling_rate = 44100  
        self.original_spectrogram_viewer = SpectrogramViewer(self.ui.original_spectro_graphics_view, self.sampling_rate)
        self.equalized_spectrogram_viewer = SpectrogramViewer(self.ui.equalized_spectro_graphics_view, self.sampling_rate)
        self.is_audiogram = False
        self.ui.show_hide_btn.clicked.connect(self.toggle_spectrogram_visibility)
        self.ui.reset_view_btn.setText("Audiogram") 
        self.ui.reset_view_btn.clicked.connect(self.toggle_scale)
        self.ui.speed_slider.valueChanged.connect(self.adjust_playback_speed)
        self.ui.zoom_in_btn.clicked.connect(self.zoom_in)
        self.ui.zoom_out_btn.clicked.connect(self.zoom_out)
        self.ui.stop_btn.clicked.connect(self.stop)
        
        self.c = 0

    def zoom_in(self):
            x_range, y_range = self.ui.original_graphics_view.viewRange()

            zoom_factor = 0.9  

            x_center = (x_range[0] + x_range[1]) / 2
            y_center = (y_range[0] + y_range[1]) / 2
            new_x_range = [(x_range[0] - x_center) * zoom_factor + x_center, 
                        (x_range[1] - x_center) * zoom_factor + x_center]
            new_y_range = [(y_range[0] - y_center) * zoom_factor + y_center, 
                        (y_range[1] - y_center) * zoom_factor + y_center]
    
            self.ui.original_graphics_view.setXRange(*new_x_range)
            self.ui.original_graphics_view.setYRange(*new_y_range)
            self.ui.equalized_graphics_view.setXRange(*new_x_range)
            self.ui.equalized_graphics_view.setYRange(*new_y_range)

    def zoom_out(self):
            x_range, y_range = self.ui.original_graphics_view.viewRange()
            
            zoom_factor = 1.1  
        
            x_center = (x_range[0] + x_range[1]) / 2
            y_center = (y_range[0] + y_range[1]) / 2
            new_x_range = [(x_range[0] - x_center) * zoom_factor + x_center, 
                        (x_range[1] - x_center) * zoom_factor + x_center]
            new_y_range = [(y_range[0] - y_center) * zoom_factor + y_center, 
                        (y_range[1] - y_center) * zoom_factor + y_center]
            
            self.ui.original_graphics_view.setXRange(*new_x_range)
            self.ui.original_graphics_view.setYRange(*new_y_range)
            self.ui.equalized_graphics_view.setXRange(*new_x_range)
            self.ui.equalized_graphics_view.setYRange(*new_y_range)

    def stop(self):
            # self.stream.close()
            self.timer.stop()
            self.data = None
            self.audio_stream.terminate()
            self.is_timer_running = False
            self.state = False
            self.index = 0
            self.ui.play_pause_btn.setIcon(QIcon(f'icons/icons/play copy.svg')) 
            self.player.stop()
            self.play_audio = False
            self.play_equalized_audio = False
            self.original_spectrogram_viewer.clear_spectrogram()
            self.equalized_spectrogram_viewer.clear_spectrogram()
            self.ui.frequency_graphics_view.clear()
            self.ui.original_graphics_view.clear()
            self.ui.equalized_graphics_view.clear()
            self.reset_sliders()
           

    def adjust_playback_speed(self):
        speed = self.ui.speed_slider.value()
        base_interval = 50  # Original interval in ms (1x speed)
        self.timer.setInterval(base_interval // speed)
        print(f"Playback speed set to {speed}x, Timer interval: {self.timer.interval()} ms")


    def toggle_scale(self):
        """
        Toggle between linear and audiogram scales.
        """
        if self.is_audiogram:
            self.is_audiogram = False
            self.ui.reset_view_btn.setText("Audiogram")  
        else:
            self.is_audiogram = True
            self.ui.reset_view_btn.setText("Linear")  
        
        self.plot_frequency_graph()
        self.c = 0
        self.phases = []

    def toggle_spectrogram_visibility(self):
        if self.show_spectrograms:
            self.ui.original_spectro_frame.hide()
            self.ui.equalized_spectro_frame.hide()
            self.ui.original_spectro_graphics_view.hide()
            self.ui.equalized_spectro_graphics_view.hide()
            self.original_spectrogram_viewer.close_spectrogram()
            self.equalized_spectrogram_viewer.close_spectrogram()
        else:
            self.ui.original_spectro_frame.show()
            self.ui.equalized_spectro_frame.show()
            self.ui.original_spectro_graphics_view.show()
            self.ui.equalized_spectro_graphics_view.show()
            self.original_spectrogram_viewer.show_spectrogram()
            self.equalized_spectrogram_viewer.show_spectrogram()

        self.show_spectrograms = not self.show_spectrograms


    def on_mode_change(self):
        if self.file_name:
            self.timer.stop()   
            self.is_timer_running = False 
            self.plot_original_data()
            self.index = 0
            self.state = False
            self.timer.start()  
            self.is_timer_running = True  
                  

    def play_pause(self):
        if self.is_timer_running:
            self.ui.play_pause_btn.setIcon(QIcon(f'icons/icons/play copy.svg'))
            self.timer.stop()
            self.player.pause()
        else:
            self.ui.play_pause_btn.setIcon(QIcon(f'icons/icons/pause copy.svg'))
            self.timer.start(50)
            self.player.play()
        self.is_timer_running = not self.is_timer_running
        self.play_audio = not self.play_audio
        self.play_equalized_audio = not self.play_equalized_audio

    def replay(self):
        
        self.is_timer_running = False
        self.index = 0
        self.player.stop()
        self.play_audio = False
        self.play_equalized_audio = False
        self.on_mode_change()
        self.ui.play_pause_btn.setIcon(QIcon(f'icons/icons/pause copy.svg'))
        self.reset_sliders()    
        self.state = True
        self.plot_frequency_graph() 
        
         
    def reset_sliders(self):
         # Reset the sliders to their initial values

        #animal mode
        self.ui.wolf_slider.setValue(100)
        self.ui.horse_slider.setValue(100)
        self.ui.cow_slider.setValue(100)
        self.ui.dolphin_slider.setValue(100)
        self.ui.elephant_slider.setValue(100)
        self.ui.frog_slider.setValue(100)

        #ecg mode
        self.ui.vf_arrhythmia_slider.setValue(100)
        self.ui.mi_arrhythmia_slider.setValue(100)
        self.ui.sr_arrhythmia_slider.setValue(100)

        #uniform mode
        self.ui.uniform_slider_1.setValue(100)
        self.ui.uniform_slider_2.setValue(100)
        self.ui.uniform_slider_3.setValue(100)
        self.ui.uniform_slider_4.setValue(100)
        self.ui.uniform_slider_5.setValue(100)
        self.ui.uniform_slider_6.setValue(100)
        self.ui.uniform_slider_7.setValue(100)
        self.ui.uniform_slider_8.setValue(100)
        self.ui.uniform_slider_9.setValue(100)
        self.ui.uniform_slider_10.setValue(100)

        #musical mode
        self.ui.guitar_slider.setValue(100)
        self.ui.Violin_slider.setValue(100)
        self.ui.drums_slider.setValue(100)
        self.ui.Saxophone_slider.setValue(100)


    def set_home_view(self):
        if self.ecg_mode_selected:
            self.ui.original_graphics_view.xRange = [0, 1e3]
            self.ui.original_graphics_view.yRange = [-2, 2]
            self.ui.equalized_graphics_view.xRange = [0, 1e3]
            self.ui.equalized_graphics_view.yRange = [-2, 2]
        else:
            self.original_signal_viewer.home_view()
            self.equalized_signal_viewer.home_view()

    def change_sliders_for_modes(self, text):
        for sliders_frame in self.sliders_frames:
            self.sliders_frames[sliders_frame].setVisible(False)
        self.sliders_frames[text].setVisible(True)
        if text == "ECG Mode":
            self.ecg_mode_selected = True
            self.ui.original_graphics_view.xRange = [0, 1e3]
            self.ui.original_graphics_view.yRange = [-2, 2]
            self.ui.equalized_graphics_view.xRange = [0, 1e3]
            self.ui.equalized_graphics_view.yRange = [-2, 2]
        else:
            self.ecg_mode_selected = False

    def open_file(self):
        self.reset_sliders()
        self.file_name, _ = QFileDialog.getOpenFileName(
            self, "Open WAV", "", "WAV Files (*.wav);;All Files (*)"
        )
        print("fileeeeeeeeee: ", self.file_name)
        if self.file_name:
            self.from_file = True
            self.plot_original_data()
            self.index = 0
            # self.play_audio=False
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(self.file_name)))
            # self.player.play()
            self.timer.start()
            print(self.file_name)

    def plot_original_data(self):
        self.fs, self.data = wav.read(self.file_name)  # Read the WAV file
        if self.data.ndim > 1:
             self.data = self.data[:, 0]  # Use only the first channel


        # self.fs = 22050
        print(f"Sample rate of the file: {self.fs}")

        mode = self.ui.mode_comboBox.currentText()
        if mode == "ECG Mode" and self.fs != 500:
            print("Resampling ECG signal to 500 Hz")
            target_fs = 500                                           
            num_samples = int(len(self.data) * target_fs / self.fs)
            self.data = scipy.signal.resample(self.data, num_samples)
            self.fs = target_fs
            print(f"Resampled to: {self.fs} Hz")


        self.equalized_signal = self.data
        self.calculate_initial_fft()
        self.plot_frequency_graph()
        
        self.cumulative_time = []  # Reset cumulative time
        self.cumulative_data = []  # Reset cumulative data

        chunk = self.data[: self.chunk_size]
        time_chunk = np.arange(0, len(chunk)) / self.fs

        # Validate chunk lengths
        if len(chunk) != len(time_chunk):
            print("Mismatch in chunk lengths")
            return

        self.cumulative_time.extend(time_chunk)
        self.cumulative_data.extend(chunk)

        self.ui.original_graphics_view.plot(self.cumulative_time, self.cumulative_data, clear=True)


        self.cumulative_equalized_time = []  # To store time values for the equalized signal
        self.cumulative_equalized_data = []  # To store equalized signal values
        


        

        if mode == "Uniform Mode":
            self.original_spectrogram_viewer.update_spectrogram(self.data[: self.chunk_size], mode = "Uniform Mode")
        elif mode == "Musical Mode":
            self.original_spectrogram_viewer.update_spectrogram(self.data[: self.chunk_size], mode = "Musical Mode")
        elif mode == "Animal Mode":
            self.original_spectrogram_viewer.update_spectrogram(self.data[: self.chunk_size], mode = "Animal Mode")
    
        if mode == "ECG Mode":
            # print("Displaying ECG data in static mode")
            self.ui.original_graphics_view.plot(time_chunk, chunk, clear=True)
            self.original_spectrogram_viewer.update_spectrogram(self.data, mode = "ECG Mode")
            self.filtered_data = {}
            for band_number, (low, high) in self.ecg_ranges.items():
                self.filtered_data[band_number] = bandpass_filter(
                    self.data, low, high, self.fs
                )

            self.ui.equalized_graphics_view.plot(time_chunk, chunk, clear=True) 
            self.equalized_spectrogram_viewer.update_spectrogram(self.data, mode = "ECG Mode")


        if mode == "Musical Mode" or mode == "Uniform Mode" or mode == "Animal Mode":
            # self.audio_stream = pyaudio.PyAudio()
            # self.stream = self.audio_stream.open(
            #     format=pyaudio.paInt16, channels=1, rate=self.fs, output=True
            # )
            
            self.ui.original_graphics_view.plot(self.cumulative_time, self.cumulative_data, clear=True)
            self.filtered_data = {}
            if mode == "Musical Mode":
                for instrument, (low, high) in self.instruments.items():
                    self.filtered_data[instrument] = bandpass_filter(
                        self.data, low, high, self.fs
                    )
                    print(self.filtered_data)
                self.equalized_spectrogram_viewer.update_spectrogram(self.data[: self.chunk_size], mode = "Musical Mode")

            elif mode == "Uniform Mode":
                for slider_number, (low, high) in self.uniform_ranges.items():
                    self.filtered_data[slider_number] = bandpass_filter(
                        self.data, low, high, self.fs
                    )
                    print(self.filtered_data)
                self.equalized_spectrogram_viewer.update_spectrogram(self.data[: self.chunk_size], mode == "Uniform Mode")
            elif mode == "Animal Mode":
                for animal, (low, high) in self.animal_ranges.items():
                    self.filtered_data[animal] = bandpass_filter(
                        self.data, low, high, self.fs
                    )
                    print(self.filtered_data)
                self.equalized_spectrogram_viewer.update_spectrogram(self.data[: self.chunk_size], mode == "Animal Mode")


            self.ui.equalized_graphics_view.plot(self.cumulative_time, self.cumulative_data,clear=True)



    def update_plot(self):
        if not self.data.any():
            return
      

        mode = self.ui.mode_comboBox.currentText()
        chunk = self.data[self.index : self.index + self.chunk_size]
        time_chunk = np.arange(self.index, self.index + self.chunk_size) / self.fs

        # Append new chunk to cumulative data
        self.cumulative_time.extend(time_chunk)
        self.cumulative_data.extend(chunk)

        if mode == "ECG Mode":
            return

        if self.index + self.chunk_size <= len(self.data):
            if mode == "Musical Mode" or mode == "Uniform Mode" or mode == "Animal Mode":
                # Get the next chunk of the original data
                chunk = self.data[self.index : self.index + self.chunk_size]

                if mode == "Musical Mode":
                    self.original_spectrogram_viewer.update_spectrogram(chunk, mode = "Musical Mode")
                else:
                    self.original_spectrogram_viewer.update_spectrogram(chunk, mode = "Uniform Mode")

                 # Plot cumulative data
                self.ui.original_graphics_view.plot(self.cumulative_time, self.cumulative_data, clear=True)
                if self.state == False:
                    self.ui.equalized_graphics_view.plot(self.cumulative_time, self.cumulative_data, clear=True)

                    if mode == "Musical Mode":
                        self.equalized_spectrogram_viewer.update_spectrogram(chunk, mode = "Musical Mode")
                    elif mode == "Animal Mode":
                        self.equalized_spectrogram_viewer.update_spectrogram(chunk, mode = "Animal Mode")
                    else:
                        self.equalized_spectrogram_viewer.update_spectrogram(chunk, mode = "Uniform Mode")
                    
                else:
                    chunk_equalized = self.equalized_signal[
                        self.index : self.index + self.chunk_size
                    ]
                    time_chunk_equalized = np.arange(self.index, self.index + self.chunk_size) / self.fs
                    self.cumulative_equalized_time.extend(time_chunk_equalized)
                    self.cumulative_equalized_data.extend(chunk_equalized)

                    # Plot cumulative equalized signal
                    self.ui.equalized_graphics_view.plot(
                        self.cumulative_equalized_time, self.cumulative_equalized_data, clear=True
                    )

                    if mode == "Musical Mode":
                        self.equalized_spectrogram_viewer.update_spectrogram(chunk_equalized, mode = "Musical Mode")
                    elif mode == "Animal Mode":
                        self.equalized_spectrogram_viewer.update_spectrogram(chunk_equalized, mode = "Animal Mode")
                    else:
                        self.equalized_spectrogram_viewer.update_spectrogram(chunk_equalized, mode = "Uniform Mode")

                    # if self.play_equalized_audio:
                    #     # self.c += 1
                    #     self.audio_file = f"temp_audio{chunk_equalized}.wav"
                    #     # if chunk_equalized != 1:#
                    #     #     os.remove(f"temp_audio{chunk_equalized-1}.wav")

                    #     # real_signal = np.real(self.time_domain_signal_modified)
                    #     sf.write(self.audio_file, chunk_equalized.astype(np.int16).tobytes(), self.fs)
                    #     self.player.pause()
                # if self.play_audio:
                #     self.player.play()
                    # self.stream.write(chunk.astype(np.int16).tobytes())
                if self.play_equalized_audio or self.play_audio:
                    if self.player.state() != QMediaPlayer.PlayingState:
                        self.player.play()
                else:
                    self.player.pause() 
                            
                self.index += self.chunk_size

        else:
            # Stop the timer and audio stream when the end of the file is reached
            self.timer.stop()
            if self.play_equalized_audio or self.play_audio:
                self.player.stop()
            # if mode == "Musical Mode" or mode == "Uniform Mode" or mode == "Animal Mode":
            #     self.stream.stop_stream()
            #     self.stream.close()
            #     self.audio_stream.terminate()
                

    def update_instrument(self, instrument):
        if not self.data.any():
            return
        self.equalized_signal = np.zeros_like(self.data, dtype=np.float32)
        if instrument=="Guitar":
            print("Guitar")
        elif instrument=="Violin":
            print("Violin")
        elif instrument=="Drums":
            print("Drums")
        elif instrument=="Saxophone":
            print("Saxophone")

        # Sum up the filtered signals with their respective slider values
        for inst, _ in self.instruments.items():
            print(self.sliders[inst].value())
            instrument_slider_value = self.sliders[inst].value() / 100
            self.equalized_signal += instrument_slider_value * self.filtered_data[inst]

        self.state = True
        self.plot_frequency_graph()

    def update_animal(self, animal):
        if not self.data.any():
            return
        slider_value = self.animal_sliders[animal].value() / 100
        self.equalized_signal = np.zeros_like(self.data, dtype=np.float32)
        
        for Animal, _ in self.animal_ranges.items():
            print(self.animal_sliders[Animal].value())
            animal_slider_value = self.animal_sliders[Animal].value() / 100
            self.equalized_signal += animal_slider_value * self.filtered_data[Animal]

        self.state = True
        self.plot_frequency_graph()

    def control_sound(self, btn):
        if not self.data.any():
            return
        if btn == "equalized_btn":
            self.play_equalized_audio = not self.play_equalized_audio
            self.play_audio = False
            print(self.audio_file)
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(self.audio_file)))

        else:
            self.play_audio = not self.play_audio
            self.play_equalized_audio = False
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(self.file_name)))


    def update_ecg_slider(self):
        if not self.data.any():
            return
        slider_values = {
            "vf": self.ecg_sliders["vf"].value() / 100,  # normalized scale [0, 2]
            "mi": self.ecg_sliders["mi"].value() / 100,    
            "sr": self.ecg_sliders["sr"].value() / 100,    
        }

        equalized_signal_base = self.data.astype(np.float32)
        self.equalized_signal = equalized_signal_base.copy() 
    
        # Plot the updated equalized signal
        for key, value in slider_values.items():
            if key in self.filtered_data:
                # Calculate the change factor for increasing or decreasing effect
                change_effect = value * (self.filtered_data[key].astype(np.float32) - equalized_signal_base)
                # Blend this change to the equalized signal
                self.equalized_signal += change_effect

        # If all sliders are zero, reset the equalized graph to the original signal
        if all(value == 0 for value in slider_values.values()):
            self.equalized_signal = equalized_signal_base

        # Get y-axis limits from the original graph
        original_plot_item = self.ui.original_graphics_view.getPlotItem()
        original_y_min, original_y_max = original_plot_item.viewRange()[1]

        # Plot the updated equalized signal with the same y-axis limits as the original graph
        equalized_plot_item = self.ui.equalized_graphics_view.getPlotItem()
        self.ui.equalized_graphics_view.plot(self.equalized_signal[:2000], clear=True)
        self.equalized_spectrogram_viewer.update_spectrogram(self.equalized_signal[:2000], mode="ECG Mode")

        # Set the y-axis range for the equalized graph
        equalized_plot_item.setYRange(original_y_min, original_y_max)

        self.plot_frequency_graph()

    def update_uniform_slider(self):
        if not self.data.any():
            return
        sender_slider = self.sender()
        slider_value = sender_slider.value()
        print(sender_slider)
        print("value: ", slider_value)
        self.equalized_signal = np.zeros_like(self.data, dtype=np.float32)
        # Sum up the filtered signals with their respective slider values
        for slider_number, slider in self.uniform_sliders.items():
            slider_value = slider.value() / 100
            self.equalized_signal += slider_value * self.filtered_data[slider_number]
        self.state = True
        self.plot_frequency_graph()

    
    def calculate_initial_fft(self):
        mode = self.ui.mode_comboBox.currentText()
        if mode == "ECG Mode":
            sampling_rate = 500
        else:
            sampling_rate = 44100    
        dt = 1 / sampling_rate

        # perform FFT, get frequencies and magnitudes
        fft_result = np.fft.fft(self.equalized_signal)
        frequencies = np.fft.fftfreq(len(fft_result), dt)
        fft_magnitude = np.abs(fft_result)
        self.phases = np.angle(fft_result)

        # take the positive half of frequencies and magnitudes
        self.positive_freqs = frequencies[: len(frequencies) // 2 ]
        self.original_magnitude = fft_magnitude[: len(fft_result) // 2]
        # normalize the magnitude
        self.original_magnitude = self.original_magnitude / np.max(self.original_magnitude)

    
    def plot_frequency_graph(self):
        if not self.data.any():
            return
        self.magnitude = self.original_magnitude.copy()
        self.positive_magnitude = np.zeros_like(self.magnitude)
        
        mode = self.ui.mode_comboBox.currentText()
        if mode == "Uniform Mode":
            self.ui.frequency_graphics_view.setLimits(xMin=1050, xMax=2100)
            mode_sliders = self.uniform_sliders
            mode_ranges = self.uniform_ranges

        elif mode == "Musical Mode":
            self.ui.frequency_graphics_view.setLimits(xMin=80, xMax=7999)
            mode_sliders = self.sliders
            mode_ranges = self.instruments

        elif mode == "ECG Mode":
            self.ui.frequency_graphics_view.setLimits(xMin=0, xMax=50, yMin=0, yMax=1)
            mode_sliders = self.ecg_sliders
            mode_ranges = self.ecg_ranges  
            
        elif mode == "Animal Mode":
            self.ui.frequency_graphics_view.setLimits(xMin = 0, xMax = 5000) 
            mode_sliders = self.animal_sliders
            mode_ranges = self.animal_ranges

        for slider_number, slider in mode_sliders.items():
            slider_value = slider.value() / 100
            low, high = mode_ranges[slider_number]

            if mode == "Musical Mode":
                low /= 2
                high /= 2

            # find indices corresponding to this slider's range
            indices_in_range = np.where((self.positive_freqs >= low) & (self.positive_freqs < high))[0]

            # apply maximum of the current value and the slider adjusted magnitude
            self.positive_magnitude[indices_in_range] = np.maximum(
                self.positive_magnitude[indices_in_range],
                self.magnitude[indices_in_range] * slider_value
            )

        # make them 1D array
        frequencies_array = np.ravel(np.array(self.positive_freqs))
        magnitude_array = np.ravel(np.array(self.positive_magnitude))

        # trim the arrays to be the same length
        min_length = min(len(frequencies_array), len(magnitude_array))
        frequencies_array = frequencies_array[:min_length]
        magnitude_array = magnitude_array[:min_length]

        # frequency graph limits
        self.ui.frequency_graphics_view.setLimits(yMin = np.min(magnitude_array), yMax = 2.2)
                
        # clear the previous graph and plot updated graph
        self.ui.frequency_graphics_view.clear()
        # self.ui.frequency_graphics_view.plot(frequencies_array, magnitude_array)
        # Plot in linear scale by default
        if not self.is_audiogram:
            self.ui.frequency_graphics_view.plot(frequencies_array, magnitude_array)
        
        
        self.phases = np.ravel(np.array(self.phases))
        self.phases = self.phases[:min_length]

        # Apply scaling to magnitude_array
        # magnitude_array *= 100  # Multiply each element by 100

        # Check the magnitude before inverse FFT
        print(np.max(np.abs(magnitude_array)))  # Check if the magnitude is too small or too large

        # Inverse Fourier transform
        self.time_domain_signal_modified = np.fft.ifft(magnitude_array * np.exp(1j * self.phases))

        # Take real part of the signal
        real_signal = np.real(self.time_domain_signal_modified)

        # Normalize the signal if necessary to prevent clipping
        real_signal /= np.max(np.abs(real_signal))  # Normalize between -1 and 1

        # Debugging: Check real_signal properties
        print(f"Max value of real_signal: {np.max(np.abs(real_signal))}")
        if np.max(np.abs(real_signal)) == 0:
            print("Warning: Signal is empty or contains only zeros.")

        # Handle the previous file safely
        previous_audio_file = f"temp_audio{self.c-1}.wav"
        if os.path.exists(previous_audio_file):
            print(f"Removing existing file: {previous_audio_file}")
            os.remove(previous_audio_file)

        # Create a temporary file for the output
        self.audio_file = tempfile.mktemp(suffix=".wav")

        # Debug output
        print(f"Writing to file: {self.audio_file}")

        # Write the audio file
        try:
            sf.write(self.audio_file, real_signal.astype(np.float32), self.fs)
            print(f"Audio file written successfully: {self.audio_file}")
        except Exception as e:
            print(f"Error writing audio file: {e}")

        # Optionally, check the written file
        try:
            loaded_signal, _ = sf.read(self.audio_file)
            print(f"Loaded signal max value: {np.max(np.abs(loaded_signal))}")
        except Exception as e:
            print(f"Error reading audio file after write: {e}")

        # Play audio if required
        if self.play_equalized_audio:
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(self.audio_file)))
            # self.player.play()

        else:
            # Use the audiogram scale (logarithmic) if toggled
            self.plot_audiogram_scale(frequencies_array, magnitude_array)


    def plot_audiogram_scale(self, frequencies, magnitudes):
        """
        Plots frequencies on an audiogram scale (logarithmic) for better analysis.
        """
        # Apply logarithmic scale for frequencies
        log_frequencies = np.log10(frequencies + 1)  # Adding 1 to avoid log(0)
        
        # Plot the audiogram-scaled graph
        self.ui.frequency_graphics_view.plot(log_frequencies, magnitudes)


if __name__ == "__main__":
    app = QApplication([])
    ui = Equilizer()
    ui.showMaximized()
    app.exec_()
