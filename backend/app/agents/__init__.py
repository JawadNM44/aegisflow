"""Multi-agent orchestration - coordinator for 11 specialist infrastructure agents."""
from __future__ import annotations
import asyncio
from app.agents.base import BaseAgent
from app.agents.planner import PlannerAgent
from app.agents.watcher import WatcherAgent
from app.agents.diagram import DiagramAgent
from app.agents.analyzer import AnalyzerAgent
from app.agents.root_cause import RootCauseAgent
from app.agents.documentation import DocumentationAgent
from app.agents.slack import SlackAgent, JiraAgent, NotionAgent
from app.agents.qa import QAAgent
from app.agents.architecture import ArchitectureAgent
from app.services.state import state
from app.models.schemas import AgentInfo, AgentStatus


class AgentOrchestrator:
    def __init__(self):
        self.planner = PlannerAgent()
        self.agents: dict[str, BaseAgent] = {}
        self._register_agents()

    def _register_agents(self):
        agents = [
            self.planner,
            WatcherAgent(),
            DiagramAgent(),
            AnalyzerAgent(),
            RootCauseAgent(),
            DocumentationAgent(),
            SlackAgent(),
            JiraAgent(),
            NotionAgent(),
            QAAgent(),
            ArchitectureAgent(),
        ]
        for agent in agents:
            self.agents[agent.name] = agent
            if agent.name != "Planner":
                self.planner.register_agent(agent)

    async def start_all(self):
        tasks = []
        for name, agent in self.agents.items():
            t = asyncio.create_task(agent.run())
            tasks.append(t)
        await asyncio.gather(*tasks, return_exceptions=True)

    async def get_status(self) -> list[AgentInfo]:
        return await state.get_agents()


orchestrator = AgentOrchestrator()
