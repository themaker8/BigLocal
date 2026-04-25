import requests
import time
import sys

# Simulation of an Agent requesting a high-risk action
CORE_BRAIN_URL = "http://localhost:8000"
TOKEN = "SUPER_SECRET_SENTINEL_TOKEN"

def mock_agent_request(command):
    print(f"\n[Agent] Requesting authorization for: '{command}'")
    headers = {
        "X-Sentinel-Token": f"Bearer {TOKEN}"
    }
    payload = {"command": command}
    
    try:
        print("[Agent] Waiting for Sentinel (Physical) Approval...")
        start_time = time.time()
        
        # This call will block until the Pi Sentinel authorizes it
        response = requests.post(f"{CORE_BRAIN_URL}/agent/request_action", 
                               json=payload, 
                               headers=headers, 
                               timeout=70)
        
        duration = time.time() - start_time
        
        if response.status_code == 200:
            print(f"[Agent] SUCCESS: Action Authorized in {duration:.1f}s!")
            print(f"[Agent] Executing: {response.json()['command']}")
        else:
            print(f"[Agent] FAILED: {response.status_code} - {response.json()['detail']}")
            
    except requests.exceptions.Timeout:
        print("[Agent] ERROR: Request timed out (No physical response).")
    except Exception as e:
        print(f"[Agent] ERROR: {e}")

if __name__ == "__main__":
    print("=== Sentinel OS: Agent Authorization Test ===")
    print("1. Ensure pc_brain.py is running.")
    print("2. Ensure sentinel_gate.py is running on the Pi.")
    
    cmd = input("\nEnter a command to test (e.g., 'rm -rf /' or 'deploy_drone'): ")
    if not cmd:
        cmd = "test_command_01"
    
    mock_agent_request(cmd)
