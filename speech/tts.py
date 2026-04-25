import subprocess
import os
import numpy as np
import sounddevice as sd
import platform

import config # Import config module

class TextToSpeech:
    """
    Handles local text-to-speech using piper-tts.
    Works on Windows and Linux.
    """
    def __init__(self): # Removed model_path argument
        self.model_path = config.TTS_MODEL_PATH # Use path from config
        if not os.path.exists(self.model_path):
            print(f"Warning: TTS model {self.model_path} not found. Please ensure it's downloaded and accessible.")

    def say(self, text):
        """
        Uses piper-tts to generate audio and sounddevice to play it.
        """
        print(f"[TTS] Speaking: {text}")
        try:
            # Command to run piper and get raw PCM on stdout
            # Windows needs the full path if not in PATH, but we'll assume 'piper' works
            if platform.system() == "Windows":
                # Use a more robust piping method for Windows
                command = f'echo {text} | piper --model {self.model_path} --output_raw'
            else:
                command = f'echo "{text}" | piper --model {self.model_path} --output_raw'
            
            # Run piper and capture the raw PCM data
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            audio_data, err = process.communicate()

            if audio_data:
                # Piper outputs 16-bit mono PCM at 22050Hz by default
                audio_array = np.frombuffer(audio_data, dtype=np.int16)
                sd.play(audio_array, samplerate=22050)
                sd.wait()
            else:
                print(f"TTS Error: No audio generated. {err.decode()}")

        except Exception as e:
            print(f"TTS Error: {e}")

if __name__ == "__main__":
    tts = TextToSpeech()
    tts.say("System active. How can I help you, Sir?")
