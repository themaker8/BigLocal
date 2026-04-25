import sounddevice as sd
from scipy.io.wavfile import write as write_wav
import numpy as np
import time

def diagnostic():
    fs = 44100  # Sample rate
    seconds = 3  # Duration of recording

    print("--- Batcave Audio Diagnostic ---")
    print(f"1. Recording for {seconds} seconds... Speak now!")
    
    # Record audio
    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()  # Wait until recording is finished
    
    print("2. Recording complete. Saving to 'diagnostic_test.wav'...")
    write_wav('diagnostic_test.wav', fs, myrecording)
    
    print("3. Playing back... Can you hear yourself?")
    # Playback audio
    sd.play(myrecording, fs)
    sd.wait()  # Wait until playback is finished
    
    print("\nDiagnostic finished.")
    print("If you couldn't hear anything, check your 'Default Input/Output' in Windows sound settings.")

if __name__ == "__main__":
    try:
        diagnostic()
    except Exception as e:
        print(f"Error during diagnostic: {e}")
