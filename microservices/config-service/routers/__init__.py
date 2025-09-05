"""
Configuration Service API Routers
"""
from .configuration_router import router as configuration_router
from .feature_flag_router import router as feature_flag_router
from .discovery_router import router as discovery_router

__all__ = [
    "configuration_router",
    "feature_flag_router",
    "discovery_router"
]