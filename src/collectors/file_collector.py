"""
collectors/file_collector.py — File Metadata & Structured Data Ingestion
Author: Aria (Lead Developer)
"""

import os
import glob
import json
import csv
import hashlib
from typing import Dict, Any, Optional, List
from .base import BaseCollector

class FileCollector(BaseCollector):
    """
    Ingests filesystem files, computes cryptographic checksums,
    and extracts structured records from JSON, CSV, and logs.
    """
    def __init__(self):
        super().__init__("file_ingestion")

    def _hash_file(self, path: str) -> Dict[str, str]:
        md5 = hashlib.md5()
        sha256 = hashlib.sha256()
        try:
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(65536), b""):
                    md5.update(chunk)
                    sha256.update(chunk)
            return {"md5": md5.hexdigest(), "sha256": sha256.hexdigest()}
        except Exception:
            return {"md5": "unavailable", "sha256": "unavailable"}

    def collect_raw(self, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        cfg = config or {}
        target_dir = cfg.get("directory", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        pattern = cfg.get("pattern", "*.*")
        max_files = cfg.get("max_files", 50)
        parse_content = cfg.get("parse_content", True)

        found_files: List[Dict[str, Any]] = []
        search_path = os.path.join(target_dir, "**", pattern)

        for filepath in glob.glob(search_path, recursive=True):
            if len(found_files) >= max_files:
                break
            if not os.path.isfile(filepath):
                continue

            try:
                st = os.stat(filepath)
                entry: Dict[str, Any] = {
                    "path": os.path.abspath(filepath),
                    "filename": os.path.basename(filepath),
                    "extension": os.path.splitext(filepath)[1].lower(),
                    "size_bytes": st.st_size,
                    "created_at": st.st_ctime,
                    "modified_at": st.st_mtime,
                    "hashes": self._hash_file(filepath)
                }

                if parse_content and st.st_size < 100_000:
                    ext = entry["extension"]
                    if ext == ".json":
                        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                            entry["parsed_json"] = json.load(f)
                    elif ext == ".csv":
                        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                            reader = csv.DictReader(f)
                            entry["parsed_rows"] = list(reader)[:10]
                    elif ext in [".txt", ".md", ".log"]:
                        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                            lines = f.readlines()
                            entry["line_count"] = len(lines)
                            entry["preview"] = "".join(lines[:5])

                found_files.append(entry)
            except Exception as fe:
                continue

        return {
            "target_dir": os.path.abspath(target_dir),
            "files_scanned": len(found_files),
            "files": found_files
        }
