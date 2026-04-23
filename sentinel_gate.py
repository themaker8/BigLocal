import time
import requests
import sys
from display.oled import OLEDDisplay
from speech.tts import TextToSpeech
from gpiozero import Button, MotionSensor, LED
from config import OLED_ADDR, STATUS_LED, PIR_PIN

# Configuration - Update CORE_BRAIN_URL with the PC's actual IP address
CORE_BRAIN_URL = "http://192.168.1.100:8000" # Example IP
BATCAVE_TOKEN = "SUPER_SECRET_BATCAVE_TOKEN"
APPROVE_BUTTON_PIN = 21
PANIC_BUTTON_PIN = 20
PIR_AUTH_THRESHOLD = 5 # Seconds of continuous presence for auto-auth if enabled

# Hardware Initialization
try:
    oled = OLEDDisplay()
    tts = TextToSpeech()
    status_led = LED(STATUS_LED)
    approve_btn = Button(APPROVE_BUTTON_PIN)
    panic_btn = Button(PANIC_BUTTON_PIN)
    pir = MotionSensor(PIR_PIN)
except Exception as e:
    print(f"Hardware initialization failed: {e}")
    sys.exit(1)

headers = {
    "X-Batcave-Token": f"Bearer {BATCAVE_TOKEN}"
}

def trigger_panic():
    """
    Sends a panic signal to the Core Brain to immediately stop all agent activities.
    """
    print("[!!!] PANIC BUTTON PRESSED [!!!]")
    try:
        response = requests.post(f"{CORE_BRAIN_URL}/sentinel/panic", headers=headers, timeout=2)
        if response.status_code == 200:
            oled.display_text("EMERGENCY STOP", y=25)
            print("Emergency stop signal acknowledged by Core.")
    except Exception as e:
        print(f"Failed to send panic signal: {e}")
        oled.display_text("CORE OFFLINE!", y=25)

# Attach interrupt for panic button
panic_btn.when_pressed = trigger_panic

def poll_for_requests():
    """
    Main loop to poll the Core Brain for pending authorizations.
    """
    print(f"[*] Sentinel Gate Polling {CORE_BRAIN_URL}...")
    
    while True:
        try:
            status_led.on()
            response = requests.get(f"{CORE_BRAIN_URL}/sentinel/auth_request", headers=headers, timeout=5)
            status_led.off()

            if response.status_code == 200:
                pending = response.json()
                if pending:
                    # Logic for handling the first pending request in the queue
                    req = pending[0]
                    request_id = req["request_id"]
                    command = req["command"]
                    
                    print(f"[*] Authorization Required: {command}")
                    tts.say("Authorization required for shell command")
                    oled.display_text(f"AUTH REQ:", y=0)
                    oled.display_text(f"{command[:15]}", y=15)
                    oled.display_text("Press Button", y=35)
                    
                    # Wait for user physical action (Button or PIR)
                    start_wait = time.time()
                    authorized = False
                    presence_start = None
                    
                    while time.time() - start_wait < 45: # 45 second window
                        # Check Button
                        if approve_btn.is_pressed:
                            authorized = True
                            print("[+] Button Authorization Received")
                            break
                        
                        # Check PIR (Presence-based Authorization)
                        if pir.motion_detected:
                            if presence_start is None:
                                presence_start = time.time()
                            elif time.time() - presence_start >= PIR_AUTH_THRESHOLD:
                                authorized = True
                                print("[+] PIR Presence Authorization Received")
                                break
                        else:
                            presence_start = None
                        
                        time.sleep(0.1)
                    
                    # Send result back to Core
                    action_payload = {"request_id": request_id, "approved": authorized}
                    res = requests.post(f"{CORE_BRAIN_URL}/sentinel/authorize", 
                                      params=action_payload, 
                                      headers=headers, 
                                      timeout=5)
                    
                    if authorized:
                        oled.display_text("AUTHORIZED", y=25)
                    else:
                        oled.display_text("DENIED/TIMEOUT", y=25)
                    
                    time.sleep(2)
                else:
                    oled.display_text("Sentinel Active", y=10)
                    oled.display_text("Scanning...", y=30)
            
        except requests.exceptions.ConnectionError:
            print("[!] Cannot connect to Core Brain.")
            oled.display_text("CORE OFFLINE", y=25)
        except Exception as e:
            print(f"Polling error: {e}")
        
        time.sleep(2) # Poll interval

if __name__ == "__main__":
    try:
        oled.display_text("Sentinel Booting", y=25)
        time.sleep(1)
        poll_for_requests()
    except KeyboardInterrupt:
        print("Sentinel shutting down.")
        oled.clear()
