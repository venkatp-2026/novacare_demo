"""Audit logging utilities."""
from collections import deque
from datetime import datetime
from typing import Any, Dict, Optional

# Audit log (in-memory ring buffer, max 100 entries)
audit_log = deque(maxlen=100)


def log_event(
    event: str,
    patient_id: Optional[str] = None,
    endpoint: Optional[str] = None,
    actor: Optional[str] = None,
    **kwargs: Any
) -> None:
    """Log an event to the audit log."""
    log_entry: Dict[str, Any] = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": event,
    }
    
    if patient_id:
        log_entry["patient_id"] = patient_id
    if endpoint:
        log_entry["endpoint"] = endpoint
    if actor:
        log_entry["actor"] = actor
    
    # Add any additional fields
    log_entry.update(kwargs)
    
    audit_log.append(log_entry)
