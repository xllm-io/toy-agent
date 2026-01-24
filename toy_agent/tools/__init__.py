"""
Tool collection for toy-agent
提供各种工具的统一导出
"""
from toy_agent.tools.calculator import calculator
from toy_agent.tools.weather import get_weather
from toy_agent.tools.search import search_web
from toy_agent.tools.file_ops import read_file, multi_edit
from toy_agent.tools.apply_patch import apply_patch

__all__ = [
    "calculator",
    "get_weather", 
    "search_web",
    "read_file",
    "multi_edit",
    "apply_patch",
]

