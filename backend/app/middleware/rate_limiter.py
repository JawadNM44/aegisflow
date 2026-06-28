"""Simple in-memory rate limiter middleware for API protection."""
import time
from collections import defaultdict
from fastapi import Request, HTTPException

class RateLimiter:
    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: dict[str, list[float]] = defaultdict(list)

    async def __call__(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window_start = now - self.window_seconds
        self.requests[client_ip] = [t for t in self.requests[client_ip] if t > window_start]
        if len(self.requests[client_ip]) >= self.max_requests:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        self.requests[client_ip].append(now)
        return await call_next(request)
