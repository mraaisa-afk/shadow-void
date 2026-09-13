"""Shared helpers for safe, non-invasive module shims."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def blocked(action: str, **details: Any) -> dict[str, Any]:
    result: dict[str, Any] = {
        "status": "blocked",
        "action": action,
        "message": f"{action} is disabled in safe mode",
        "timestamp": timestamp(),
    }
    result.update(details)
    return result
