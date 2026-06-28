from __future__ import annotations
import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.config import settings
from app.models.events import EventBus
from app.services.state import state
from app.services.simulator import simulator
from app.services.websocket_manager import ws_manager

logger = logging.getLogger("aegisflow")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("AEGISFLOW starting...")
    logger.info(f"Cerebras mode: {'SIMULATION' if not settings.cerebras_api_key else 'LIVE'}")
    logger.info(f"Simulation: {'ENABLED' if settings.simulation_enabled else 'DISABLED'}")

    if settings.simulation_enabled:
        await simulator.start()
        logger.info("Infrastructure simulator started")

    if settings.simulation_enabled:
        from app.agents import orchestrator
        asyncio.create_task(orchestrator.start_all())
        logger.info("Multi-agent system started")

    yield

    await simulator.stop()
    logger.info("AEGISFLOW shutting down")


app = FastAPI(
    title="AEGISFLOW",
    description="AI Observability for Modern Cloud Infrastructure",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health")
async def health():
    arch = await state.get_architecture()
    return {
        "status": "ok",
        "app": settings.app_name,
        "cerebras": "simulated" if not settings.cerebras_api_key else "live",
        "nodes": len(arch.nodes),
        "edges": len(arch.edges),
        "agents": len([a for a in await state.get_agents()]),
    }


@app.get("/")
async def root():
    return {
        "name": "AEGISFLOW",
        "tagline": "AI Observability for Modern Cloud Infrastructure",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }
