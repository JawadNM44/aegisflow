from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "AEGISFLOW"
    debug: bool = True
    secret_key: str = "aegisflow-demo-secret-key"

    # Cerebras / Gemma 4
    cerebras_api_key: Optional[str] = None
    cerebras_base_url: str = "https://api.cerebras.ai/v1"
    gemma_model: str = "gemma-4-31b"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    ws_port: int = 8001

    # Redis (optional, falls back to in-memory)
    redis_url: Optional[str] = None

    # Integration credentials (optional)
    slack_token: Optional[str] = None
    slack_channel: str = "#aegisflow-incidents"
    jira_url: Optional[str] = None
    jira_email: Optional[str] = None
    jira_token: Optional[str] = None
    jira_project: str = "AEGIS"
    notion_token: Optional[str] = None
    notion_page_id: Optional[str] = None
    github_token: Optional[str] = None

    # Simulation
    simulation_enabled: bool = True
    simulation_interval: int = 10  # seconds

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
