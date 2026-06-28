from __future__ import annotations
import asyncio
import json
from typing import Optional
from app.agents.base import BaseAgent
from app.models.schemas import AgentStatus
from app.services.state import state
from app.models.events import EventBus
from app.services.websocket_manager import ws_manager


class PlannerAgent(BaseAgent):
    def __init__(self):
        super().__init__("Planner")
        self.agents: dict[str, BaseAgent] = {}
        self.event_bus = EventBus()

    def register_agent(self, agent: BaseAgent):
        self.agents[agent.name] = agent

    async def _run_impl(self):
        await self.log("info", "Planner agent started")
        self.event_bus.subscribe("all", self.on_event)
        while True:
            await asyncio.sleep(1)

    async def on_event(self, event):
        await self.set_status(AgentStatus.WORKING, f"Processing: {event.title}")
        await self.log("info", f"Event received: {event.title}", {"event_id": event.id})

        if event.requires_analysis and event.severity.value in ("warning", "critical"):
            analyzer = self.agents.get("Analyzer")
            if analyzer:
                await analyzer.invoke_analysis(event)
            await self.log("info", "Dispatched to AnalyzerAgent")

        await ws_manager.broadcast_event("event", event.model_dump())
        await self.set_status(AgentStatus.IDLE)

    def get_agent(self, name: str) -> Optional[BaseAgent]:
        return self.agents.get(name)
