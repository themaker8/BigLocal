from scipy.io.wavfile import write as write_wav
import sounddevice as sd 
import numpy as np       
import collections
import threading
import time 

class I2SMicrophone:
    """
    Handles non-blocking audio capture from an I2S microphone using sounddevice.
    """
    @staticmethod
    def find_i2s_device_index(name_part):
        """
        Finds the index of an I2S input device by searching for 'name_part' in its name.
        """
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            if device.get('max_input_channels', 0) > 0 and name_part.lower() in device.get('name', '').lower():
                print(f"Found I2S input device: {device['name']} at index {i}")
                return i
            
        raise RuntimeError(f"I2S input device containing '{name_part}' not found. "
                           "Ensure I2S is enabled and dtoverlay=i2s-mmap is configured in /boot/config.txt.")

    def __init__(self, sample_rate=44100, channels=1, dtype='int16', device_name_part="i2s", device_id=None):
        """
        Initializes the I2S Microphone for non-blocking capture.
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.dtype = dtype
        self.audio_buffer = collections.deque() 
        self.stream = None 
        self._is_recording = threading.Event() 

        if device_id is not None:
            self.input_device_index = device_id
        else:
            self.input_device_index = I2SMicrophone.find_i2s_device_index(device_name_part)

        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype=self.dtype,
            device=self.input_device_index,
            callback=self._audio_callback_method
        )
        print(f"Microphone initialized: Device Index {self.input_device_index}, Sample Rate {self.sample_rate}Hz")


    def _audio_callback_method(self, indata, frames, time_info, status):
        """
        Callback function for the sounddevice input stream.
        Appends new audio data to the buffer.
        """
        if status:
            print(f"Sounddevice Stream Status: {status}")
        
        
        if self._is_recording.is_set():
            # It's important to make a copy, as indata is a view into a buffer
            self.audio_buffer.append(np.copy(indata))


    def start_recording(self):
        """
        Starts the non-blocking audio recording stream.
        """
        if self.stream.stopped:
            self.audio_buffer.clear() # Clear buffer before new recording
            self.stream.start()
            self._is_recording.set() # Set recording status to active
            print("Recording started...")
        else:
            print("Stream is already active.")


    def stop_recording(self):
        """
        Stops the audio recording stream and returns the collected audio data.
        """
        if self.stream.active:
            self._is_recording.clear() # Set recording status to inactive
            self.stream.stop()
            print("Recording stopped.")
        else:
            print("Stream is not active.")

        # Concatenate all collected NumPy arrays into a single array
        if self.audio_buffer:
            recorded_data = np.concatenate(list(self.audio_buffer), axis=0)
            self.audio_buffer.clear() # Clear buffer after retrieving data
            return recorded_data
        else:
            return np.array([], dtype=self.dtype) # Return empty array if no data was recorded


    def close(self):
        """
        Closes the sounddevice stream and releases resources.
        Should be called when the microphone is no longer needed.
        """
        if self.stream:
            self.stream.close()
            print("Microphone stream closed.")

# --- Example Usage (for testing the module) ---
if __name__ == "__main__":
    
    try:
        mic = I2SMicrophone(device_name_part="i2s") # Adjust name_part if needed

        print("--- Testing 5-second recording ---")
        mic.start_recording()
        time.sleep(5) # Record for 5 seconds
        audio_data = mic.stop_recording()

        if audio_data.size > 0:
            print(f"Recorded {audio_data.size} samples.")
            wav_filename = "recorded_audio.wav"
            write_wav(wav_filename, mic.sample_rate, audio_data)
            print(f"Audio saved to {wav_filename}")
        else:
            print("No audio data recorded.")

        print("--- Testing short recording with background task ---")
        mic.start_recording()
        for i in range(3):
            print(f"Main thread doing other work... {i+1}s")
            time.sleep(1)
        audio_data_short = mic.stop_recording()

        if audio_data_short.size > 0:
            print(f"Recorded {audio_data_short.size} samples in short test.")
        else:
            print("No audio data recorded in short test.")

        mic.close()

    except RuntimeError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
