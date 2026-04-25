from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel
import asyncio
import uuid
import time
import logging
import uvicorn
import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pc_brain")

app = FastAPI(title="Sentinel Core Brain")

# State Management
auth_queue = {} # request_id: { "command": str, "status": str, "event": asyncio.Event, "timestamp": float }
agent_status = "ACTIVE" # ACTIVE or EMERGENCY_STOP

class AuthRequest(BaseModel):
    command: str

def verify_token(token: str):
    if token != f"Bearer {config.SENTINEL_TOKEN}":
        logger.warning(f"Unauthorized access attempt with token: {token}")
        raise HTTPException(status_code=403, detail="Unauthorized")

@app.post("/agent/request_action")
async def request_action(request: AuthRequest, x_sentinel_token: str = Header(None)):
    verify_token(x_sentinel_token)
    
    if agent_status == "EMERGENCY_STOP":
        raise HTTPException(status_code=503, detail="Agent is disabled due to Emergency Stop.")

    request_id = str(uuid.uuid4())
    event = asyncio.Event()
    
    auth_queue[request_id] = {
        "command": request.command,
        "status": "PENDING",
        "event": event,
        "timestamp": time.time()
    }
    
    logger.info(f"[*] New Auth Request: {request_id} - {request.command}")
    
    try:
        await asyncio.wait_for(event.wait(), timeout=60.0)
    except asyncio.TimeoutError:
        auth_queue[request_id]["status"] = "TIMEOUT"
        raise HTTPException(status_code=408, detail="Authorization timed out.")
    
    status = auth_queue[request_id]["status"]
    if status == "APPROVED":
        return {"status": "AUTHORIZED", "command": request.command}
    else:
        raise HTTPException(status_code=401, detail="Authorization denied.")

@app.get("/sentinel/auth_request")
async def get_pending_requests(x_sentinel_token: str = Header(None)):
    verify_token(x_sentinel_token)
    return [
        {"request_id": rid, "command": req["command"]}
        for rid, req in auth_queue.items()
        if req["status"] == "PENDING"
    ]

@app.post("/sentinel/authorize")
async def authorize_request(request_id: str, approved: bool, x_sentinel_token: str = Header(None)):
    verify_token(x_sentinel_token)
    if request_id not in auth_queue:
        raise HTTPException(status_code=404, detail="Request not found")
    
    auth_queue[request_id]["status"] = "APPROVED" if approved else "DENIED"
    auth_queue[request_id]["event"].set()
    return {"status": "SUCCESS", "request_id": request_id}

@app.post("/sentinel/panic")
async def trigger_panic(x_sentinel_token: str = Header(None)):
    verify_token(x_sentinel_token)
    global agent_status
    agent_status = "EMERGENCY_STOP"
    logger.critical("[!!!] EMERGENCY STOP TRIGGERED [!!!]")
    return {"status": "EMERGENCY_STOP_ACTIVATED"}

def start_server():
    uvicorn.run(app, host=config.CORE_BRAIN_IP, port=config.CORE_BRAIN_PORT)

if __name__ == "__main__":
    start_server()
