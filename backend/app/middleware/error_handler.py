"""Global exception handler middleware for consistent error responses."""
from fastapi import Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger("aegisflow")

async def global_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(f"Unhandled error on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "path": request.url.path},
    )
