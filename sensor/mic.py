import board
import audiobusio
import array
from config import MIC_SCK_PIN, MIC_WS_PIN, MIC_SD_PIN

class I2SMicrophone:
    def __init__(self, sck_pin=MIC_SCK_PIN, ws_pin=MIC_WS_PIN, sd_pin=MIC_SD_PIN, sample_rate=16000, bit_depth=16):
        # Map GPIO pins to board pins if they are integers
        sck = getattr(board, f"D{sck_pin}") if isinstance(sck_pin, int) else sck_pin
        ws = getattr(board, f"D{ws_pin}") if isinstance(ws_pin, int) else ws_pin
        sd = getattr(board, f"D{sd_pin}") if isinstance(sd_pin, int) else sd_pin
        
        self.mic = audiobusio.I2SIn(sck, ws, sd)
        self.sample_rate = sample_rate
        self.bit_depth = bit_depth

    def record(self, duration_seconds):
        num_samples = self.sample_rate * duration_seconds
        samples = array.array('H' if self.bit_depth == 16 else 'I', [0] * int(num_samples))
        self.mic.record(samples, self.sample_rate)
        return samples

    def deinit(self):
        self.mic.deinit()
