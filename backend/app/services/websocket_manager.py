from __future__ import annotations

"""websocket_manager service - infrastructure management for AEGISFLOW observability."""

import asyncio
import json
from typing import Any
from fastapi import WebSocket
from collections import defaultdict


class WebSocketManager:
    _instance: WebSocketManager | None = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connections: dict[str, set[WebSocket]] = defaultdict(set)
        return cls._instance

    async def connect(self, ws: WebSocket, channel: str = "global"):
        await ws.accept()
        self.connections[channel].add(ws)

    async def disconnect(self, ws: WebSocket, channel: str = "global"):
        self.connections[channel].discard(ws)

    async def broadcast(self, channel: str, message: dict[str, Any]):
        dead = set()
        for ws in list(self.connections[channel]):
            try:
                await ws.send_json(message)
            except Exception:
                dead.add(ws)
        for ws in dead:
            self.connections[channel].discard(ws)

    async def broadcast_event(self, event_type: str, data: dict[str, Any]):
        await self.broadcast("global", {"type": event_type, "data": data})


ws_manager = WebSocketManager()
