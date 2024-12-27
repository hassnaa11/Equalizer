from gui1 import Ui_MainWindow
from weiner_filter import WeinerFilter
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
from Spectrogram import SpectrogramViewer
import scipy.signal
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl
import numpy as np, bisect, librosa, soundfile as sf
import os
import tempfile
from scipy.io import wavfile
temp_audio_file = tempfile.mktemp(suffix=".wav")
# self.audio_file = tempfile.mktemp(suffix=".wav")
from scipy.signal import resample

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
        self.ui.mode_comboBox.currentTextChanged.connect(self.on_mode_change)
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
        self.is_timer_running = True
        self.audio_stream = None
        self.player = QMediaPlayer()
        self.play_equalized_audio = False
        self.play_audio = False
        self.data = np.array([])  # Holds the audio data
        self.index = 0
        self.chunk_size = 3000
        self.ui.pushButton_12.setIcon(QIcon(f'icons/icons/frog2.png'))

        self.ui.frog_slider.valueChanged.connect( lambda: self.update_instrument("frog"))
        self.ui.Saxophone_slider.valueChanged.connect(lambda: self.update_instrument("Saxophone"))
        self.ui.Violin_slider.valueChanged.connect(lambda: self.update_instrument("E"))
        self.ui.guitar_slider.valueChanged.connect(lambda: self.update_instrument("A"))
        self.ui.new_slider.valueChanged.connect(lambda: self.update_instrument("O"))

        self.ui.open_btn.clicked.connect(self.open_file)
        self.ui.original_sound_btn.clicked.connect(lambda: self.control_sound("original_btn"))
        self.ui.equalized_sound_btn.clicked.connect(lambda: self.control_sound("equalized_btn"))

        self.sliders = {
            "frog": self.ui.frog_slider,
            "Saxophone": self.ui.Saxophone_slider,
            "A": self.ui.guitar_slider,
            "E": self.ui.Violin_slider,
            "O": self.ui.new_slider,
        }
        self.instruments = {
            "frog": [(250,650)],
            "Saxophone": [(3000, 6000)], 
            "O": [(0, 250)],
            "A": [(650, 2200)],
            "E": [(0,250),(650,2200)],     
        }
       
        # animal mode
        self.animal_sliders = {
            "Cymbals": self.ui.Guitar_slider,
            # "Cow": self.ui.extra_slider,
            "frog": self.ui.frog_slider,
            "horse": self.ui.extra2_slider,
            "flute": self.ui.flute_slider,
            # "zebra": self.ui.extra3_slider,
            "dog": self.ui.dog_slider,
            "elephant": self.ui.extra4_slider,
            "cricket": self.ui.cricket_slider,
        }
        self.animal_ranges = { 
            "dog":[(0, 300)],
            # "Cow": [(250, 350)], 
            "flute": [(650,900)],
            "horse": [(900, 1500)],
            "Cymbals":[(1500, 2700)],
            # "zebra": [(1200, 1500)],
            "frog": [(300, 650)], 
            "elephant": [(2700, 4500)],
            "cricket": [(4500, 18500)], 
               
            
}

        self.ui.pushButton_5.setIcon(QIcon(f'icons/icons/frog-.png'))
        self.ui.pushButton_6.setIcon(QIcon(f'icons/icons/flute.png'))
        self.ui.pushButton_7.setIcon(QIcon(f'icons/icons/cricket.png'))
        self.ui.pushButton_2.setIcon(QIcon(f'icons/icons/cymbals3.png'))
        self.ui.pushButton.setIcon(QIcon(f'icons/icons/dog.png'))

        self.ui.cricket_slider.valueChanged.connect(lambda: self.update_animal("cricket"))
        self.ui.flute_slider.valueChanged.connect(lambda: self.update_animal("flute"))
        self.ui.frog_slider.valueChanged.connect(lambda: self.update_animal("frog"))
        self.ui.Guitar_slider.valueChanged.connect(lambda: self.update_animal("Cymbals"))
        self.ui.dog_slider.valueChanged.connect(lambda: self.update_animal("dog"))
        
        self.ui.cricket_slider.setValue(100)
        self.ui.flute_slider.setValue(100)
        self.ui.frog_slider.setValue(100)
        self.ui.Guitar_slider.setValue(100)
        self.ui.dog_slider.setValue(100)
        # self.ui.extra_slider.setValue(0)
        # self.ui.extra2_slider.setValue(0)
        # self.ui.extra3_slider.setValue(0)
        # self.ui.extra4_slider.setValue(0)
        
        
        #####animal divisions#####
        self.animal_slicers = {
            "Cymbals": self.ui.pushButton_2,
            "frog": self.ui.pushButton_5,
            "flute": self.ui.pushButton_7,
            "dog": self.ui.pushButton,
            "cricket": self.ui.pushButton_9,
        }
        
        
        
        
        # end of animal mode

        self.sliders_frames = {
            "Uniform Mode": self.ui.uniform_sliders_frame,
            "Animal Mode": self.ui.animals_sliders_frame,
            "Musical Mode": self.ui.music_sliders_frame,
            "Weiner Filter": self.ui.ecg_sliders_frame,
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
        self.isreplayed = False
        
        # Weiner Filter 
        self.weiner = WeinerFilter()
        self.rect_roi = pg.RectROI([0, -0.25], [0.2, 1.4], pen='r')
        self.rect_roi.addScaleHandle([1, 0.5], [0.5, 0.5]) 
        self.selected_range = None 
        self.ui.select_btn.clicked.connect(self.select_signal_to_filter)
        self.done_selection = False
        self.ui.select_btn.hide()
        self.ui.done_select_btn.hide() 
        self.is_stopped = False 


    def select_signal_to_filter(self):
        if not self.data.any():
            return
        if self.rect_roi in self.ui.original_graphics_view.items():
            self.ui.original_graphics_view.removeItem(self.rect_roi)
        self.rect_roi = pg.RectROI([0, -20000], [0.2, 30000], pen='r')
        self.rect_roi.setSize([0.2, 30000])
        self.ui.original_graphics_view.addItem(self.rect_roi)
        self.ui.done_select_btn.clicked.connect(self.on_select)
        
    
    def on_select(self):
        pos = self.rect_roi.pos() 
        size = self.rect_roi.size()
        left = pos.x() 
        right = pos.x() + size[0] 
        top = pos.y() + size[1]   
        bottom = pos.y() 
        print(f"Rectangle bounds - Left: {left}, Right: {right}, Top: {top}, Bottom: {bottom}")
        
        x_data = self.cumulative_time  
        y_data = self.data  
        left_idx = 0
        right_idx = 0

        for i, x in enumerate(x_data):
            if x >= left:  
                left_idx = i
                break  

        for i, x in enumerate(x_data):
            if x >= right: 
                right_idx = i
                break  

        right_idx = max(right_idx, left_idx + 1)

        selected_x = x_data[left_idx:right_idx+1]
        selected_y = y_data[left_idx:right_idx+1]

        print(f"Selected x data: {selected_x[:5]}") 
        print(f"Selected y data: {selected_y[:5]}")
        self.save_selected_signal(selected_y)

        self.selected_range = (left, right, top, bottom)
        print(f"Selected range: {self.selected_range}")
        
        
    def save_selected_signal(self,selected_y):
        # normalize the selected_y to fit in the range of int16 (standard for .wav files)
        selected_y_normalized = np.int16(selected_y / np.max(np.abs(selected_y)) * 32767)
        
        wavfile.write('selected_signal.wav', self.fs, selected_y_normalized)
        self.done_selection = True
        
        fs, self.data = wavfile.read(self.file_name)
        fs, noise_signal = wavfile.read('selected_signal.wav')    
        
        # Ensure signals are mono
        if self.data.ndim > 1:
            self.data = self.data[:, 0]
        if noise_signal.ndim > 1:
            noise_signal = noise_signal[:, 0]
        self.audio_file, self.equalized_signal = self.weiner.apply_wiener_filter(self.data, noise_signal, fs)
        print(self.equalized_signal) 
        self.ui.equalized_graphics_view.clear()
        if os.path.exists(self.audio_file):
            print(f"Denoised signal saved at: {self.audio_file}")

        if self.play_equalized_audio:
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(self.audio_file)))
            
        self.equalized_spectrogram_viewer.update_spectrogram(self.equalized_signal[:2000], mode="Weiner Filter")    
                        

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
        self.is_stopped = True
        mode = self.ui.mode_comboBox.currentText()
        if mode == "Weiner Filter":
            self.ui.select_btn.show()
            self.ui.done_select_btn.show() 
        else:
            self.ui.select_btn.hide()
            self.ui.done_select_btn.hide() 
        # self.stream.close()
        self.timer.stop()
        self.data = None
        # self.audio_stream.terminate()
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
        self.equalized_signal = None
        self.reset_sliders()
           

    def adjust_playback_speed(self):
        speed = self.ui.speed_slider.value()
        base_interval = 50  
        self.timer.setInterval(base_interval // speed)  
        self.player.setPlaybackRate(speed)  
        print(f"Playback speed set to {speed}x, Timer interval: {self.timer.interval()} ms, Audio playback rate: {self.player.playbackRate()}x")



    def toggle_scale(self):
        """
        Toggle between linear and audiogram scales.
        """
        self.is_audiogram = not self.is_audiogram
        if self.is_audiogram:
           
            self.ui.reset_view_btn.setText("Linear")  
        else:
            
            self.ui.reset_view_btn.setText("Audiogram")  
        
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
        # if not self.data.any():
        #     return
        self.stop()
        

    def play_pause(self):
        if self.is_timer_running:
            print("stopp")
            self.ui.play_pause_btn.setIcon(QIcon(f'icons/icons/play copy.svg'))
            self.player.pause()
            self.timer.stop()
            
        else:
            print("runn")
            self.ui.play_pause_btn.setIcon(QIcon(f'icons/icons/pause copy.svg'))
            self.timer.start()
            # self.player.play()
        self.is_timer_running = not self.is_timer_running
    
        # self.play_audio = not self.play_audio
        # self.play_equalized_audio = not self.play_equalized_audio

    def replay(self):
        self.ui.original_graphics_view.clear()
        self.ui.equalized_graphics_view.clear()
        self.isreplayed = True
        self.is_timer_running = False
        self.index = 0
        self.cumulative_equalized_time = []  
        self.cumulative_equalized_data = [] 
        self.player.stop()
        # self.play_audio = False
        # self.play_equalized_audio = False
        # self.on_mode_change()
        if self.file_name:
            self.timer.stop()   
            self.is_timer_running = False 
            self.plot_original_data()
            self.index = 0
            self.state = False
            self.timer.start()  
            self.is_timer_running = True 
        self.ui.play_pause_btn.setIcon(QIcon(f'icons/icons/pause copy.svg'))
        # self.reset_sliders()    
        self.state = True
        self.plot_frequency_graph() 
        
         
    def reset_sliders(self):
        #animal mode
        self.ui.cricket_slider.setValue(100)
        self.ui.flute_slider.setValue(100)
        self.ui.frog_slider.setValue(100)
        self.ui.Guitar_slider.setValue(100)
        self.ui.dog_slider.setValue(100)
        # self.ui.extra_slider.setValue(0)
        # self.ui.extra2_slider.setValue(0)
        # self.ui.extra3_slider.setValue(0)
        # self.ui.extra4_slider.setValue(0)

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
        self.ui.frog_slider.setValue(100)
        self.ui.Violin_slider.setValue(100)
        self.ui.guitar_slider.setValue(100)
        self.ui.Saxophone_slider.setValue(100)
        self.ui.new_slider.setValue(100)



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
        if text == "Weiner Filter":
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
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(self.file_name)))
            self.timer.start()
            print(self.file_name)
            self.ui.play_pause_btn.setIcon(QIcon(f'icons/icons/pause copy.svg'))

             
    def plot_original_data(self):
        self.fs, self.data = wav.read(self.file_name)  
        if self.data.ndim > 1:
            self.data = self.data.flatten() 
        self.data = self.data.astype(np.float32)  # Ensure data is in float32 for consistency
        print(f"Sample rate of the file: {self.fs}")
        self.cumulative_time = []  # Reset cumulative time
        self.cumulative_data = []  # Reset cumulative data

        chunk = self.data[: self.chunk_size]
        time_chunk = np.arange(0, len(chunk)) / self.fs

        if len(chunk) != len(time_chunk):
            print("Mismatch in chunk lengths")
            return

        self.cumulative_time.extend(time_chunk)
        self.cumulative_data.extend(chunk)

        self.ui.original_graphics_view.plot(self.cumulative_time, self.cumulative_data, clear=True)
        self.cumulative_equalized_time = []  # To store time values for the equalized signal
        self.cumulative_equalized_data = []  # To store equalized signal values

        mode = self.ui.mode_comboBox.currentText()

        if not self.isreplayed:
            self.equalized_signal = self.data
        if self.is_stopped:
            self.is_stopped = False
            self.equalized_signal = self.data    
            
        self.ui.equalized_graphics_view.plot(self.data[: self.chunk_size], clear=True)
        
        self.calculate_initial_fft()
        self.plot_frequency_graph()
        if len(self.data.shape) > 1:
            self.data = self.data[:, 0]
    
        self.original_spectrogram_viewer.update_spectrogram(self.data[: self.chunk_size], mode = mode)
        if mode != "Weiner Filter":
            self.equalized_spectrogram_viewer.update_spectrogram(self.data[: self.chunk_size], mode = mode)

        self.filtered_data = {}
        if mode == "Musical Mode":
            for instrument, ranges in self.instruments.items():
                self.filtered_data[instrument] = np.zeros_like(self.data, dtype=np.float32)
                for low, high in ranges:
                    self.filtered_data[instrument] += bandpass_filter(self.data, low, high, self.fs).astype(np.float32)
                print(self.filtered_data)
            if not self.isreplayed:
                self.equalized_spectrogram_viewer.update_spectrogram(self.data, mode = "Musical Mode")

        elif mode == "Uniform Mode":
            for slider_number, (low, high) in self.uniform_ranges.items():
                self.filtered_data[slider_number] = bandpass_filter(
                    self.data, low, high, self.fs
                ).astype(np.float32)
                print(self.filtered_data)
            if not self.isreplayed:
                self.equalized_spectrogram_viewer.update_spectrogram(self.data, mode == "Uniform Mode")
        elif mode == "Animal Mode":
            for animal, ranges in self.animal_ranges.items():
                self.filtered_data[animal] = np.zeros_like(self.data, dtype=np.float32)
                for low, high in ranges:
                    self.filtered_data[animal] += bandpass_filter(self.data, low, high, self.fs).astype(np.float32)
                print(self.filtered_data)
              
            if not self.isreplayed:
                self.equalized_spectrogram_viewer.update_spectrogram(self.data, mode == "Animal Mode")
        


    def update_plot(self):
        if not self.data.any():
            return
      
        mode = self.ui.mode_comboBox.currentText()
        chunk = self.data[self.index : self.index + self.chunk_size]
        time_chunk = np.arange(self.index, self.index + self.chunk_size) / self.fs

        # Append new chunk to cumulative data
        self.cumulative_time.extend(time_chunk)
        self.cumulative_data.extend(chunk)

        # if mode == "Weiner Filter":
        #     return

        if self.index + self.chunk_size <= len(self.data):
            # Get the next chunk of the original data
            chunk = self.data[self.index : self.index + self.chunk_size]

            # if mode == "Musical Mode":
            #     self.original_spectrogram_viewer.update_spectrogram(chunk, mode = "Musical Mode")
            # else:
            #     self.original_spectrogram_viewer.update_spectrogram(chunk, mode = "Uniform Mode")

                # Update plot with cumulative data
            x_range_start = max(0, self.cumulative_time[-1] - 0.5) 
            x_range_end = self.cumulative_time[-1]

            self.ui.original_graphics_view.plot(
                self.cumulative_time, self.cumulative_data, clear=True
            )
            self.ui.original_graphics_view.setXRange(x_range_start, x_range_end)  # Set x-axis to scroll

            if self.state == False:
                self.ui.equalized_graphics_view.plot(
                    self.cumulative_time, self.cumulative_data, clear=True
                )
                self.ui.equalized_graphics_view.setXRange(x_range_start, x_range_end)  # Set x-axis to scroll

                # if mode == "Musical Mode":
                #     self.equalized_spectrogram_viewer.update_spectrogram(chunk, mode="Musical Mode")
                # elif mode == "Animal Mode":
                #     self.equalized_spectrogram_viewer.update_spectrogram(chunk, mode="Animal Mode")
                # else:
                #     self.equalized_spectrogram_viewer.update_spectrogram(chunk, mode="Uniform Mode")

            else:
                # Ensure no overflow when slicing
                if self.index + self.chunk_size > len(self.equalized_signal):
                    self.chunk_size = len(self.equalized_signal) - self.index
                
                # Extract chunks
                chunk_equalized = self.equalized_signal[self.index : self.index + self.chunk_size]
                time_chunk_equalized = np.arange(self.index, self.index + self.chunk_size) / self.fs

                # Check if time and signal chunk lengths match
                if len(chunk_equalized) != len(time_chunk_equalized):
                    raise ValueError(
                        f"Mismatch in chunk sizes: Data={len(chunk_equalized)}, Time={len(time_chunk_equalized)}"
                    )
                
                # Update cumulative arrays
                self.cumulative_equalized_time.extend(time_chunk_equalized)
                self.cumulative_equalized_data.extend(chunk_equalized)

                # Ensure cumulative arrays are of the same length
                if len(self.cumulative_equalized_time) != len(self.cumulative_equalized_data):
                    raise ValueError(
                        f"Mismatch in cumulative sizes: Time={len(self.cumulative_equalized_time)}, Data={len(self.cumulative_equalized_data)}"
                    )

                # Plot the updated data
                self.ui.equalized_graphics_view.plot(
                    self.cumulative_equalized_time, self.cumulative_equalized_data, clear=True
                )
                
                # Update index for the next chunk
                # chunk_equalized = self.equalized_signal[
                #     self.index : self.index + self.chunk_size
                # ]
                # time_chunk_equalized = np.arange(self.index, self.index + self.chunk_size) / self.fs
                # self.cumulative_equalized_time.extend(time_chunk_equalized)
                # self.cumulative_equalized_data.extend(chunk_equalized)

                # self.ui.equalized_graphics_view.plot(
                #     self.cumulative_equalized_time, self.cumulative_equalized_data, clear=True
                # )
                self.ui.equalized_graphics_view.setXRange(x_range_start, x_range_end)  # Set x-axis to scroll


                # if mode == "Musical Mode":
                #     self.equalized_spectrogram_viewer.update_spectrogram(chunk_equalized, mode = "Musical Mode")
                # elif mode == "Animal Mode":
                #     self.equalized_spectrogram_viewer.update_spectrogram(chunk_equalized, mode = "Animal Mode")
                # else:
                #     self.equalized_spectrogram_viewer.update_spectrogram(chunk_equalized, mode = "Uniform Mode")

            if self.play_equalized_audio or self.play_audio:
                if self.player.state() != QMediaPlayer.PlayingState:
                    self.player.play()
            else:
                self.player.pause() 
                        
            self.index += self.chunk_size

        else:
            self.timer.stop()
            # if self.play_equalized_audio or self.play_audio:
            #     self.player.stop()
            self.replay()    
            # if mode == "Musical Mode" or mode == "Uniform Mode" or mode == "Animal Mode":
            #     self.stream.stop_stream()
            #     self.stream.close()
            #     self.audio_stream.terminate()
                

    def update_instrument(self, instrument):
        if not self.data.any():
            return
        self.equalized_signal = np.zeros_like(self.data, dtype=np.float32)
        if instrument=="frog":
            print("frog")
        elif instrument=="Saxophone":
            print("Saxophone")
        elif instrument=="E":
            print("E")
        elif instrument=="A":
            print("A")
        elif instrument=="O":
            print("O")
        
        for inst, ranges in self.instruments.items():
            instrument_slider_value = self.sliders[inst].value() / 100

            # Handle multiple ranges for an instrument
            for low, high in ranges:
                filtered_signal = bandpass_filter(self.data, low, high, self.fs)
                self.equalized_signal += instrument_slider_value * filtered_signal


        # for inst, ranges in self.instruments.items():
        #     print(self.sliders[inst].value())
        #     instrument_slider_value = self.sliders[inst].value() / 100
            
        #     self.equalized_signal += instrument_slider_value * self.filtered_data[inst]

        self.state = True
        self.plot_frequency_graph()
        self.equalized_spectrogram_viewer.update_spectrogram(self.equalized_signal, mode="Musical Mode")

    # def update_animal(self, animal):
    #     if not self.data.any():
    #         return
    #     self.equalized_signal = np.zeros_like(self.data, dtype=np.float64)
        
    #     for Animal, _ in self.animal_ranges.items():
    #         print(self.animal_sliders[Animal].value())
    #         animal_slider_value = self.animal_sliders[Animal].value() / 100
    #         self.equalized_signal += animal_slider_value * self.filtered_data[Animal]
        
        

    #     self.state = True
    #     self.plot_frequency_graph()
    #     self.equalized_spectrogram_viewer.update_spectrogram(self.equalized_signal,mode="Animal Mode")
    
    def update_animal(self, animal):
        if not self.data.any():
            return
        self.equalized_signal = np.zeros_like(self.data, dtype=np.float32)
        
        for Animal, ranges in self.animal_ranges.items():
            animal_slider_value = self.animal_sliders[Animal].value() / 100
            print(animal_slider_value)

            
            for low, high in ranges:
                filtered_signal = bandpass_filter(self.data, low, high, self.fs)
                self.equalized_signal += animal_slider_value * filtered_signal

            

        self.state = True
        self.plot_frequency_graph()
        self.equalized_spectrogram_viewer.update_spectrogram(self.equalized_signal, mode="Animal Mode")

    
    # def update_animal(self, animal):
    #     if not self.data.any():
    #         return
        
    #     slider_value = self.animal_sliders[animal].value() / 100
    #     self.equalized_signal = np.zeros_like(self.data, dtype=np.float32)

    #     # This will store the most recent (lowest) value for each frequency range
    #     applied_values = {}

    #     for Animal, _ in self.animal_ranges.items():
    #         print(self.animal_sliders[Animal].value())
    #         animal_slider_value = self.animal_sliders[Animal].value() / 100

    #         # Determine the overlapping frequency ranges
    #         animal_range = self.animal_ranges[Animal]
    #         current_range = self.animal_ranges[animal]
            
    #         # Check if there is an overlap between current animal range and any other range
    #         overlap_found = False
    #         for freq in range(animal_range[0], animal_range[1]):
    #             if freq >= current_range[0] and freq <= current_range[1]:
    #                 overlap_found = True
    #                 break
            
    #         # If there is overlap, choose the lower slider value for the frequency range
    #         if overlap_found:
    #             # Apply the lower slider value for the overlapping frequency
    #             applied_values[animal_range] = min(applied_values.get(animal_range, float('inf')), animal_slider_value)
    #         else:
    #             # Apply the slider value normally if there's no overlap
    #             applied_values[animal_range] = animal_slider_value
            
    #         # Add the equalized signal for the current animal
    #         self.equalized_signal += applied_values[animal_range] * self.filtered_data[Animal]

    #     self.state = True
    #     self.plot_frequency_graph()
    #     self.equalized_spectrogram_viewer.update_spectrogram(self.equalized_signal, mode="Animal Mode")


    def control_sound(self, btn):
        if not self.data.any():
            return
        mode = self.ui.mode_comboBox.currentText()
        if btn == "equalized_btn":
            if self.done_selection == False and mode == "Weiner Filter":
                self.audio_file = self.file_name
            self.play_equalized_audio = not self.play_equalized_audio
            if self.play_equalized_audio:
                self.replay()
            self.play_audio = False
            print(self.audio_file)
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(self.audio_file)))

        else:
            self.play_audio = not self.play_audio
            if self.play_audio:
                self.replay()
            self.play_equalized_audio = False
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(self.file_name)))
            

    def update_uniform_slider(self):
        if not self.data.any():
            return
        sender_slider = self.sender()
        slider_value = sender_slider.value()
        print(sender_slider)
        print("value: ", slider_value)
        self.equalized_signal = np.zeros_like(self.data, dtype=np.float32)
        for slider_number, slider in self.uniform_sliders.items():
            slider_value = slider.value() / 100
            self.equalized_signal += slider_value * self.filtered_data[slider_number]
        self.state = True
        self.plot_frequency_graph()
        self.equalized_spectrogram_viewer.update_spectrogram(self.equalized_signal,mode="Uniform Mode")

    
    def calculate_initial_fft(self):
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
        if mode == "Musical Mode":
            self.ui.frequency_graphics_view.setLimits(xMin=0, xMax=8000)
            mode_sliders = self.sliders
            mode_ranges = self.instruments

            for slider_number, slider in mode_sliders.items():
                slider_value = slider.value() / 100
                ranges = mode_ranges[slider_number]

                # Handle multiple ranges
                for low, high in ranges:
                    # Find indices corresponding to this slider's range
                    indices_in_range = np.where((self.positive_freqs >= low) & (self.positive_freqs < high))[0]

                    # Apply maximum of the current value and the slider-adjusted magnitude
                    self.positive_magnitude[indices_in_range] = np.maximum(
                        self.positive_magnitude[indices_in_range],
                        self.magnitude[indices_in_range] * slider_value
                    )
        elif mode == "Animal Mode":
                self.ui.frequency_graphics_view.setLimits(xMin=0, xMax=18500)
                mode_sliders = self.animal_sliders
                mode_ranges = self.animal_ranges
                
                for slider_number, slider in mode_sliders.items():
                    slider_value = slider.value() / 100
                    ranges = mode_ranges[slider_number]

                
                    for low, high in ranges:
                    # Find indices corresponding to this slider's range
                        indices_in_range = np.where((self.positive_freqs >= low) & (self.positive_freqs < high))[0]

                        # Apply maximum of the current value and the slider-adjusted magnitude
                        self.positive_magnitude[indices_in_range] = np.maximum(
                            self.positive_magnitude[indices_in_range],
                            self.magnitude[indices_in_range] * slider_value
                        )

        else:
            # Logic for other modes remains unchanged
            if mode == "Uniform Mode":
                self.ui.frequency_graphics_view.setLimits(xMin=1050, xMax=2100)
                mode_sliders = self.uniform_sliders
                mode_ranges = self.uniform_ranges

            elif mode == "Weiner Filter":
                self.ui.frequency_graphics_view.setLimits(xMin=0, xMax=8000, yMin=np.min(self.original_magnitude),
                                                          yMax=np.max(self.original_magnitude))
                self.ui.frequency_graphics_view.clear()
                if self.is_audiogram:
                    self.plot_audiogram_scale(self.positive_freqs, self.original_magnitude)
                else:
                    self.ui.frequency_graphics_view.plot(self.positive_freqs, self.original_magnitude)
                return

            for slider_number, slider in mode_sliders.items():
                slider_value = slider.value() / 100
                low, high = mode_ranges[slider_number]

                # Find indices corresponding to this slider's range
                indices_in_range = np.where((self.positive_freqs >= low) & (self.positive_freqs < high))[0]

                # Apply maximum of the current value and the slider-adjusted magnitude
                self.positive_magnitude[indices_in_range] = np.maximum(
                    self.positive_magnitude[indices_in_range],
                    self.magnitude[indices_in_range] * slider_value
                )

        # Make them 1D arrays
        frequencies_array = np.ravel(np.array(self.positive_freqs))
        magnitude_array = np.ravel(np.array(self.positive_magnitude))

        # Trim the arrays to be the same length
        min_length = min(len(frequencies_array), len(magnitude_array))
        frequencies_array = frequencies_array[:min_length]
        magnitude_array = magnitude_array[:min_length]

        # Frequency graph limits
        self.ui.frequency_graphics_view.setLimits(yMin=np.min(magnitude_array), yMax=4.1)

        self.ui.frequency_graphics_view.clear()

        # Plot in linear scale by default
        if self.is_audiogram:
            self.plot_audiogram_scale(frequencies_array, magnitude_array)
        else:
            self.ui.frequency_graphics_view.plot(frequencies_array, magnitude_array)

        self.phases = np.ravel(np.array(self.phases))
        self.phases = self.phases[:min_length]

        # Inverse Fourier transform
        self.time_domain_signal_modified = np.fft.ifft(magnitude_array * np.exp(1j * self.phases))

        # Take real part of the signal
        real_signal = np.real(self.time_domain_signal_modified)

        real_signal /= np.max(np.abs(real_signal))

        # Handle the previous file safely
        previous_audio_file = f"temp_audio{self.c-1}.wav"
        if os.path.exists(previous_audio_file):
            print(f"Removing existing file: {previous_audio_file}")
            os.remove(previous_audio_file)

        # File for the equalized sound
        self.audio_file = tempfile.mktemp(suffix=".wav")

        # Write the audio file
        try:
            sf.write(self.audio_file, real_signal.astype(np.float32), self.fs)
            print(f"Audio file written successfully: {self.audio_file}")
        except Exception as e:
            print(f"Error writing audio file: {e}")

        try:
            loaded_signal, _ = sf.read(self.audio_file)
            print(f"Loaded signal max value: {np.max(np.abs(loaded_signal))}")
        except Exception as e:
            print(f"Error reading audio file after write: {e}")

        if self.play_equalized_audio:
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(self.audio_file)))


    def plot_audiogram_scale(self, frequencies, magnitudes):
        mode = self.ui.mode_comboBox.currentText()
        if len(frequencies) == 0 or len(magnitudes) == 0:
            print("No data to plot on audiogram scale.")
            return

        frequencies = np.maximum(frequencies, 1e-9)
        if mode == "Uniform Mode":
            self.ui.frequency_graphics_view.setLimits(xMin=3, xMax=3.4)
        elif mode == "Musical Mode":
            self.ui.frequency_graphics_view.setLimits(xMin=0, xMax=4.1)
        elif mode == "Animal Mode":
            self.ui.frequency_graphics_view.setLimits(xMin=0, xMax=4.3)
        else:
            self.ui.frequency_graphics_view.setLimits(xMin=0, xMax=2)

        log_frequencies = np.log10(frequencies)

        self.ui.frequency_graphics_view.plot(log_frequencies, magnitudes)



if __name__ == "__main__":
    app = QApplication([])
    ui = Equilizer()
    ui.showMaximized()
    app.exec_()
