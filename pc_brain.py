from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel
import asyncio
import uuid
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pc_brain")

app = FastAPI(title="Batcave Core Brain")

# Security Token (In a real scenario, use environment variables)
BATCAVE_TOKEN = "SUPER_SECRET_BATCAVE_TOKEN"

# State Management
auth_queue = {} # request_id: { "command": str, "status": str, "event": asyncio.Event, "timestamp": float }
agent_status = "ACTIVE" # ACTIVE or EMERGENCY_STOP

class AuthRequest(BaseModel):
    command: str

def verify_token(token: str):
    if token != f"Bearer {BATCAVE_TOKEN}":
        logger.warning(f"Unauthorized access attempt with token: {token}")
        raise HTTPException(status_code=403, detail="Unauthorized")

@app.post("/agent/request_action")
async def request_action(request: AuthRequest, x_batcave_token: str = Header(None)):
    """
    Endpoint for the OpenClaw agent to request a high-risk action.
    This call blocks until the physical Sentinel authorizes it.
    """
    verify_token(x_batcave_token)
    
    if agent_status == "EMERGENCY_STOP":
        logger.error("Agent attempted action during EMERGENCY STOP")
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
        await asyncio.wait_for(event.wait(), timeout=60.0) # 1 minute timeout
    except asyncio.TimeoutError:
        auth_queue[request_id]["status"] = "TIMEOUT"
        logger.warning(f"Authorization timed out for request {request_id}")
        raise HTTPException(status_code=408, detail="Authorization timed out.")
    
    status = auth_queue[request_id]["status"]
    if status == "APPROVED":
        logger.info(f"[+] Request {request_id} APPROVED")
        return {"status": "AUTHORIZED", "command": request.command}
    else:
        logger.info(f"[-] Request {request_id} DENIED")
        raise HTTPException(status_code=401, detail="Authorization denied.")

@app.get("/sentinel/auth_request")
async def get_pending_requests(x_batcave_token: str = Header(None)):
    """
    Endpoint for the Pi Sentinel to poll for pending authorizations.
    """
    verify_token(x_batcave_token)
    
    pending = [
        {"request_id": rid, "command": req["command"]}
        for rid, req in auth_queue.items()
        if req["status"] == "PENDING"
    ]
    return pending

@app.post("/sentinel/authorize")
async def authorize_request(request_id: str, approved: bool, x_batcave_token: str = Header(None)):
    """
    Endpoint for the Pi Sentinel to approve or deny a request.
    """
    verify_token(x_batcave_token)
    
    if request_id not in auth_queue:
        raise HTTPException(status_code=404, detail="Request not found")
    
    auth_queue[request_id]["status"] = "APPROVED" if approved else "DENIED"
    auth_queue[request_id]["event"].set()
    
    return {"status": "SUCCESS", "request_id": request_id, "action": "APPROVED" if approved else "DENIED"}

@app.post("/sentinel/panic")
async def trigger_panic(x_batcave_token: str = Header(None)):
    """
    Emergency Stop endpoint.
    """
    verify_token(x_batcave_token)
    global agent_status
    agent_status = "EMERGENCY_STOP"
    logger.critical("[!!!] EMERGENCY STOP TRIGGERED BY SENTINEL [!!!]")
    
    # In a real scenario, this might also trigger a subprocess kill for the agent
    return {"status": "EMERGENCY_STOP_ACTIVATED"}

@app.get("/health")
async def health():
    return {"status": "ALIVE", "agent_status": agent_status}

if __name__ == "__main__":
    import uvicorn
    # Running on 0.0.0.0 to be accessible by the Pi on the local network
    uvicorn.run(app, host="0.0.0.0", port=8000)
