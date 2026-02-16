# API module
"""API routers for CyberDemo backend."""

from .router import api_router
from .health import router as health_router
from .gen import router as gen_router

__all__ = ["api_router", "health_router", "gen_router"]
