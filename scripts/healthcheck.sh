#!/bin/bash
# Docker healthcheck for AEGISFLOW backend
curl -sf http://localhost:8000/health || exit 1
