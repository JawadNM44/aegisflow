# AEGISFLOW

**AI Observability for Modern Cloud Infrastructure**

AEGISFLOW is an AI-native observability platform for the Cerebras × Google DeepMind Gemma 4 Hackathon. It combines real-time C4 architecture visualization with multi-agent AI reasoning to transform how enterprises understand and respond to cloud infrastructure failures.

## Quick Start

```bash
# Clone and start
git clone <repo> && cd aegisflow
docker compose up

# Or run without Docker:

# Backend
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Frontend
cd frontend
npm install
npm run dev
```

Open **http://localhost:3000**

## Architecture

```
Frontend (Next.js + React Flow)  ←→  WebSocket  ←→  Backend (FastAPI)  ←→  Agents
                                                          ↑
                                                    Gemma 4 (Cerebras)
```

### Multi-Agent System (11 agents)

| Agent | Role |
|-------|------|
| **Planner** | Orchestrates all agents, coordinates workflows |
| **Watcher** | Polls infrastructure, emits health events |
| **Diagram** | Maintains C4 architecture model |
| **Analyzer** | Gemma 4 reasoning for every infrastructure event |
| **RootCause** | Deep investigation of incidents |
| **Documentation** | Generates incident reports |
| **Slack** | Posts notifications (simulated or live) |
| **Jira** | Creates tickets (simulated or live) |
| **Notion** | Updates documentation (simulated or live) |
| **QA** | Validates system integrity continuously |
| **Architecture** | Synchronizes C4 model |

### Demo Flow

1. Open dashboard → Live C4 architecture diagram with health status
2. Click "Kill PostgreSQL" → Instant failure injection
3. Diagram updates: PostgreSQL turns red, dependencies highlight
4. Analyzer Agent (Gemma 4) generates incident analysis
5. Slack notification sent (simulated or real)
6. Jira ticket created (simulated or real)
7. Incident report generated
8. Root Cause Agent performs deep investigation
9. All within seconds

## Features

- **Live C4 Architecture**: Auto-discovered infrastructure visualized as interactive React Flow diagram
- **Gemma 4 Reasoning**: Every event analyzed via Cerebras ultra-fast inference
- **Multi-Agent Orchestration**: 11 coordinated agents for incident response
- **Failure Propagation**: Blast radius visualization with animated dependencies
- **Enterprise Integrations**: Slack, Jira, Notion, GitHub (graceful degradation)
- **Infrastructure Simulator**: Realistic demo without real infrastructure
- **Audit Logs**: Complete incident timeline and agent activity

## Tracks

- **Track 1** — Best Multi-Agent + Multimodal Use Case
- **Track 3** — Best Enterprise Use Case

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI (Python) |
| Frontend | Next.js, React, TypeScript |
| Diagram | React Flow |
| AI | Gemma 4 (Cerebras API) |
| Realtime | WebSockets |
| State | In-memory |
| Deployment | Docker Compose |
