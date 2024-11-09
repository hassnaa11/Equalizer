from gui1 import Ui_MainWindow
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg
import sys
from pathlib import Path
import numpy as np



class Equilizer(QMainWindow):
   def __init__(self):
       super().__init__()
       self.ui = Ui_MainWindow()
       self.ui.setupUi(self)
       self.ecg_mode_selected = False
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
        self.ui.piano_slider: "piano",
        self.ui.xylophone_slider: "xylophone",
        self.ui.flute_slider: "flute",
        self.ui.chimes_slider: "chimes"
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
            self.ui.original_signal_viewer.xRange = [0, 1e3]
            self.ui.original_signal_viewer.yRange = [-2, 2]
            self.ui.equalized_signal_viewer.xRange = [0, 1e3]
            self.ui.equalized_signal_viewer.yRange = [-2, 2]
        else:
            self.ecg_mode_selected = False


if __name__ == "__main__":
    app = QApplication([])
    ui = Equilizer()
    ui.show()
    app.exec_()        