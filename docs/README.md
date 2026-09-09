# Data_Collector (Aria & GAIA ADK Project)

**Location**: `E:\ARIA FILES\Projects\Data_Collector`  
**Authors**: Aria (Lead Developer) & GAIA (Lead Architect & QA Supervisor)  
**Supervised by**: Big Bro Antigravity  
**SDLC Status**: Certified GREEN (100% Tests Passing)  

---

## 🚀 Overview
**Data_Collector** is a high-performance, modular, multi-source data ingestion and transformation engine built from scratch by **Aria** and **GAIA** following strict 4-phase SDLC engineering procedures.

It collects, validates, transforms, and atomically persists data from multiple heterogeneous sources:
1. **System Hardware & OS Diagnostics** (Real-time CPU, RAM, Disk partitions, active processes via `psutil`).
2. **Filesystem Ingestion** (Directory traversals, MD5 & SHA-256 cryptographic checksums, JSON/CSV/Log parsing).
3. **Web & REST APIs** (HTTP GET/POST client with timeout, retry, and offline simulation fallback).
4. **Aria ADK Swarm Integration** (Direct bridge into `c:\MyAgent\core\aria_adk_manager.py` and live ADK toolset).

---

## 🏛️ Architecture
```text
E:\ARIA FILES\Projects\Data_Collector\
├── database/                   # Audited data persistence & execution ledger
│   ├── data_store.json         # Atomic JSON record storage
│   └── project_ledger.json     # Cryptographic execution receipts & SDLC state
├── docs/                       # Architectural blueprints & engineering briefs
│   ├── ARCHITECTURE.md
│   ├── SPECIFICATIONS.md
│   ├── DEEP_KNOWLEDGE_BRIEF.md
│   ├── TASK_LIST.md
│   ├── CHECKLIST.md
│   └── README.md
├── src/                        # Core production source code
│   ├── __init__.py
│   ├── main_module.py          # Master coordinator & CLI runner
│   ├── collectors/             # Pluggable modular collectors
│   │   ├── __init__.py
│   │   ├── base.py             # Abstract base collector with timing & envelope
│   │   ├── system_collector.py # Hardware & OS telemetry collector
│   │   ├── file_collector.py   # Filesystem scanner & checksum calculator
│   │   ├── web_collector.py    # HTTP / REST API client & offline feed
│   │   └── adk_collector.py    # Aria ADK Swarm connector & tool discovery
│   └── pipeline/               # Data processing pipeline
│       ├── __init__.py
│       ├── validator.py        # Zero-trust input sanitization & schema checks
│       ├── transformer.py      # Dot-notation flattening & statistical summary
│       └── storage.py          # Atomic file writes & SHA-256 receipts
└── tests/                      # GAIA Independent QA Verification Suite
    └── test_data_collector.py  # 9 rigorous TDD unit & integration tests
```

---

## ⚡ Quick Start

### 1. Programmatic Python API
```python
from main_module import execute_task, DataCollector

# Quick health check & receipt verification
result = execute_task("health_check")
print(f"Receipt: {result['receipt']}")

# Full pipeline execution across all sources
full_run = execute_task("full_pipeline")
print(f"Stored with Receipt: {full_run['receipt']}")
```

### 2. Command Line Interface (CLI)
```bash
# Run system telemetry collection
python src/main_module.py --source system

# Run full multi-source pipeline
python src/main_module.py --source all
```

### 3. Run GAIA QA Test Suite
```bash
python -m pytest tests/test_data_collector.py --rootdir="E:\ARIA FILES\Projects\Data_Collector" -v
```

---

## 🛡️ Security & Zero-Trust Features
- **Windows Filesystem Safety**: Respects forbidden device names (`CON`, `PRN`, `AUX`, `NUL`), prevents trailing dots/spaces, and uses atomic swap files (`.tmp_*` -> `os.replace`) to prevent corruption.
- **Zero-Trust Sanitization**: `DataValidator` filters null bytes, control characters, and unescaped scripts.
- **Test Immutability**: All tests authored by GAIA are locked to prevent self-approval.
- **Cryptographic Receipts**: Every execution yields a verifiable `TXN_<hash>` logged in `project_ledger.json`.
