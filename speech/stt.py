# speech/stt.py

from faster_whisper import WhisperModel
import numpy as np
import threading
import time # For demonstration/testing purposes

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
            beam_size=5 # Default beam size, good balance for accuracy/speed
        )

        full_transcription = []
        for segment in segments:
            full_transcription.append(segment.text)
        
        return "".join(full_transcription).strip()

# --- Example Usage (for testing the module) ---
if __name__ == "__main__":
    # This example requires sensors/mic.py and scipy to be working
    from sensors.mic import I2SMicrophone
    from scipy.io.wavfile import write as write_wav

    # Setup microphone
    try:
        mic = I2SMicrophone(device_name_part="i2s")
        stt_processor = SpeechToText(model_size="tiny.en") # Use tiny.en for Pi 5 testing

        print("--- STT Test: Speak for 5 seconds ---")
        mic.start_recording()
        print("Recording...")
        time.sleep(5)
        audio_data = mic.stop_recording()

        if audio_data.size > 0:
            print(f"Recorded {audio_data.size} samples. Transcribing...")
            
            # You can optionally save the recorded audio for debugging
            # wav_filename = "stt_test_recording.wav"
            # write_wav(wav_filename, mic.sample_rate, audio_data)
            # print(f"Test audio saved to {wav_filename}")

            transcribed_text = stt_processor.transcribe_audio(audio_data)
            print(f"Transcribed Text: {transcribed_text}")
        else:
            print("No audio recorded for transcription.")

        mic.close()

    except RuntimeError as e:
        print(f"Initialization or Runtime Error: {e}")
        print("Please ensure your I2S microphone is properly configured and detected.")
    except ImportError:
        print("Error: 'scipy' or 'faster_whisper' or 'sounddevice' not installed.")
        print("Please install them: pip install scipy faster-whisper sounddevice numpy")
    except Exception as e:
        print(f"An unexpected error occurred during STT test: {e}")
