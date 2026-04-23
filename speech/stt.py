# speech/stt.py

from faster_whisper import WhisperModel
import numpy as np
import threading
import time # For demonstration/testing purposes
import platform
import sounddevice as sd # Import sounddevice to query devices locally
# This example requires sensors/mic.py and scipy to be working
from audio.mic import I2SMicrophone
from scipy.io.wavfile import write as write_wav



class SpeechToText:
    """
    Handles local speech-to-text transcription using the faster-whisper library.
    """

    def __init__(self, model_size="tiny.en", device="cpu", compute_type="int8"):
        """
        Initializes the SpeechToText module by loading the faster-whisper model.
        Model is loaded only once.
        """
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type

        print(f"Loading faster-whisper model: {model_size} on {device} with {compute_type}...")
        try:
            # Load the model. This will download if not available locally.
            self.model = WhisperModel(
                self.model_size, 
                device=self.device, 
                compute_type=self.compute_type
            )
            print(f"Faster-whisper model '{model_size}' loaded successfully.")
        except Exception as e:
            raise RuntimeError(f"Failed to load faster-whisper model {model_size}: {e}")

    def transcribe_audio(self, audio_data: np.ndarray) -> str:
        """
        Transcribes a NumPy array of audio data into text.
        Expected audio_data: 1D NumPy array of int16 samples (e.g., from I2SMicrophone).
        """
        if audio_data.size == 0:
            return ""

        # faster-whisper expects float32 audio scaled between -1.0 and 1.0
        # Convert int16 (from sounddevice) to float32 and normalize
        # max value for int16 is 32767, so divide by 32768.0 for [-1, 1] range
        audio_float32 = audio_data.astype(np.float32) / 32768.0

        # Transcribe the audio
        # The transcribe method returns an iterator of segments
        segments, info = self.model.transcribe(
            audio_float32, 
            language="en", 
            beam_size=5,
            no_speech_threshold=0.4
        )

        print(f'transcription info {info}')

        full_transcription = []
        segment_count = 0
        for segment in segments:
            full_transcription.append(segment.text)
            segment_count +=1
        print(f'no of sgements{segment_count}')
        return "".join(full_transcription).strip()


if __name__ == "__main__":
    # Determine the microphone for testing based on OS
    mic_test_kwargs = {}
    if platform.system() == "Windows":
        print("Detected Windows OS. Attempting to use default microphone for local testing.")
        mic_test_kwargs = {"device_id": 1} # -1 usually means default input device
        print("If testing fails, please run 'python -m sounddevice' in your terminal")
        print("and adjust 'device_id' or 'device_name_part' in the stt.py example usage.")
    else: # Assume Raspberry Pi OS or similar Linux
        print("Detected non-Windows OS. Attempting to use I2S microphone (Pi-specific).")
        mic_test_kwargs = {"device_name_part": "i2s"} # Pi-specific I2S device

    # Setup microphone and STT processor
    try:
        mic = I2SMicrophone(**mic_test_kwargs)
        stt_processor = SpeechToText(model_size="tiny.en") # Use tiny.en for Pi 5 testing

        print("\n--- STT Test: Speak for 5 seconds ---")
        mic.start_recording()
        print("Recording...")
        time.sleep(5)
        audio_data = mic.stop_recording()

        if audio_data.size > 0:
            print(f"Recorded {audio_data.size} samples. Transcribing...")

            # You can optionally save the recorded audio for debugging
            wav_filename = "stt_test_recording.wav"
            write_wav(wav_filename, mic.sample_rate, audio_data)
            #print(f"Test audio saved to {wav_filename}")

            transcribed_text = stt_processor.transcribe_audio(audio_data)
            print(f"\nTranscribed Text: \"{transcribed_text}\"")
        else:
            print("No audio recorded for transcription.")

        mic.close()

    except RuntimeError as e:
        print(f"Initialization or Runtime Error: {e}")
        print("Please ensure your microphone is properly configured and detected.")
        if platform.system() != "Windows":
            print("For Raspberry Pi, ensure I2S is enabled and dtoverlay=i2s-mmap is configured.")
    except ImportError:
        print("Error: 'scipy' or 'faster_whisper' or 'sounddevice' not installed.")
        print("Please install them: pip install scipy faster-whisper sounddevice numpy")
    except Exception as e:
        print(f"An unexpected error occurred during STT test: {e}")
