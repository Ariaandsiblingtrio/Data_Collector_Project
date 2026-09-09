"""
pipeline/storage.py — Atomic Data Storage & Cryptographic Ledger Audit
Author: Aria & GAIA
"""

import os
import json
import time
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

class DataStorage:
    """
    Manages atomic writing of collected datasets into database/data_store.json,
    computes SHA-256 cryptographic verification receipts, and records to project ledger.
    """
    def __init__(self, db_dir: Optional[str] = None):
        self.db_dir = db_dir or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "database")
        os.makedirs(self.db_dir, exist_ok=True)
        self.data_store_file = os.path.join(self.db_dir, "data_store.json")
        self.ledger_file = os.path.join(self.db_dir, "project_ledger.json")

    def _atomic_write(self, filepath: str, content: str) -> None:
        tmp_path = f"{filepath}.tmp_{int(time.time() * 1000)}"
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, filepath)

    def generate_receipt(self, records_batch: Dict[str, Any]) -> str:
        serialized = json.dumps(records_batch, sort_keys=True)
        h = hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:16].upper()
        return f"TXN_{h}"

    def store_dataset(self, dataset: Dict[str, Any]) -> Dict[str, Any]:
        """
        Appends or writes dataset to data_store.json and updates project ledger with receipt.
        """
        receipt = self.generate_receipt(dataset)
        record_envelope = {
            "receipt": receipt,
            "stored_at": datetime.now(timezone.utc).isoformat(),
            "dataset": dataset
        }

        # Load existing store
        existing_data = []
        if os.path.exists(self.data_store_file):
            try:
                with open(self.data_store_file, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
                    if not isinstance(existing_data, list):
                        existing_data = [existing_data]
            except Exception:
                existing_data = []

        existing_data.append(record_envelope)
        self._atomic_write(self.data_store_file, json.dumps(existing_data, indent=2))

        # Update project ledger
        ledger_data = {
            "status": "COMPLETED",
            "project_name": "Data_Collector",
            "last_receipt": receipt,
            "total_stored_batches": len(existing_data),
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "deliverables": [
                "src/main_module.py",
                "src/collectors/system_collector.py",
                "src/collectors/file_collector.py",
                "src/collectors/web_collector.py",
                "src/collectors/adk_collector.py",
                "tests/test_data_collector.py",
                "database/data_store.json",
                "database/project_ledger.json"
            ]
        }
        self._atomic_write(self.ledger_file, json.dumps(ledger_data, indent=2))

        return {
            "status": "SUCCESS",
            "receipt": receipt,
            "filepath": self.data_store_file,
            "total_batches": len(existing_data)
        }
