"""
tests/test_data_collector.py — GAIA Independent Verification Suite for Data_Collector
Author: Big Sister GAIA (Supervisor & Lead Architect)
Mandate: Strict Red-Green TDD verification & multi-source system audit.
"""

import sys
import os
import pytest

# Ensure src/ is on sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from main_module import execute_task, DataCollector
from collectors.system_collector import SystemCollector
from collectors.file_collector import FileCollector
from collectors.web_collector import WebCollector
from collectors.adk_collector import ADKCollector
from pipeline.validator import DataValidator
from pipeline.transformer import DataTransformer
from pipeline.storage import DataStorage

def test_primary_contract():
    """Verifies standard GAIA contract: status SUCCESS and valid receipt."""
    res = execute_task("health_check")
    assert res.get("status") == "SUCCESS", f"Expected SUCCESS, got {res}"
    assert "receipt" in res, "Missing receipt in task execution result!"
    assert res["receipt"].startswith("TXN_"), f"Invalid receipt format: {res['receipt']}"
    assert len(res.get("modules_online", [])) >= 4

def test_system_collector():
    """Verifies live physical CPU, memory, and disk telemetry collection."""
    collector = SystemCollector()
    res = collector.collect()
    assert res["status"] == "SUCCESS"
    assert res["source"] == "system_telemetry"
    assert "cpu" in res["data"]
    assert "memory" in res["data"]
    assert "disk" in res["data"]
    assert res["latency_ms"] >= 0

def test_file_collector():
    """Verifies file scanning, hashing, and structured parsing."""
    collector = FileCollector()
    # Scan the project's docs folder
    docs_dir = os.path.join(PROJECT_ROOT, "docs")
    res = collector.collect({"directory": docs_dir, "pattern": "*.md"})
    assert res["status"] == "SUCCESS"
    assert res["data"]["files_scanned"] > 0
    first_file = res["data"]["files"][0]
    assert "hashes" in first_file
    assert "sha256" in first_file["hashes"]

def test_web_collector_offline_mode():
    """Verifies web collector offline simulation and graceful fallback."""
    collector = WebCollector()
    res = collector.collect({"offline_mock": True})
    assert res["status"] == "SUCCESS"
    assert res["data"]["source_type"] == "offline_mock"
    assert "sensor_network" in res["data"]["payload"]

def test_adk_collector():
    """Verifies Aria ADK swarm discovery and tool listing."""
    collector = ADKCollector()
    res = collector.collect()
    assert res["status"] == "SUCCESS"
    assert "installed_adks_count" in res["data"]
    assert "total_available_tools" in res["data"]

def test_pipeline_validator():
    """Verifies zero-trust input validation and string sanitization."""
    validator = DataValidator()
    # Test valid envelope
    valid_env = {"source": "test", "status": "SUCCESS", "timestamp": "2026-09-09T00:00:00Z", "data": {"a": 1}}
    ok, violations = validator.validate_envelope(valid_env)
    assert ok is True
    assert len(violations) == 0

    # Test dangerous injection sanitization
    dirty = {"key\x00": "evil\x08data", "normal": "safe"}
    cleaned = validator.sanitize_payload(dirty)
    assert "\x00" not in list(cleaned.keys())[0]
    assert "\x08" not in cleaned["normal"]

def test_pipeline_transformer():
    """Verifies dictionary flattening and numerical metric extraction."""
    transformer = DataTransformer()
    nested = {"level1": {"level2": {"metric": 42, "ratio": 3.14}}, "status": "active"}
    flat = transformer.flatten_dict(nested)
    assert "level1.level2.metric" in flat
    assert flat["level1.level2.metric"] == 42

    metrics = transformer.extract_summary_metrics(flat)
    assert metrics["numeric_fields"] == 2
    assert metrics["min_val"] == 3.14
    assert metrics["max_val"] == 42.0

def test_storage_and_receipt_generation():
    """Verifies atomic database persistence and ledger record update."""
    storage = DataStorage()
    sample_dataset = {"test_batch": 1, "value": "omega_reading"}
    res = storage.store_dataset(sample_dataset)
    assert res["status"] == "SUCCESS"
    assert res["receipt"].startswith("TXN_")
    assert os.path.exists(res["filepath"])

def test_end_to_end_pipeline():
    """Runs complete end-to-end multi-source ingestion cycle."""
    engine = DataCollector()
    res = engine.run_collection(sources=["system", "adk"], store=True)
    assert res["status"] == "SUCCESS"
    assert "receipt" in res
    assert "system" in res["sources_collected"]
    assert "adk" in res["sources_collected"]
    assert "system_telemetry" == res["data"]["system"]["source"]
