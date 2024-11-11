# arrhythmia_handler.py

import numpy as np

def detect_arrhythmias(ecg_signal):
    """
    Detects the type of arrhythmia present in the given ECG signal.
    Types detected: Atrial Fibrillation, Myocardial Infarction, Sinus Rhythm.
    Returns a dictionary indicating detected types and their magnitudes.
    """
    detection_results = {
        'normal': False,
        'atrial_fibrillation': 0.0,
        'myocardial_infarction': 0.0,
        'sinus_rhythm': 0.0
    }
    
    if np.mean(ecg_signal) > 0.5:
        detection_results['atrial_fibrillation'] = 0.6
    if np.max(ecg_signal) > 1.0:
        detection_results['myocardial_infarction'] = 0.8
    if np.std(ecg_signal) < 0.3:
        detection_results['sinus_rhythm'] = 0.5
    else:
        detection_results['normal'] = True
    
    return detection_results

import numpy as np

def apply_slider_changes(ecg_signal, slider_values):
    """
    Modifies the ECG signal based on the slider values for different arrhythmias.
    """
    # Convert ecg_signal to float64 for precise manipulation
    modified_signal = np.array(ecg_signal, dtype=np.float64, copy=True)

    if slider_values['atrial_fibrillation'] > 0:
        noise = np.random.normal(loc=0, scale=slider_values['atrial_fibrillation'], size=len(ecg_signal))
        modified_signal += modified_signal * noise
        
    if slider_values['myocardial_infarction'] > 0:
        # Create a custom, non-periodic pattern for modification
        linear_inversion_pattern = np.linspace(1, -1, len(ecg_signal)) * slider_values['myocardial_infarction']
        modified_signal *= (1 + linear_inversion_pattern)
        
    # if slider_values['myocardial_infarction'] > 0:
    #     # Using a hyperbolic tangent modulation pattern for a smooth, wave-like effect
    #     modulation_pattern = 1 + slider_values['myocardial_infarction'] * np.tanh(np.linspace(-2, 2, len(ecg_signal)))
    #     modified_signal *= modulation_pattern

    # if slider_values['myocardial_infarction'] > 0:
    #     modified_signal *= slider_values['myocardial_infarction'] * np.cos(np.linspace(0, 5 * np.pi, len(ecg_signal)))

    if slider_values['sinus_rhythm'] > 0:
        small_random_variation = np.random.normal(0, 0.05, len(ecg_signal))
        modified_signal += small_random_variation * slider_values['sinus_rhythm']
    
    # Scale modified signal and convert back to int16 for further processing if needed
    modified_signal = np.clip(modified_signal, -32768, 32767)  # Ensures values remain within int16 range
    modified_signal = modified_signal.astype(np.int16)
    
    return modified_signal


# def apply_slider_changes(ecg_signal, slider_values):
#     """
#     Modifies the ECG signal based on the slider values for different arrhythmias.
#     """
#     # Convert ecg_signal to float64 to allow safe multiplication and prevent casting errors
#     modified_signal = np.array(ecg_signal, dtype=np.float64, copy=True)

#     if slider_values['atrial_fibrillation'] > 0:
#         modified_signal *= slider_values['atrial_fibrillation'] * np.sin(np.linspace(0, 5 * np.pi, len(ecg_signal)))
#     if slider_values['myocardial_infarction'] > 0:
#         modified_signal *= slider_values['myocardial_infarction'] * np.cos(np.linspace(0, 5 * np.pi, len(ecg_signal)))
#     if slider_values['sinus_rhythm'] > 0:
#         modified_signal *= slider_values['sinus_rhythm'] * np.random.normal(0, 0.1, len(ecg_signal))
    
#     #convert back to int16 if necessary for further processing
#     modified_signal = modified_signal.astype(np.int16)
    
#     return modified_signal


# arrhythmia_handler.py
# import numpy as np
# from scipy.fft import rfft, irfft, rfftfreq

# def detect_arrhythmias(ecg_signal):
#     """
#     Detects different frequency ranges present in the ECG signal.
#     """
#     detection_results = {
#         'normal': 0.0,
#         'atrial_fibrillation': 0.0,
#         'myocardial_infarction': 0.0,
#         'sinus_rhythm': 0.0
#     }
#     freqs = rfftfreq(len(ecg_signal))
#     fft_values = np.abs(rfft(ecg_signal))

#     # Calculate the mean magnitudes in each frequency range safely
#     af_values = fft_values[(freqs > 4) & (freqs <= 6)]
#     mi_values = fft_values[(freqs >= 0) & (freqs <= 2)]
#     sr_values = fft_values[(freqs >= 2) & (freqs <= 4)]
#     # normal_values = fft_values[(freqs >= 0) & (freqs <= 50)]

#     # Use np.nanmean to safely compute means without NaNs
#     # detection_results['normal'] = np.nanmean(normal_values) if len(normal_values) > 0 else 0.0
#     detection_results['atrial_fibrillation'] = np.nanmean(af_values) if len(af_values) > 0 else 0.0
#     detection_results['myocardial_infarction'] = np.nanmean(mi_values) if len(mi_values) > 0 else 0.0
#     detection_results['sinus_rhythm'] = np.nanmean(sr_values) if len(sr_values) > 0 else 0.0
#     return detection_results

# def apply_slider_changes(ecg_signal, slider_values):
#     """
#     Apply changes to ECG signal frequencies based on slider values.
#     """
#     freqs = rfftfreq(len(ecg_signal))
#     fft_values = rfft(ecg_signal)
    
#     # Adjust frequencies based on slider values
#     # fft_values[(freqs >= 0) & (freqs <= 50)] *= slider_values['normal']
#     fft_values[(freqs > 4) & (freqs <= 6)] *= slider_values['atrial_fibrillation']
#     fft_values[(freqs >= 0) & (freqs <= 2)] *= slider_values['myocardial_infarction']
#     fft_values[(freqs >= 2) & (freqs <= 4)] *= slider_values['sinus_rhythm']
    
#     # Inverse FFT to get the modified time-domain signal
#     modified_signal = irfft(fft_values)
    
#     # Convert to int16 for consistent signal format
#     modified_signal = np.clip(modified_signal, -32768, 32767).astype(np.int16)
    
#     return modified_signal
