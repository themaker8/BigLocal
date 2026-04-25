import time
import requests
import sys
import config

# Mocking the physical hardware for PC testing
print("--- Sentinel OS: VIRTUAL SENTINEL (Simulated Pi) ---")

headers = {
    "X-Sentinel-Token": f"Bearer {config.SENTINEL_TOKEN}"
}

def virtual_poll():
    print(f"[*] Virtual Sentinel Polling {config.CORE_BRAIN_URL}...")
    while True:
        try:
            # Poll for requests
            response = requests.get(f"{config.CORE_BRAIN_URL}/sentinel/auth_request", headers=headers, timeout=5)
            
            if response.status_code == 200:
                pending = response.json()
                if pending:
                    req = pending[0]
                    rid = req["request_id"]
                    cmd = req["command"]
                    
                    print(f"\n[!] PHYSICAL AUTHENTICATION REQUIRED")
                    print(f"    COMMAND: {cmd}")
                    print(f"    REQUEST_ID: {rid}")
                    
                    # Simulate the physical button press with keyboard input
                    choice = input("\n[SENTINEL] Press 'y' to AUTHORIZE, 'n' to DENY, or 'p' for PANIC: ").lower()
                    
                    if choice == 'p':
                        requests.post(f"{config.CORE_BRAIN_URL}/sentinel/panic", headers=headers)
                        print("[!!!] PANIC SIGNAL SENT")
                        continue

                    approved = (choice == 'y')
                    
                    # Send result back to Core
                    res = requests.post(f"{config.CORE_BRAIN_URL}/sentinel/authorize", 
                                      params={"request_id": rid, "approved": approved}, 
                                      headers=headers, 
                                      timeout=5)
                    
                    if res.status_code == 200:
                        status = "AUTHORIZED" if approved else "DENIED"
                        print(f"[+] Result Sent: {status}")
                    else:
                        print(f"[-] Error sending result: {res.text}")
                        
                    time.sleep(2)
            
        except requests.exceptions.ConnectionError:
            print("[!] Core Brain not detected. Is main.py running?")
            time.sleep(5)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(2)
        
        time.sleep(1)

if __name__ == "__main__":
    try:
        virtual_poll()
    except KeyboardInterrupt:
        print("\nVirtual Sentinel shutting down.")
