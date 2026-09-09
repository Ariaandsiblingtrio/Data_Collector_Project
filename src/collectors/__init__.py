"""
collectors/__init__.py
"""
from .base import BaseCollector
from .system_collector import SystemCollector
from .file_collector import FileCollector
from .web_collector import WebCollector
from .adk_collector import ADKCollector

__all__ = [
    "BaseCollector",
    "SystemCollector",
    "FileCollector",
    "WebCollector",
    "ADKCollector"
]
