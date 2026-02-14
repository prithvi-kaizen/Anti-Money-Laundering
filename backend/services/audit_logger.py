"""
Sentinel AML — Audit Logger
In-memory audit trail for investigation transparency.
"""

import time
import uuid
from datetime import datetime, timezone


# In-memory audit store: alert_id -> list[AuditEntry]
_audit_store: dict[str, list[dict]] = {}


def log_action(alert_id: str, action: str, module: str,
               input_summary: str, output_summary: str,
               evidence_ids: list[str] = None,
               duration_ms: int = 0) -> dict:
    """Log an audit entry for an alert investigation."""
    entry = {
        "entry_id": f"AUD-{uuid.uuid4().hex[:8].upper()}",
        "alert_id": alert_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "module": module,
        "input_summary": input_summary,
        "output_summary": output_summary,
        "evidence_ids": evidence_ids or [],
        "duration_ms": duration_ms,
    }

    if alert_id not in _audit_store:
        _audit_store[alert_id] = []
    _audit_store[alert_id].append(entry)

    return entry


def get_audit_trail(alert_id: str) -> dict:
    """Get complete audit trail for an alert."""
    entries = _audit_store.get(alert_id, [])
    total_duration = sum(e.get("duration_ms", 0) for e in entries)
    return {
        "alert_id": alert_id,
        "entries": entries,
        "total_duration_ms": total_duration,
    }


def clear_audit(alert_id: str):
    """Clear audit trail for an alert (for re-investigation)."""
    _audit_store.pop(alert_id, None)


class AuditContext:
    """Context manager for timing and logging audit entries."""

    def __init__(self, alert_id: str, action: str, module: str, input_summary: str):
        self.alert_id = alert_id
        self.action = action
        self.module = module
        self.input_summary = input_summary
        self.start_time = None
        self.entry = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = int((time.time() - self.start_time) * 1000)
        output = f"Error: {exc_val}" if exc_type else "Completed successfully"
        self.entry = log_action(
            self.alert_id, self.action, self.module,
            self.input_summary, output,
            duration_ms=duration_ms,
        )
        return False

    def set_output(self, output_summary: str, evidence_ids: list[str] = None):
        """Set the output summary before exiting context."""
        duration_ms = int((time.time() - self.start_time) * 1000)
        self.entry = log_action(
            self.alert_id, self.action, self.module,
            self.input_summary, output_summary,
            evidence_ids=evidence_ids,
            duration_ms=duration_ms,
        )
