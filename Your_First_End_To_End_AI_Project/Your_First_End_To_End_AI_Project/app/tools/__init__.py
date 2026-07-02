"""
tools/__init__.py — Tool Registry (Episode 4)
===============================================
4 tools: calculator, weather, wikipedia, converter
"""

from app.tools.calculator import run as calculator_run
from app.tools.weather_api import run as weather_run
from app.tools.wikipedia_tool import run as wikipedia_run
from app.tools.unit_converter import run as converter_run

TOOL_REGISTRY: dict = {
    "calculator": calculator_run,
    "weather": weather_run,
    "wikipedia": wikipedia_run,
    "converter": converter_run,
}

__all__ = ["TOOL_REGISTRY"]
