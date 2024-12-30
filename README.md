# Signal Equalizer

## Introduction
Signal Equalizer is a desktop application designed for manipulating frequency components of signals. It has applications in music, speech processing, and biomedical fields, such as noise suppression or feature enhancement.

---

## Features
- **Uniform Range Mode**: Divides the signal's total frequency range into 10 equal sections, each controlled by a slider.
- **Animal Sounds & Musical Instruments Mode**: Sliders control magnitudes of specific instrument and animal sounds within a mixed signal.
- **Musical Instruments & Vowels Mode**: Sliders manipulate musical instruments and vowel components in an input audio signal.
- **Wiener Filter Mode**: Apply a Wiener filter for noise suppression or signal restoration.
- **Dual Linked Cine Viewers**: Linked input and output signal viewers, synchronized for time and zoom operations.
- **Spectrogram Display**: Shows spectrograms of the input and output signals, which dynamically update with slider adjustments.
- **Audiogram & Linear Scale Views**: Fourier transform graph supports linear and audiogram scaling, switchable in the UI.
- **Responsive User Interface**: Sliders and controls adjust seamlessly when switching modes.

---

## Modes
### 1. Uniform Range Mode
- Divides the frequency spectrum of the signal into 10 equal ranges.
- Each range is manipulated independently using a slider.

 ![](media/unifrom_mode.png)

### 2. Musical Instruments & Animal Sounds Mode
- Control both specific musical instrument and animal sound components in a composite audio signal.

 ![](media/animal_mode.png)

### 3. Musical Instruments & Vowels Mode
- Modify the magnitude of musical instruments and vowel sounds present in the signal.
- Each slider can correspond to multiple frequency windows.

![](media/music_mode.png)
 
### 4. Wiener Filter Mode
- Implement noise suppression or signal restoration.
- Select noisy segment from original signal then apply filter to remove noise.

![](media/wiener.png)
---

## Visualization
- **Linked Cine Viewers**: Simultaneously view input and output signals with play, pause, zoom, pan, and reset functionalities.
- **Dynamic Spectrograms**: Toggle spectrogram views for visualizing frequency magnitude changes.
- **Fourier Transform Graph**: Switch between linear and audiogram scales.

### DEMO

![](media/equilizer_demo.gif)

---

## How to Run
1. Clone this repository:
   ```bash
   git clone https://github.com/hassnaa11/Equalizer
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```

---

## Usage
1. Open a signal file.
2. Select a mode from the dropdown menu.
3. Use the sliders to adjust frequency components.
4. View changes in real-time through the cine viewers and spectrograms.

---

## Contributors

<table align="center" width="100%">
  <tr>
    <td align="center" width="20%">
      <a href="https://github.com/yasmine-msg79">
        <img src="https://github.com/yasmine-msg79.png?size=100" style="width:80%;" alt="yasmine-msg79"/>
      </a>
      <br />
      <a href="https://github.com/yasmine-msg79">yasmine Mahmoud</a>
    </td>
    <td align="center" width="20%">
      <a href="https://github.com/hassnaa11">
        <img src="https://github.com/hassnaa11.png?size=100" style="width:80%;" alt="hassnaa11"/>
      </a>
      <br />
      <a href="https://github.com/hassnaa11">hassnaa11</a>
    </td>
    <td align="center" width="20%">
      <a href="https://github.com/shahdragab89">
        <img src="https://github.com/shahdragab89.png?size=100" style="width:80%;" alt="shahdragab89"/>
      </a>
      <br />
      <a href="https://github.com/shahdragab89">shahdragab89</a>
    </td>
   <td align="center" width="20%">
      <a href="https://github.com/Emaaanabdelazeemm">
        <img src="https://github.com/Emaaanabdelazeemm.png?size=100" style="width:80%;" alt="Emaaanabdelazeemm"/>
      </a>
      <br />
      <a href="https://github.com/Emaaanabdelazeemm">Emaaanabdelazeemm</a>
    </td>
   <td align="center" width="20%">
      <a href="https://github.com/Ayat-Tarek">
        <img src="https://github.com/Ayat-Tarek.png?size=100" style="width:80%;" alt="Ayat-Tarek"/>
      </a>
      <br />
      <a href="https://github.com/Ayat-Tarek">Ayat Tarek</a>
    </td>
  </tr>
</table>




