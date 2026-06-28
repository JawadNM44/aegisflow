from __future__ import annotations
import asyncio
from abc import ABC, abstractmethod
from typing import Optional

from app.services.state import state
from app.models.schemas import AgentInfo, AgentStatus, AgentLog


class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name
        self.info = AgentInfo(name=name)

    async def log(self, level: str, message: str, details: dict | None = None):
        await state.agent_log(self.name, level, message, details)

    async def set_status(self, status: AgentStatus, task: Optional[str] = None):
        self.info.status = status
        self.info.current_task = task
        await state.set_agent(self.info)

    async def run(self):
        await self.set_status(AgentStatus.IDLE)
        try:
            await self._run_impl()
        except Exception as e:
            self.info.error_count += 1
            await self.log("error", f"Agent crashed: {e}")
            await self.set_status(AgentStatus.ERROR)

    @abstractmethod
    async def _run_impl(self):
        pass
