from gpiozero import MotionSensor
from config import PIR_PIN

class PIRSensor:
    def __init__(self):
        self.sensor = MotionSensor(PIR_PIN)

    def wait_for_motion(self):
        self.sensor.wait_for_motion()

    def wait_for_no_motion(self):                           
         self.sensor.wait_for_no_motion()                    
                                                    
    def is_motion_detected(self):                           
        return self.sensor.motion_detected                    
                                                    
    def when_motion(self, callback):                        
         self.sensor.when_motion = callback                  
                                                    
    def when_no_motion(self, callback):                     
         self.sensor.when_no_motion = callback

