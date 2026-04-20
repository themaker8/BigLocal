from luma.oled.device import ssd1306
from luma.i2c.interface import i2c
from luma.core.render import canvas
from config import OLED_ADDR

class OLEDDisplay:
    def __init__(self, port=1, address=OLED_ADDR):
        self.serial = i2c(port=port, address=address)
        self.device = ssd1306(self.serial)

    def display_text(self, text, x=10, y=10):
        with canvas(self.device) as draw:
            draw.rectangle(self.device.bounding_box, outline="black", fill="black")
            draw.text((x, y), text, fill="white")

    def clear(self):
        with canvas(self.device) as draw:
            draw.rectangle(self.device.bounding_box, outline="black", fill="black")

    def show_status(self, motion=False, clap=False):
        with canvas(self.device) as draw:
            draw.rectangle(self.device.bounding_box, outline="white")
            draw.text((10, 10), f"Motion: {'YES' if motion else 'NO'}", fill="white")
            draw.text((10, 30), f"Clap: {'YES' if clap else 'NO'}", fill="white")
