# Sentinel OS Configuration

# Physical Gating (Pi Sentinel)
PIR_PIN = 17
STATUS_LED = 26
APPROVE_BUTTON_PIN = 21
PANIC_BUTTON_PIN = 20

# Display Pinout
OLED_SDA_PIN = 2
OLED_SCL_PIN = 3
OLED_ADDR = 0x3C

# Networking & Security
CORE_BRAIN_IP = "0.0.0.0" # Bind to all interfaces on PC
CORE_BRAIN_PORT = 8000
# IMPORTANT: Update this on the Pi to your PC's actual LAN IP (e.g., 192.168.1.50)
CORE_BRAIN_URL = f"http://localhost:{CORE_BRAIN_PORT}" 
SENTINEL_TOKEN = "SUPER_SECRET_SENTINEL_TOKEN"

# Audio & Voice
MIC_SCK_PIN = 18
MIC_WS_PIN = 19
MIC_SD_PIN = 20
# Ensure this path is correct if you downloaded the model elsewhere!
TTS_MODEL_PATH = "en_US-lessac-medium.onnx" 

# Storage
DB_PATH = "logs/BigLocal.db"
CHROMA_PATH = "knowledge/chromadb"

# AI
LLM_MODEL = "llama3" # Default local model
