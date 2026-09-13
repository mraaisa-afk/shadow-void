"""Read-only process inventory for ShadowVoid.

Process injection, migration, preload tricks, and payload spawning were removed.
This module only exposes non-invasive process metadata useful for diagnostics.
"""

from __future__ import annotations

import os
import platform
import shutil
from datetime import datetime, timezone
from typing import Any

from ._safe import blocked


class ProcessInjector:
    """Compatibility API whose only active operation is process listing."""

    def __init__(self, core=None):
        self.core = core
        self.current_pid = os.getpid()
        self.libc = None
        self.libc_path = None

    @staticmethod
    def _read_status(pid: int) -> dict[str, str]:
        values: dict[str, str] = {}
        try:
            with open(f"/proc/{pid}/status", encoding="utf-8") as handle:
                for line in handle:
                    key, separator, value = line.partition(":")
                    if separator:
                        values[key] = value.strip()
        except (OSError, UnicodeError):
            pass
        return values

    def find_process(self, name: str) -> int | None:
        name = str(name)
        for process in self.get_process_list():
            if process["name"] == name or name in process["cmdline"]:
                return process["pid"]
        return None

    def _find_process_manual(self, name: str) -> int | None:
        return self.find_process(name)

    def get_process_list(self) -> list[dict[str, Any]]:
        if platform.system() != "Linux":
            return []
        processes: list[dict[str, Any]] = []
        try:
            entries = os.listdir("/proc")
        except OSError:
            return processes
        for entry in entries:
            if not entry.isdigit():
                continue
            pid = int(entry)
            status = self._read_status(pid)
            if not status:
                continue
            try:
                with open(f"/proc/{pid}/cmdline", "rb") as handle:
                    cmdline = handle.read().replace(b"\0", b" ").decode("utf-8", "replace").strip()
            except OSError:
                cmdline = ""
            processes.append(
                {
                    "pid": pid,
                    "name": status.get("Name", ""),
                    "cmdline": cmdline,
                }
            )
        return sorted(processes, key=lambda item: item["pid"])

    def list_injectable_processes(self) -> list[dict[str, Any]]:
        """List processes as non-injectable diagnostic entries."""

        return [
            {
                **process,
                "uid": self._read_status(process["pid"]).get("Uid", "").split(" ")[0],
                "injectable": False,
            }
            for process in self.get_process_list()
        ]

    def _find_binary_path(self, name: str) -> str | None:
        return shutil.which(name)

    def generate_migration_stub(self, target_path: str | None = None) -> dict[str, Any]:
        return blocked("process migration", target=target_path)

    def migrate_to_process(self, target_name: str = "svchost") -> dict[str, Any]:
        return blocked("process migration", target=target_name)

    def spawn_and_inject(self, target_name: str = "svchost", payload: Any = None) -> dict[str, Any]:
        return blocked("process injection", target=target_name)

    def execute_in_process(self, pid: int, code: str) -> dict[str, Any]:
        return blocked("cross-process code execution", target_pid=pid)

    def substitute_process(self, target_name: str = "svchost") -> dict[str, Any]:
        return blocked("process substitution", target=target_name)

    def _try_ptrace_injection(self, target_pid: int) -> bool:
        return False

    def _try_ld_preload_injection(self, target_pid: int) -> bool:
        return False

    def _try_mem_injection(self, target_pid: int) -> bool:
        return False

    def cleanup(self) -> dict[str, str]:
        return {"status": "success", "message": "No injection artifacts are created in safe mode"}
