"""
LLM module - Client wrapper for external LLM providers.

The LLM client is used ONLY by agents for reasoning and extraction.
Tools do NOT use the LLM - they are deterministic.
"""

from safety_agent.llm.client import LLMClient

__all__ = ["LLMClient"]
