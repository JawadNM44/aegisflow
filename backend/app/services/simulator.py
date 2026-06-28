"""simulator service - infrastructure management for AEGISFLOW observability."""
from __future__ import annotations
import asyncio
import uuid
import random
from datetime import datetime

from app.services.state import state
from app.models.schemas import (
    InfrastructureEvent, EventType, EventSeverity, C4Node, HealthStatus,
    NodeType, C4Edge, EdgeType
)
from app.models.events import EventBus
from app.config import settings


class InfrastructureSimulator:
    _instance: InfrastructureSimulator | None = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._running = False
            cls._instance._task = None
        return cls._instance

    async def start(self):
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._simulate_background_activity())

    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
            self._task = None

    async def _simulate_background_activity(self):
        await asyncio.sleep(3)
        while self._running:
            try:
                if random.random() < 0.1:
                    await self._random_minor_event()
                await asyncio.sleep(settings.simulation_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[Simulator] Error: {e}")

    async def _random_minor_event(self):
        node_ids = list(state.architecture.nodes.keys())
        if not node_ids:
            return
        node_id = random.choice(node_ids)
        node = state.architecture.nodes[node_id]
        await state.update_node_health(node_id, HealthStatus.WARNING)
        event = EventBus.create_event(
            source="simulator",
            event_type=EventType.HEALTH_CHANGE,
            severity=EventSeverity.WARNING,
            title=f"{node.name} latency spike detected",
            message=f"Response time for {node.name} increased by 200ms",
            affected_nodes=[node_id],
            payload={"latency_ms": random.randint(500, 2000), "threshold": 300},
        )
        await EventBus().publish(event)
        await asyncio.sleep(5)
        if node_id in state.architecture.nodes:
            await state.update_node_health(node_id, HealthStatus.HEALTHY)

    async def inject_failure(self, target_name: str, severity: str = "critical"):
        arch = await state.get_architecture()
        target_node = None
        for node in arch.nodes.values():
            if target_name.lower() in node.name.lower() or target_name.lower() == node.id.lower():
                target_node = node
                break

        if not target_node:
            return {"error": f"Node '{target_name}' not found"}

        health = HealthStatus.CRITICAL if severity == "critical" else HealthStatus.WARNING
        before_health = target_node.health
        await state.update_node_health(target_node.id, health)

        event = EventBus.create_event(
            source="simulator",
            event_type=EventType.FAILURE,
            severity=EventSeverity.CRITICAL if severity == "critical" else EventSeverity.WARNING,
            title=f"{target_node.name} FAILURE",
            message=f"{target_node.name} is {'down' if severity == 'critical' else 'degraded'}",
            affected_nodes=[target_node.id],
            payload={
                "before_health": before_health.value,
                "after_health": health.value,
                "type": target_node.type.value,
                "technology": target_node.technology,
            },
        )
        await EventBus().publish(event)

        connected_edges = [e for e in arch.edges.values() if e.source == target_node.id or e.target == target_node.id]
        for edge in connected_edges:
            affected_id = edge.target if edge.source == target_node.id else edge.source
            if arch.nodes.get(affected_id) and arch.nodes[affected_id].health == HealthStatus.HEALTHY:
                if severity == "critical":
                    await state.update_node_health(affected_id, HealthStatus.WARNING)
                    downstream_event = EventBus.create_event(
                        source="simulator",
                        event_type=EventType.FAILURE,
                        severity=EventSeverity.WARNING,
                        title=f"{arch.nodes[affected_id].name} affected by {target_node.name} failure",
                        message=f"Propagation: {target_node.name} failure impacting {arch.nodes[affected_id].name}",
                        affected_nodes=[affected_id],
                        payload={"propagation_from": target_node.id},
                    )
                    await EventBus().publish(downstream_event)

        return {"success": True, "node": target_node.name, "severity": severity}

    async def restore_service(self, target_name: str):
        arch = await state.get_architecture()
        for node in arch.nodes.values():
            if target_name.lower() in node.name.lower() or target_name.lower() == node.id.lower():
                old_health = node.health
                if old_health != HealthStatus.HEALTHY:
                    await state.update_node_health(node.id, HealthStatus.HEALTHY)
                    event = EventBus.create_event(
                        source="simulator",
                        event_type=EventType.HEALTH_CHANGE,
                        severity=EventSeverity.INFO,
                        title=f"{node.name} restored",
                        message=f"{node.name} is now healthy (was {old_health.value})",
                        affected_nodes=[node.id],
                    )
                    await EventBus().publish(event)
                    return {"success": True, "node": node.name}
        return {"error": f"Node '{target_name}' not found"}

    async def simulate_deployment(self, target_name: str):
        event = EventBus.create_event(
            source="simulator",
            event_type=EventType.DEPLOYMENT,
            severity=EventSeverity.INFO,
            title=f"Deployment triggered: {target_name}",
            message=f"New version of {target_name} is being deployed",
            affected_nodes=[],
            payload={"service": target_name, "version": f"v{random.randint(1,20)}.{random.randint(0,9)}"},
        )
        await EventBus().publish(event)
        return {"success": True}

    async def simulate_scaling(self, target_name: str, replicas: int = 3):
        event = EventBus.create_event(
            source="simulator",
            event_type=EventType.SCALING,
            severity=EventSeverity.INFO,
            title=f"Scaling {target_name} to {replicas} replicas",
            message=f"Auto-scaling triggered for {target_name}",
            affected_nodes=[],
            payload={"service": target_name, "replicas": replicas},
        )
        await EventBus().publish(event)
        return {"success": True}


simulator = InfrastructureSimulator()
