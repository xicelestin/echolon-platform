"""
Telemetry-lite: internal logging to help iterate on UX.
No external API — logs to console or local file in dev.
Tracks: disabled modules (missing columns), validation failures, recommendation triggers.
"""
import os
import json
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

_LOG_FILE = os.environ.get("ECHOLON_TELEMETRY_LOG", "")
_DEV = bool(os.environ.get("ECHOLON_DEV"))


def _log(event: str, data: Optional[Dict[str, Any]] = None):
    """Log event to console (dev) and optionally to file."""
    entry = {
        "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "event": event,
        **(data or {}),
    }
    if _DEV:
        print(f"[echolon] {entry['event']}: {json.dumps({k: v for k, v in entry.items() if k != 'ts'})}")
    if _LOG_FILE:
        try:
            with open(_LOG_FILE, "a") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception:
            pass


def log_module_disabled(module: str, reason: str, missing_columns: Optional[List[str]] = None):
    """Log when a module is disabled due to missing columns."""
    _log("module_disabled", {"module": module, "reason": reason, "missing_columns": missing_columns or []})


def log_validation_failure(check: str, message: str, status: str = "warn"):
    """Log validation check failures."""
    _log("validation_failure", {"check": check, "message": message, "status": status})


def log_recommendation_fired(recommendation_id: str, metric: str, value: Any = None):
    """Log when a recommendation is shown to the user."""
    _log("recommendation_fired", {"id": recommendation_id, "metric": metric, "value": value})
