import time
import numpy as np
from audio.mic import I2SMicrophone
from audio.cl import ClapDetector
from speech.stt import SpeechToText
from speech.tts import TextToSpeech
import requests
import config # Add this import

import platform

class AI_Assistant_System:
    def __init__(self):
        print("[AI Assistant] Initializing Systems...")
        
        mic_kwargs = {}
        if platform.system() == "Windows":
            print("[AI Assistant] PC Detected: Using default system microphone.")
            mic_kwargs = {"device_name_part": "1"} 
        else:
            print("[AI Assistant] Pi Detected: Searching for I2S hardware.")
            mic_kwargs = {"device_name_part": "i2s"}

        self.mic = I2SMicrophone(**mic_kwargs)
        self.clap_detector = ClapDetector(self.mic, threshold=4000)

        self.stt = SpeechToText(model_size="tiny.en")
        self.tts = TextToSpeech()
        self.core_url = config.CORE_BRAIN_URL
        self.headers = {"X-Sentinel-Token": f"Bearer {config.SENTINEL_TOKEN}"}

    def listen_and_execute(self):
        print("\n[AI Assistant] System Standby. Clap to wake...")
        
        while True:
            if self.clap_detector.detect_once(chunk_duration=0.5):
                print("[!] Wake Signal Detected (Clap)")
                self.tts.say("Yes, Sir?")
                
                print("[AI Assistant] Listening for command...")
                time.sleep(0.5) 
                self.mic.start_recording()
                time.sleep(5) 
                audio_data = self.mic.stop_recording()
                
                command_text = self.stt.transcribe_audio(audio_data)
                print(f"[AI Assistant] Transcribed: '{command_text}'")
                
                if not command_text:
                    self.tts.say("I didn't catch that, Sir.")
                    continue

                cmd_lower = command_text.lower()
                
                if "hello" in cmd_lower or "hi" in cmd_lower:
                    self.tts.say("Hello, Sir. All systems are operational. How can I assist you?")
                elif "status" in cmd_lower:
                    self.tts.say("The Sentinel is active and guarding the perimeter.")
                elif "emergency" in cmd_lower or "stop" in cmd_lower:
                    requests.post(f"{self.core_url}/sentinel/panic", headers=self.headers)
                    self.tts.say("Emergency stop activated.")
                else:
                    self.tts.say(f"Executing request for {command_text}")
                print("[AI Assistant] Returning to standby...")
                time.sleep(1)

if __name__ == "__main__":
    ai_assistant = AI_Assistant_System()
    try:
        ai_assistant.listen_and_execute()
    except KeyboardInterrupt:
        print("\n[AI Assistant] Powering down.")
