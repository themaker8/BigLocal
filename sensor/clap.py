
import array
import time
from sensor.mic import I2SMicrophone

class ClapDetector:
    def __init__(self, mic: I2SMicrophone, threshold=10000):
        self.mic = mic
        self.threshold = threshold

    def is_clap(self, samples):
        # Basic peak detection
        for s in samples:
            # Handle signed 16-bit
            val = s if s < 32768 else s - 65536
            if abs(val) > self.threshold:
                return True
        return False

    def listen_for_clap(self, chunk_duration=0.1):
        while True:
            samples = self.mic.record(chunk_duration)
            if self.is_clap(samples):
                return True
            time.sleep(0.01)

    def detect_once(self, chunk_duration=0.1):
        samples = self.mic.record(chunk_duration)
        return self.is_clap(samples)
