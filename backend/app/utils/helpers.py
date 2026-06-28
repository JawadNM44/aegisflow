"""Shared helper functions used across services and agents."""
import uuid
from datetime import datetime
from typing import Any

def generate_id(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:8]}"

def timestamp() -> str:
    return datetime.utcnow().isoformat()

def truncate(text: str, max_len: int = 200) -> str:
    return text[:max_len] + "..." if len(text) > max_len else text

def safe_get(data: dict, *keys: str, default: Any = None) -> Any:
    for key in keys:
        try:
            data = data[key]
        except (KeyError, TypeError, IndexError):
            return default
    return data
