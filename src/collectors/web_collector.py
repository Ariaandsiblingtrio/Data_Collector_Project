"""
collectors/web_collector.py — Web & REST API Data Ingestion Engine
Author: Aria (Lead Developer)
"""

from typing import Dict, Any, Optional
from datetime import datetime, timezone
import json
from .base import BaseCollector

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

class WebCollector(BaseCollector):
    """
    Ingests web endpoints and REST APIs with configurable timeout,
    retries, and safe offline mock fallback for zero-network environments.
    """
    def __init__(self):
        super().__init__("web_api")

    def collect_raw(self, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        cfg = config or {}
        url = cfg.get("url")
        method = cfg.get("method", "GET").upper()
        headers = cfg.get("headers", {"User-Agent": "AriaDataCollector/1.0"})
        timeout = cfg.get("timeout", 5)
        offline_mock = cfg.get("offline_mock", False)

        # Built-in offline mock feed if requested or if no URL specified
        if offline_mock or not url:
            return {
                "source_type": "offline_mock",
                "simulated_endpoint": "https://api.aria.local/telemetry/sample",
                "status_code": 200,
                "payload": {
                    "sensor_network": "Aria_IoT_Grid",
                    "metrics": [
                        {"node": "alpha_1", "temperature_c": 21.4, "humidity_pct": 45.2},
                        {"node": "beta_2", "temperature_c": 22.1, "humidity_pct": 43.8}
                    ],
                    "heartbeat": datetime.now(timezone.utc).isoformat()
                }
            }

        if not HAS_REQUESTS:
            raise RuntimeError("The 'requests' package is required for live HTTP calls.")

        resp = requests.request(method=method, url=url, headers=headers, timeout=timeout)
        is_json = "application/json" in resp.headers.get("Content-Type", "")
        payload = resp.json() if is_json else resp.text[:2048]

        return {
            "source_type": "live_http",
            "url": url,
            "status_code": resp.status_code,
            "headers": dict(resp.headers),
            "payload": payload
        }
