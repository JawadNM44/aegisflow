from __future__ import annotations
from datetime import datetime
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel

from app.services.state import state
from app.models.schemas import (
    C4Architecture, C4Node, C4Edge, HealthStatus,
    Incident, InfrastructureEvent, SimulationCommand,
    AgentInfo, GemmaAnalysis
)
from app.models.events import EventBus
from app.services.websocket_manager import ws_manager
from app.services.simulator import simulator
from app.services.cerebras import cerebras

router = APIRouter(prefix="/api/v1")


# --- Health ---

@router.get("/health")
async def api_health():
    arch = await state.get_architecture()
    return {
        "status": "ok",
        "app": "AEGISFLOW",
        "cerebras": "live" if not cerebras.simulation_mode else "simulated",
        "cerebras_speed_ms": cerebras.last_inference_ms or None,
        "nodes": len(arch.nodes),
        "edges": len(arch.edges),
        "agents": len([a for a in await state.get_agents()]),
    }


# --- Architecture ---

@router.get("/architecture")
async def get_architecture():
    arch = await state.get_architecture()
    return arch.model_dump()


@router.get("/architecture/nodes")
async def get_nodes():
    arch = await state.get_architecture()
    return [n.model_dump() for n in arch.nodes.values()]


@router.get("/architecture/edges")
async def get_edges():
    arch = await state.get_architecture()
    return [e.model_dump() for e in arch.edges.values()]


@router.post("/architecture/nodes/{node_id}/health")
async def update_node_health(node_id: str, health: HealthStatus):
    await state.update_node_health(node_id, health)
    arch = await state.get_architecture()
    await ws_manager.broadcast_event("architecture", arch.model_dump())
    return {"status": "ok"}


# --- Incidents ---

@router.get("/incidents")
async def get_incidents(limit: int = 20):
    incidents = await state.get_incidents(limit)
    return [i.model_dump() for i in incidents]


@router.get("/incidents/{incident_id}")
async def get_incident(incident_id: str):
    incident = await state.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident.model_dump()


# --- Events ---

@router.get("/events")
async def get_events(limit: int = 50):
    from app.services.state import state
    events = await state.get_events(limit)
    return [e.model_dump() for e in events]


# --- Simulation ---

@router.post("/simulate/failure")
async def simulate_failure(cmd: SimulationCommand):
    result = await simulator.inject_failure(cmd.target, cmd.severity or "critical")
    return result


@router.post("/simulate/restore")
async def simulate_restore(target: str):
    result = await simulator.restore_service(target)
    return result


@router.post("/simulate/deployment")
async def simulate_deployment(target: str):
    result = await simulator.simulate_deployment(target)
    return result


@router.post("/simulate/scaling")
async def simulate_scaling(target: str, replicas: int = 3):
    result = await simulator.simulate_scaling(target, replicas)
    return result


# --- Agents ---

@router.get("/agents")
async def get_agents():
    from app.agents import orchestrator
    return await orchestrator.get_status()


@router.get("/agents/{name}")
async def get_agent(name: str):
    agent = await state.get_agent(name)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent.model_dump()


# --- Analysis ---

@router.post("/analyze")
async def analyze_event(event_data: dict[str, Any]):
    event = InfrastructureEvent(**event_data)
    arch = await state.get_architecture()
    analysis = cerebras.analyze_event(event.model_dump(), arch.model_dump())
    return analysis.model_dump()


# --- Integrations ---

@router.get("/integrations/status")
async def integration_status():
    from app.agents.slack import SlackAgent, JiraAgent, NotionAgent
    return {
        "slack": SlackAgent()._status.value if hasattr(SlackAgent(), '_status') else "simulated",
        "jira": JiraAgent()._status.value if hasattr(JiraAgent(), '_status') else "simulated",
        "notion": NotionAgent()._status.value if hasattr(NotionAgent(), '_status') else "simulated",
    }


# --- Multimodal Diagram Analysis ---

class DiagramAnalysisRequest(BaseModel):
    image: str
    prompt: str = "Analyze this infrastructure architecture diagram. Identify potential issues, single points of failure, bottlenecks, and optimization opportunities. Describe what you see."


@router.post("/analyze/diagram")
async def analyze_diagram(req: DiagramAnalysisRequest):
    result = cerebras.analyze_diagram(req.image, req.prompt)
    if result:
        return result
    return {"analysis": "Diagram analysis unavailable (Gemma 4 API not reachable)", "inference_time_ms": None}


# --- WebSocket ---

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        arch = await state.get_architecture()
        await websocket.send_json({"type": "init", "architecture": arch.model_dump()})

        incidents = await state.get_incidents()
        await websocket.send_json({"type": "incidents", "incidents": [i.model_dump() for i in incidents]})

        await websocket.send_json({"type": "ready", "message": "AEGISFLOW connected"})

        while True:
            data = await websocket.receive_json()
            action = data.get("action")
            if action == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket)
    except Exception as e:
        print(f"[WebSocket] Error: {e}")
        await ws_manager.disconnect(websocket)
