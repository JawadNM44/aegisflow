"""Logging configuration for AEGISFLOW services."""
import logging
import sys

def setup_logging(level: str = "INFO"):
    fmt = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(fmt))
    root = logging.getLogger("aegisflow")
    root.setLevel(getattr(logging, level.upper(), logging.INFO))
    root.addHandler(handler)
    return root
