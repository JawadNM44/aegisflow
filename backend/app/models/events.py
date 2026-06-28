from __future__ import annotations
import asyncio
import uuid
from datetime import datetime
from typing import Callable, Coroutine, Any
from collections import defaultdict
from app.models.schemas import InfrastructureEvent, EventType, EventSeverity


class EventBus:
    _instance: EventBus | None = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.subscribers = defaultdict(list)
            cls._instance.event_history: list[InfrastructureEvent] = []
            cls._instance._lock = asyncio.Lock()
        return cls._instance

    async def publish(self, event: InfrastructureEvent) -> None:
        async with self._lock:
            self.event_history.append(event)
            if len(self.event_history) > 1000:
                self.event_history = self.event_history[-500:]

        tasks = []
        for callback in list(self.subscribers.get("all", [])):
            tasks.append(callback(event))
        for callback in list(self.subscribers.get(event.type.value, [])):
            tasks.append(callback(event))
        for callback in list(self.subscribers.get(event.severity.value, [])):
            tasks.append(callback(event))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    def subscribe(self, event_type: str, callback: Callable[[InfrastructureEvent], Coroutine]):
        self.subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: str, callback: Callable):
        if callback in self.subscribers[event_type]:
            self.subscribers[event_type].remove(callback)

    async def get_history(self, limit: int = 50) -> list[InfrastructureEvent]:
        async with self._lock:
            return self.event_history[-limit:]

    @classmethod
    def create_event(cls, source: str, event_type: EventType, severity: EventSeverity,
                     title: str, message: str = "", affected_nodes: list[str] | None = None,
                     payload: dict | None = None) -> InfrastructureEvent:
        return InfrastructureEvent(
            id=str(uuid.uuid4())[:8],
            source=source,
            type=event_type,
            severity=severity,
            title=title,
            message=message,
            affected_nodes=affected_nodes or [],
            payload=payload or {},
        )
