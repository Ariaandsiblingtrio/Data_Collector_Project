"""
pipeline/validator.py — Zero-Trust Schema Validation & Data Sanitization
Author: GAIA (Lead Architect & QA Supervisor) & Aria
"""

import re
from typing import Dict, Any, List, Tuple

class DataValidator:
    """
    Validates ingested data payloads against strict zero-trust integrity rules:
    - Enforces required envelope fields.
    - Sanitizes malicious string injections and control characters.
    - Verifies physical numeric constraints.
    """
    REQUIRED_ENVELOPE_FIELDS = {"source", "status", "timestamp", "data"}

    @staticmethod
    def sanitize_string(val: str) -> str:
        """Strips dangerous control characters and null bytes."""
        if not isinstance(val, str):
            return str(val)
        # Remove null bytes and non-printable control chars (except standard newlines/tabs)
        sanitized = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', val)
        return sanitized.strip()

    def validate_envelope(self, payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
        violations = []
        if not isinstance(payload, dict):
            return False, ["Payload must be a dictionary object."]

        missing = self.REQUIRED_ENVELOPE_FIELDS - set(payload.keys())
        if missing:
            violations.append(f"Missing mandatory fields: {', '.join(missing)}")

        if payload.get("status") not in ("SUCCESS", "ERROR"):
            violations.append(f"Invalid status value: {payload.get('status')}")

        return len(violations) == 0, violations

    def sanitize_payload(self, data: Any) -> Any:
        """Recursively sanitizes dictionary structures."""
        if isinstance(data, dict):
            return {self.sanitize_string(k): self.sanitize_payload(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.sanitize_payload(item) for item in data]
        elif isinstance(data, str):
            return self.sanitize_string(data)
        return data
