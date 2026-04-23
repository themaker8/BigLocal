# BigLocal: Security Layer - Hardware-in-the-Loop (HITL) Gatekeeping

## Overview
Standard autonomous agents (like OpenClaw or AutoGPT) often operate with high agency, meaning they can execute shell commands, modify files, or access network resources without real-time human oversight. The **Sentinel Gatekeeping** model introduces a physical "Air Gap" for authorization.

## Security Architecture

### 1. The Core Brain (PC Proxy)
The PC Core Brain acts as a **Mandatory Access Control (MAC)** layer. 
- **Tool Shadowing:** The agent does not have direct access to `subprocess.run` or sensitive APIs. Instead, it must call the Core Brain's `/agent/request_action` endpoint.
- **Asynchronous Blocking:** The Core Brain holds the agent's execution thread in an `asyncio.Event` wait loop. The request cannot proceed until a physical verification signal is received.
- **Token-Based Authentication:** All communication between the Agent, Core, and Sentinel is signed with the `X-Batcave-Token`.

### 2. The Sentinel (Physical Gating)
The Raspberry Pi Sentinel provides the **Physical Authorization Layer**.
- **Out-of-Band Verification:** Authorization does not happen on the same device where the agent lives. Even if the PC is fully compromised, the attacker cannot "press" the physical button on the Pi.
- **Visual Audit:** The OLED display shows the exact command being requested. This prevents "blind signing" where an agent might hide a malicious command inside a benign-looking request.
- **Multi-Modal Auth:** The Sentinel supports both explicit (Button Press) and implicit (PIR-based presence) authorization, ensuring that a human must be physically present at the "Console" for high-risk actions.

### 3. Emergency Stop (Panic Protocol)
The Sentinel features a hard-wired **Panic Button**. 
- When pressed, it sends a high-priority signal to the Core Brain.
- The Core Brain enters a global `EMERGENCY_STOP` state, immediately rejecting all further agent requests and potentially killing active agent processes.

## Why this is safer
1. **Zero-Trust Agency:** We assume the agent *might* hallucinate or be manipulated into executing harmful code. The physical button is the "Dead Man's Switch."
2. **Local-Only:** No cloud dependencies means no external attack surface for the gatekeeping logic.
3. **Physical Presence Requirement:** Remote attackers cannot bypass the Sentinel without physical access to your room.

## Integration Diagram
```text
[ Agent (PC) ] --(Request Action)--> [ Core Brain (FastAPI) ] <---(Poll/Auth)---> [ Sentinel (Pi) ]
      |                                     |                                         |
      | (Blocks)                            | (Queues & Waits)                        | (Displays on OLED)
      |                                     |                                         |
      | <------------(Returns)--------------| <---(Button Pressed)--------------------|
```
