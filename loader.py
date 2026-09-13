#!/usr/bin/env python3
"""Compatibility loader for ShadowVoid.

Remote payload download, self-deletion, arbitrary ``exec``, and temporary-file
fallbacks were removed.  The old loader was a dropper, not a dependable module
loader, and could execute unauthenticated bytes from the network.
"""

from __future__ import annotations

import sys
from typing import Any


CONFIG: dict[str, Any] = {
    "payload_url": None,
    "memory_only": False,
    "self_destruct": False,
}


def scrub_tracks() -> bool:
    """Retained for compatibility; never alters user history or files."""

    return False


def download_payload(url: str) -> bytes:
    raise RuntimeError("remote payload loading is disabled")


def decrypt_payload(encrypted_data: bytes, key: bytes) -> bytes:
    raise RuntimeError("payload execution is disabled")


def execute_in_memory(code_string: str, globals_dict: dict[str, Any] | None = None) -> bool:
    """Reject arbitrary source execution rather than silently running it."""

    return False


def execute_payload_memory(payload: bytes) -> bool:
    return False


def execute_payload(payload: bytes) -> bool:
    return False


def get_key() -> bytes:
    raise RuntimeError("static payload keys are not supported")


def main(argv: list[str] | None = None) -> int:
    """Delegate to the normal local CLI without downloading a payload."""

    from core import main as core_main

    return core_main(sys.argv[1:] if argv is None else argv)


if __name__ == "__main__":
    raise SystemExit(main())
