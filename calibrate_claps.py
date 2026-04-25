import time
import numpy as np
from audio.mic import I2SMicrophone
import platform

def calibrate():
    print("--- JARVIS Clap Calibration ---")
    print("This tool shows you the peak volume of your sounds.")
    print("Clap now to see the numbers...\n")
    
    mic_kwargs = {"device_name_part": ""} if platform.system() == "Windows" else {"device_name_part": "i2s"}
    mic = I2SMicrophone(**mic_kwargs)
    
    try:
        while True:
            mic.start_recording()
            time.sleep(0.5)
            samples = mic.stop_recording()
            
            if samples.size > 0:
                # Calculate max absolute peak
                peak = np.max(np.abs(samples))
                
                # Visual meter
                bar = "#" * int(peak / 500)
                print(f"Peak Volume: {peak:5} | {bar}")
                
                if peak > 10000:
                    print("  [!!!] LOUD CLAP DETECTED [!!!]")
                elif peak > 4000:
                    print("  [*] Normal Clap Level")
            
    except KeyboardInterrupt:
        print("\nCalibration finished.")
        mic.close()

if __name__ == "__main__":
    calibrate()
