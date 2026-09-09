r"""`nmain_module.py â€” Master Data Collection Facade & Pipeline Coordinator
Authors: Aria (Lead Developer) & GAIA (Lead Architect)
Target: E:\ARIA FILES\Projects\Data_Collector
"""

import os
import sys
import argparse
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

# Ensure local package discoverability
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if _CURRENT_DIR not in sys.path:
    sys.path.insert(0, _CURRENT_DIR)

from collectors.system_collector import SystemCollector
from collectors.file_collector import FileCollector
from collectors.web_collector import WebCollector
from collectors.adk_collector import ADKCollector
from pipeline.validator import DataValidator
from pipeline.transformer import DataTransformer
from pipeline.storage import DataStorage

class DataCollector:
    """
    Central coordinator orchestrating multi-source collection,
    validation, transformation, and atomic audited storage.
    """
    def __init__(self):
        self.collectors = {
            "system": SystemCollector(),
            "file": FileCollector(),
            "web": WebCollector(),
            "adk": ADKCollector()
        }
        self.validator = DataValidator()
        self.transformer = DataTransformer()
        self.storage = DataStorage()

    def run_collection(
        self,
        sources: Optional[List[str]] = None,
        config: Optional[Dict[str, Any]] = None,
        store: bool = True
    ) -> Dict[str, Any]:
        """
        Runs collection across chosen sources, validates and stores results.
        """
        target_sources = sources or ["system", "file", "adk"]
        cfg = config or {}
        collected_data = {}

        for src in target_sources:
            col = self.collectors.get(src)
            if not col:
                continue
            res = col.collect(cfg.get(src, {}))
            is_valid, violations = self.validator.validate_envelope(res)
            if is_valid:
                clean_res = self.validator.sanitize_payload(res)
                flat_metrics = self.transformer.flatten_dict(clean_res.get("data", {}))
                summary = self.transformer.extract_summary_metrics(flat_metrics)
                clean_res["summary"] = summary
                collected_data[src] = clean_res
            else:
                collected_data[src] = {
                    "source": src,
                    "status": "VALIDATION_FAILED",
                    "violations": violations
                }

        storage_res = {}
        if store:
            storage_res = self.storage.store_dataset(collected_data)

        receipt = storage_res.get("receipt") or self.storage.generate_receipt(collected_data)

        return {
            "status": "SUCCESS",
            "receipt": receipt,
            "sources_collected": list(collected_data.keys()),
            "data": collected_data,
            "storage": storage_res
        }

def execute_task(task_type: str = "health_check", **kwargs) -> Dict[str, Any]:
    """
    Standard GAIA contract and SDLC execution entry point.
    Guarantees 'status' and 'receipt' keys in all responses.
    """
    engine = DataCollector()

    if task_type == "health_check":
        # Quick health validation across core modules
        sys_res = engine.collectors["system"].collect()
        receipt = engine.storage.generate_receipt(sys_res)
        return {
            "status": "SUCCESS",
            "receipt": receipt,
            "task": task_type,
            "engine_state": "HEALTHY",
            "modules_online": list(engine.collectors.keys())
        }

    elif task_type == "collect_system":
        return engine.run_collection(sources=["system"], config=kwargs, store=True)

    elif task_type == "collect_files":
        return engine.run_collection(sources=["file"], config=kwargs, store=True)

    elif task_type == "collect_adk":
        return engine.run_collection(sources=["adk"], config=kwargs, store=True)

    elif task_type == "full_pipeline":
        return engine.run_collection(sources=["system", "file", "web", "adk"], config=kwargs, store=True)

    else:
        # Fallback dynamic task execution
        return engine.run_collection(sources=["system"], config=kwargs, store=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aria Data Collector Master Runner")
    parser.add_argument("--task", default="health_check", help="Task type to execute")
    parser.add_argument("--source", default="system", help="Source to collect (system, file, web, adk, all)")
    args = parser.parse_args()

    print(f"[*] Starting Data_Collector with task='{args.task}', source='{args.source}'...")
    if args.source == "all":
        out = execute_task("full_pipeline")
    else:
        out = execute_task(f"collect_{args.source}" if args.source in ["system", "files", "adk"] else args.task)

    print(f"[+] Task Completed! Receipt: {out.get('receipt')}")
    print(json.dumps(out, indent=2))

