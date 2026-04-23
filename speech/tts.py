import subprocess
import os

class TextToSpeech:
    """
    Handles local text-to-speech using piper-tts.
    """
    def __init__(self, model_path="en_US-lessac-medium.onnx"):
        # This assumes piper is in the PATH or in the current directory
        self.model_path = model_path
        # Check if model exists, if not, we might need to download it or use a default
        if not os.path.exists(model_path):
            print(f"Warning: TTS model {model_path} not found. TTS will be disabled or use fallback.")

    def say(self, text):
        """
        Uses piper-tts to speak the provided text.
        """
        print(f"[TTS] Speaking: {text}")
        try:
            # Piper command: echo "text" | piper --model model.onnx --output_raw | aplay -r 22050 -f S16_LE -t raw
            # Using a simple subprocess call to piper
            # If on Windows, 'aplay' won't work, we'd need a different player
            command = f'echo "{text}" | piper --model {self.model_path} --output_raw | aplay -r 22050 -f S16_LE -t raw'
            subprocess.run(command, shell=True, check=True)
        except Exception as e:
            print(f"TTS Error: {e}")

if __name__ == "__main__":
    tts = TextToSpeech()
    tts.say("Authorization required for shell command")
