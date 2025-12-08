"""
API module for Safety Agent.

Exposes the FastAPI application for serving the safety observation pipeline.
"""

from safety_agent.api.server import app

__all__ = ["app"]
