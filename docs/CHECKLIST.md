# Engineering Quality Checklist: Data_Collector

- [x] Zero external dependencies required for core functionality (uses standard lib + optional psutil/requests).
- [x] Complies with `docs/guidelines/file_structuring.md`.
- [x] All paths reside in `E:\ARIA FILES\Projects\Data_Collector`.
- [x] Standard envelope pattern on all collector outputs (`source`, `status`, `timestamp`, `latency_ms`, `data`).
- [x] Atomic writes with fsync on all database persistence.
- [x] GAIA Test Suite fully passing (9/9 tests green).
- [x] Read-only permission enforced on QA test suite file.
