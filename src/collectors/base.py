"""
collectors/base.py — Abstract Base Collector for Data_Collector
Author: Aria (Lead Developer)
Supervised by: GAIA & Big Bro Antigravity
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import time

class BaseCollector(ABC):
    """
    Abstract contract for all modular data collectors.
    Guarantees standard envelope, latency tracking, and error resilience.
    """
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def collect_raw(self, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Subclasses must implement actual retrieval logic."""
        pass

    def collect(self, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Standard execution envelope with timing and zero-crash error containment.
        """
        start_t = time.perf_counter()
        now_iso = datetime.now(timezone.utc).isoformat()
        try:
            payload = self.collect_raw(config or {})
            elapsed_ms = round((time.perf_counter() - start_t) * 1000, 2)
            record_count = len(payload) if isinstance(payload, (list, dict)) else 1
            return {
                "source": self.name,
                "status": "SUCCESS",
                "timestamp": now_iso,
                "latency_ms": elapsed_ms,
                "record_count": record_count,
                "data": payload,
                "error": None
            }
        except Exception as e:
            elapsed_ms = round((time.perf_counter() - start_t) * 1000, 2)
            return {
                "source": self.name,
                "status": "ERROR",
                "timestamp": now_iso,
                "latency_ms": elapsed_ms,
                "record_count": 0,
                "data": {},
                "error": str(e)
            }
