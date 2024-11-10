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


def apply_slider_changes(ecg_signal, slider_values):
    """
    Modifies the ECG signal based on the slider values for different arrhythmias.
    """
     # Convert ecg_signal to float64 to allow safe multiplication and prevent casting errors
    modified_signal = np.array(ecg_signal, dtype=np.float64, copy=True)

    if slider_values['atrial_fibrillation'] > 0:
        modified_signal *= (1 + slider_values['atrial_fibrillation'])
    if slider_values['myocardial_infarction'] > 0:
        modified_signal *= (1 + slider_values['myocardial_infarction'])
    if slider_values['sinus_rhythm'] > 0:
        modified_signal *= (1 + slider_values['sinus_rhythm'])
    
    #convert back to int16 if necessary for further processing
    modified_signal = modified_signal.astype(np.int16)
    
    return modified_signal
