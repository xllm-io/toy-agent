"""
Toy Agent - A lightweight Agent framework
"""

from .agent import Agent
from .tool_registry import ToolRegistry, Tool, tool
from .llm_client import LLMClient

__all__ = [
    "Agent",
    "ToolRegistry",
    "Tool",
    "tool",
    "LLMClient",
]

__version__ = "0.1.0"

