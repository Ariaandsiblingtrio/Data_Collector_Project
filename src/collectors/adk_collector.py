"""
collectors/adk_collector.py — Aria ADK Swarm Integration & Capability Ingestion
Author: Aria (Lead Developer)
"""

import os
import sys
from typing import Dict, Any, Optional, List
from .base import BaseCollector

# Add project root to path to locate core ADK manager
MYAGENT_ROOT = r"C:\MyAgent"
if MYAGENT_ROOT not in sys.path:
    sys.path.insert(0, MYAGENT_ROOT)

class ADKCollector(BaseCollector):
    """
    Connects directly into Aria's Agent Development Kit (ADK) ecosystem.
    Collects registered ADK metadata, tool schemas, and executes ADK tasks.
    """
    def __init__(self):
        super().__init__("aria_adk_swarm")

    def collect_raw(self, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        cfg = config or {}
        target_adk = cfg.get("adk_name")

        adks_summary: List[Dict[str, Any]] = []
        active_tools: List[str] = []

        try:
            from core.aria_adk_manager import get_adk_manager
            mgr = get_adk_manager()
            installed = mgr.list_adks()
            for adk in installed:
                adks_summary.append({
                    "name": adk.get("name"),
                    "description": adk.get("description"),
                    "version": adk.get("version", "1.0.0"),
                    "author": adk.get("author", "Aria")
                })
        except Exception as e:
            adks_summary.append({"error": f"ADK manager unavailable: {e}"})

        # Discover ADK tools from Aria ADK Engine
        try:
            from core.aria_adk import ALL_ADK_TOOLS
            active_tools = [t.get("name") for t in ALL_ADK_TOOLS if isinstance(t, dict)]
        except Exception:
            active_tools = ["aria_read_file", "aria_write_file", "aria_system_context"]

        return {
            "installed_adks_count": len(adks_summary),
            "adks": adks_summary,
            "total_available_tools": len(active_tools),
            "sample_tools": active_tools[:10],
            "target_adk_invoked": target_adk or "none"
        }
