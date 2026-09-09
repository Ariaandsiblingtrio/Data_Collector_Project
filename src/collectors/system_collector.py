"""
collectors/system_collector.py — Real-time Operating System Telemetry Ingestion
Author: Aria (Lead Developer)
"""

import platform
import os
import sys
from typing import Dict, Any, Optional
from .base import BaseCollector

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

class SystemCollector(BaseCollector):
    """
    Collects live physical hardware and OS telemetry metrics:
    CPU, Memory, Disk partitions, and active host processes.
    """
    def __init__(self):
        super().__init__("system_telemetry")

    def collect_raw(self, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        cfg = config or {}
        include_processes = cfg.get("include_processes", False)
        top_proc_limit = cfg.get("top_proc_limit", 5)

        data = {
            "host": {
                "platform": platform.platform(),
                "node": platform.node(),
                "machine": platform.machine(),
                "python_version": platform.python_version()
            },
            "cpu": {},
            "memory": {},
            "disk": {}
        }

        if HAS_PSUTIL:
            # CPU telemetry
            data["cpu"] = {
                "physical_cores": psutil.cpu_count(logical=False) or 1,
                "logical_cores": psutil.cpu_count(logical=True) or 1,
                "percent_utilization": psutil.cpu_percent(interval=0.05),
                "frequencies_mhz": getattr(psutil.cpu_freq(), "_asdict", lambda: {})() if psutil.cpu_freq() else {}
            }

            # Memory telemetry
            mem = psutil.virtual_memory()
            data["memory"] = {
                "total_bytes": mem.total,
                "available_bytes": mem.available,
                "used_bytes": mem.used,
                "percent_used": mem.percent
            }

            # Disk telemetry (all mounted partitions)
            disks = {}
            for part in psutil.disk_partitions(all=False):
                try:
                    usage = psutil.disk_usage(part.mountpoint)
                    disks[part.mountpoint] = {
                        "device": part.device,
                        "fstype": part.fstype,
                        "total_bytes": usage.total,
                        "used_bytes": usage.used,
                        "free_bytes": usage.free,
                        "percent_used": usage.percent
                    }
                except (PermissionError, OSError):
                    continue
            data["disk"] = disks

            # Optional: Top memory processes
            if include_processes:
                procs = []
                for p in sorted(psutil.process_iter(["pid", "name", "memory_percent"]), 
                                key=lambda x: x.info.get("memory_percent") or 0, 
                                reverse=True)[:top_proc_limit]:
                    procs.append({
                        "pid": p.info.get("pid"),
                        "name": p.info.get("name"),
                        "memory_percent": round(p.info.get("memory_percent") or 0.0, 2)
                    })
                data["top_processes"] = procs
        else:
            # Standard library fallback
            data["cpu"] = {"logical_cores": os.cpu_count() or 1, "note": "psutil not available"}
            data["memory"] = {"note": "psutil not available"}
            data["disk"] = {"note": "psutil not available"}

        return data
