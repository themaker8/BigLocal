import time
import requests
import sys
from display.oled import OLEDDisplay
from speech.tts import TextToSpeech
from gpiozero import Button, MotionSensor, LED
import config

# Hardware Initialization
try:
    oled = OLEDDisplay(address=config.OLED_ADDR)
    tts = TextToSpeech(model_path=config.TTS_MODEL_PATH)
    status_led = LED(config.STATUS_LED)
    approve_btn = Button(config.APPROVE_BUTTON_PIN)
    panic_btn = Button(config.PANIC_BUTTON_PIN)
    pir = MotionSensor(config.PIR_PIN)
except Exception as e:
    print(f"Hardware initialization failed: {e}")
    sys.exit(1)

headers = {
    "X-Sentinel-Token": f"Bearer {config.SENTINEL_TOKEN}"
}

def trigger_panic():
    print("[!!!] PANIC BUTTON PRESSED [!!!]")
    try:
        requests.post(f"{config.CORE_BRAIN_URL}/sentinel/panic", headers=headers, timeout=2)
        oled.display_text("EMERGENCY STOP", y=25)
    except Exception as e:
        print(f"Failed to send panic signal: {e}")
        oled.display_text("CORE OFFLINE!", y=25)

panic_btn.when_pressed = trigger_panic

def poll_for_requests():
    print(f"[*] Sentinel Gate Polling {config.CORE_BRAIN_URL}...")
    while True:
        try:
            status_led.on()
            response = requests.get(f"{config.CORE_BRAIN_URL}/sentinel/auth_request", headers=headers, timeout=5)
            status_led.off()

            if response.status_code == 200:
                pending = response.json()
                if pending:
                    req = pending[0]
                    rid, cmd = req["request_id"], req["command"]
                    
                    tts.say("Authorization required for shell command")
                    oled.display_text(f"AUTH REQ:", y=0)
                    oled.display_text(f"{cmd[:15]}", y=15)
                    oled.display_text("Press Button", y=35)
                    
                    start_wait = time.time()
                    auth = False
                    while time.time() - start_wait < 45: # Max wait time for physical authorization
                        if approve_btn.is_pressed:
                            auth = True
                            break
                        
                        if pir.motion_detected and time.time() - start_wait > 5: # PIR_AUTH_THRESHOLD in seconds
                            auth = True
                            break
                        
                        time.sleep(0.1)
                    
                    requests.post(f"{config.CORE_BRAIN_URL}/sentinel/authorize", 
                                 params={"request_id": rid, "approved": auth}, 
                                 headers=headers, timeout=5)
                    oled.display_text("AUTHORIZED" if auth else "DENIED", y=25)
                    time.sleep(2)
                else:
                    oled.display_text("Sentinel Active", y=10)
            
        except Exception as e:
            print(f"Error: {e}")
            oled.display_text("CORE OFFLINE", y=25)
        time.sleep(2)

if __name__ == "__main__":
    poll_for_requests()
