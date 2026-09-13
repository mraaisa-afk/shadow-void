#!/usr/bin/env python3
"""ShadowVoid core.

ShadowVoid is intentionally limited to local, read-only security assessment and
training helpers.  Earlier revisions bundled a downloader, persistence,
anti-forensics, C2, process injection, and active attack code.  Those features
were both unsafe and unreliable, so the core now provides a small deterministic
command runner and explicitly blocks actions that modify or access other
systems.
"""

from __future__ import annotations

import hashlib
import json
import os
import random
import shlex
import string
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path
from types import ModuleType
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parent

CONFIG: dict[str, Any] = {
    "framework": {
        "name": "ShadowVoid",
        "version": "1.0.0-safe",
        "author": "ShadowVoid",
        "safe_mode": True,
        "debug": False,
    },
    "stealth": {
        "process_name": None,
        "hide_from_ps": False,
        "scrub_history": False,
        "clear_screen": False,
        "anti_debug": False,
        "anti_sandbox": False,
        "timestomping": False,
    },
    "c2": {
        "enabled": False,
        "dga": {"enabled": False, "domains_per_day": 0, "tlds": []},
        "routing": {"tor": False, "i2p": False, "socks5": ""},
        "heartbeat": {"interval": 300, "jitter": 0, "kill_switch": 0},
    },
    "modules": {
        name: {"enabled": True, "path": f"modules/{name}.py"}
        for name in (
            "recon",
            "exploit",
            "auth",
            "wireless",
            "net",
            "web",
            "onion",
            "post_exploit",
            "process_injection",
        )
    },
    "logging": {"enabled": True},
}

SESSION: dict[str, Any] = {
    "active": False,
    "start_time": None,
    "targets": [],
    "compromised": [],
    "last_heartbeat": None,
    "kill_switch_triggered": False,
}

MODULES: dict[str, ModuleType] = {}
MODULE_SOURCE_CACHE: dict[str, str] = {}
_MEMORY_LOADER = None


def _module_path(name: str, configured_path: str | None = None) -> Path:
    """Resolve a module path from either slash or dotted configuration.

    The old loader appended ``.py`` to ``modules.recon`` and looked for a file
    named ``modules.recon.py``.  Accepting both forms keeps configuration
    backwards compatible while resolving the actual package path correctly.
    """

    raw = configured_path or f"modules/{name}.py"
    path = Path(raw)
    if path.suffix != ".py":
        path = Path(str(path).replace(".", "/") + ".py")
    if not path.is_absolute():
        path = ROOT / path
    return path.resolve()


def load_module_from_memory(name: str, source_code: str) -> ModuleType | None:
    """Load trusted repository source from the in-memory source cache.

    This helper is retained for API compatibility, but it no longer hides
    failures or leaves a partially initialized module in ``sys.modules``.
    """

    module_name = name if "." in name else f"modules.{name}"
    module = ModuleType(module_name)
    module.__file__ = f"<memory:{module_name}>"
    module.__package__ = module_name.rpartition(".")[0]
    try:
        code = compile(source_code, module.__file__, "exec")
        sys.modules[module_name] = module
        exec(code, module.__dict__)
        return module
    except Exception:
        sys.modules.pop(module_name, None)
        return None


def make_memory_resident() -> bool:
    """Install an idempotent finder for cached repository modules.

    Python's legacy ``find_module`` API was removed from several import paths;
    this implementation uses the modern finder protocol and never installs a
    duplicate finder on repeated initialization.
    """

    global _MEMORY_LOADER
    if _MEMORY_LOADER is not None:
        return True

    import importlib.abc
    import importlib.machinery

    class MemoryLoader(importlib.abc.Loader):
        def create_module(self, spec):
            return None

        def exec_module(self, module):
            source = MODULE_SOURCE_CACHE.get(module.__name__.split(".")[-1])
            if source is None:
                raise ImportError(f"Module {module.__name__} is not cached")
            exec(compile(source, f"<memory:{module.__name__}>", "exec"), module.__dict__)

    class MemoryFinder(importlib.abc.MetaPathFinder):
        def find_spec(self, fullname, path=None, target=None):
            short_name = fullname.split(".")[-1]
            if fullname.startswith("modules.") and short_name in MODULE_SOURCE_CACHE:
                return importlib.machinery.ModuleSpec(fullname, MemoryLoader())
            return None

    _MEMORY_LOADER = MemoryFinder()
    sys.meta_path.insert(0, _MEMORY_LOADER)
    return True


def execute_in_memory(code_string: str, globals_dict: dict[str, Any] | None = None) -> bool:
    """Reject arbitrary code execution.

    The previous implementation exposed ``exec`` as a public payload runner.
    Keeping the function as a compatibility shim prevents callers from silently
    executing untrusted input.
    """

    return False


def cache_module_in_memory(module_name: str, module_path: str | os.PathLike[str]) -> bool:
    """Cache a repository module's source and return whether it was readable."""

    path = Path(module_path)
    try:
        if not path.is_file():
            return False
        MODULE_SOURCE_CACHE[module_name.split(".")[-1]] = path.read_text(encoding="utf-8")
        return True
    except (OSError, UnicodeError):
        return False


def load_modules() -> dict[str, ModuleType]:
    """Load every enabled module and return a fresh registry.

    Modules are loaded under their package-qualified names, so loading a module
    called ``net`` cannot overwrite an unrelated top-level ``net`` module.
    Failed modules are omitted and reported in ``MODULE_LOAD_ERRORS``.
    """

    MODULES.clear()
    MODULE_LOAD_ERRORS.clear()
    for name, config in CONFIG["modules"].items():
        if not config.get("enabled", False):
            continue
        path = _module_path(name, config.get("path"))
        try:
            path.relative_to(ROOT)
        except ValueError:
            MODULE_LOAD_ERRORS[name] = "module path escapes the repository"
            continue
        if not cache_module_in_memory(name, path):
            MODULE_LOAD_ERRORS[name] = f"module file not found: {path}"
            continue
        source = MODULE_SOURCE_CACHE[name]
        module = load_module_from_memory(f"modules.{name}", source)
        if module is None:
            MODULE_LOAD_ERRORS[name] = "module failed to initialize"
            continue
        MODULES[name] = module
    return dict(MODULES)


MODULE_LOAD_ERRORS: dict[str, str] = {}


# The following names remain as harmless compatibility shims.  They deliberately
# do not modify files, process metadata, timestamps, logs, or debugger state.
def camouflage_process(new_name: str = "") -> bool:
    return False


def hide_from_ps() -> bool:
    return False


def scrub_history() -> bool:
    return False


def clear_screen() -> bool:
    return False


def timestomping(filepath: str | os.PathLike[str]) -> bool:
    return False


def anti_debug_check() -> bool:
    return False


def anti_sandbox_check() -> bool:
    return False


def log_tampering() -> bool:
    return False


def secure_delete(filepath: str | os.PathLike[str]) -> bool:
    return False


class AES256GCM:
    """Small AES-GCM wrapper with strict validation.

    PyCryptodome is an explicit dependency for this class.  The old XOR
    fallback was not encryption and made callers believe their data was safe;
    it has been removed rather than silently weakening security.
    """

    nonce_size = 12
    tag_size = 16
    key_size = 32

    def __init__(self, key: bytes):
        if not isinstance(key, bytes) or len(key) != self.key_size:
            raise ValueError("AES-256-GCM requires a 32-byte key")
        self.key = key

    @staticmethod
    def _aes():
        try:
            from Crypto.Cipher import AES
        except ImportError as exc:
            raise RuntimeError(
                "AES-256-GCM requires pycryptodome; install requirements.txt"
            ) from exc
        return AES

    def encrypt(self, plaintext: bytes | str) -> bytes:
        if isinstance(plaintext, str):
            plaintext = plaintext.encode("utf-8")
        if not isinstance(plaintext, bytes):
            raise TypeError("plaintext must be bytes or str")
        AES = self._aes()
        nonce = os.urandom(self.nonce_size)
        cipher = AES.new(self.key, AES.MODE_GCM, nonce=nonce)
        ciphertext, tag = cipher.encrypt_and_digest(plaintext)
        return nonce + tag + ciphertext

    def decrypt(self, ciphertext: bytes | str) -> bytes:
        if isinstance(ciphertext, str):
            ciphertext = ciphertext.encode("utf-8")
        if not isinstance(ciphertext, bytes):
            raise TypeError("ciphertext must be bytes or str")
        if len(ciphertext) < self.nonce_size + self.tag_size:
            raise ValueError("ciphertext is truncated")
        AES = self._aes()
        nonce = ciphertext[: self.nonce_size]
        tag = ciphertext[self.nonce_size : self.nonce_size + self.tag_size]
        body = ciphertext[self.nonce_size + self.tag_size :]
        cipher = AES.new(self.key, AES.MODE_GCM, nonce=nonce)
        return cipher.decrypt_and_verify(body, tag)


def generate_key(length: int = 32) -> bytes:
    if length <= 0:
        raise ValueError("key length must be positive")
    return os.urandom(length)


class DomainGenerator:
    """Deterministic domain-name generator for offline test fixtures only."""

    def __init__(self, domains_per_day: int = 1000, tlds: Iterable[str] | None = None):
        if not isinstance(domains_per_day, int) or domains_per_day < 0:
            raise ValueError("domains_per_day must be a non-negative integer")
        self.domains_per_day = min(domains_per_day, 10_000)
        if isinstance(tlds, str):
            raise ValueError("tlds must be an iterable of strings, not a string")
        self.tlds = tuple(tlds or ("example",))
        if not self.tlds or any(not isinstance(tld, str) or not tld for tld in self.tlds):
            raise ValueError("tlds must contain non-empty strings")

    def generate_domains(self, count: int = 10) -> list[str]:
        if not isinstance(count, int) or count < 0 or count > 10_000:
            raise ValueError("count must be between 0 and 10000")
        day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        seed = int.from_bytes(hashlib.sha256(day.encode("ascii")).digest()[:8], "big")
        rng = random.Random(seed)
        chars = string.ascii_lowercase + string.digits
        domains: list[str] = []
        for _ in range(count):
            label = "".join(rng.choice(chars) for _ in range(rng.randint(6, 12)))
            domains.append(f"{label}.{rng.choice(self.tlds)}")
        return domains

    def get_daily_domain(self) -> str:
        count = max(self.domains_per_day, 1)
        domains = self.generate_domains(count)
        day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        index = int.from_bytes(hashlib.sha256(day.encode("ascii")).digest()[-8:], "big") % len(domains)
        return domains[index]


class C2Connection:
    """Compatibility object for the retired command-and-control feature."""

    def __init__(self, core=None):
        self.core = core
        self.connected = False
        self.running = False
        self.current_router = None
        self.routers: list[tuple[str, Any]] = []
        self.connection_thread: threading.Thread | None = None

    def initialize_routers(self) -> bool:
        self.routers = []
        return False

    def connect(self) -> bool:
        self.connected = False
        return False

    def make_request(self, *args, **kwargs):
        return None

    def start_persistent_connection(self) -> bool:
        self.running = False
        return False

    def stop(self) -> None:
        self.running = False
        self.connected = False
        self.current_router = None


class TorRouter:
    def __init__(self, socks_port: str = "9050", control_port: str = "9051"):
        self.socks_port = str(socks_port)
        self.control_port = str(control_port)
        self.proxy_url = f"socks5://127.0.0.1:{self.socks_port}"

    def is_available(self) -> bool:
        return False

    def make_request(self, *args, **kwargs):
        return None


class I2PRouter:
    def __init__(self, http_proxy: str = "127.0.0.1:4444"):
        self.http_proxy = http_proxy
        self.proxy_url = f"http://{http_proxy}"

    def is_available(self) -> bool:
        return False

    def make_request(self, *args, **kwargs):
        return None


class DeadDropResolver:
    def resolve(self, service: str, identifier: str):
        return None

    def resolve_pastebin(self, paste_id: str):
        return None

    def resolve_github(self, gist_id: str):
        return None


class HeartbeatManager:
    """Local lifecycle helper; it never sends network heartbeats."""

    def __init__(self, interval=300, jitter=0, kill_switch=0, c2_connection=None):
        self.interval = max(1, int(interval))
        self.jitter = max(0, int(jitter))
        self.kill_switch = max(0, int(kill_switch))
        self.c2_connection = c2_connection
        self.running = False
        self.last_heartbeat = datetime.now(timezone.utc)
        self._stop_event = threading.Event()

    def send_heartbeat(self) -> bool:
        self.last_heartbeat = datetime.now(timezone.utc)
        SESSION["last_heartbeat"] = self.last_heartbeat
        return True

    def run(self) -> None:
        self.running = True
        self._stop_event.clear()
        while not self._stop_event.wait(self.interval):
            self.send_heartbeat()

    def check_kill_switch(self) -> bool:
        return False

    def stop(self) -> None:
        self.running = False
        self._stop_event.set()


def polymorphic_code(original_code: str) -> str:
    """Return source unchanged; runtime code mutation is not supported."""

    if not isinstance(original_code, str):
        raise TypeError("original_code must be a string")
    return original_code


def code_obfuscation(code: str) -> str:
    """Return source unchanged; obfuscated execution is intentionally disabled."""

    if not isinstance(code, str):
        raise TypeError("code must be a string")
    return code


class ShadowVoidCore:
    def __init__(self):
        self.framework_name = CONFIG["framework"]["name"]
        self.framework_version = CONFIG["framework"]["version"]
        self.tor_router = None
        self.i2p_router = None
        self.dga: DomainGenerator | None = None
        self.dead_drops = None
        self.heartbeat: HeartbeatManager | None = None
        self.cipher: AES256GCM | None = None
        self.c2_connection: C2Connection | None = None
        self.initialize()

    def initialize(self) -> None:
        self.initialize_stealth()
        self.initialize_crypto()
        self.initialize_memory_resident()
        load_modules()
        if CONFIG["c2"]["enabled"]:
            self.initialize_c2()
        self.start_session()

    def initialize_stealth(self) -> dict[str, bool]:
        return {
            "safe_mode": True,
            "process_modified": False,
            "files_modified": False,
        }

    def initialize_crypto(self) -> bool:
        try:
            self.crypto_key = generate_key()
            self.cipher = AES256GCM(self.crypto_key)
        except (RuntimeError, ValueError):
            self.cipher = None
        return self.cipher is not None

    def initialize_memory_resident(self) -> bool:
        return make_memory_resident()

    def initialize_c2(self) -> bool:
        self.c2_connection = C2Connection(self)
        self.dead_drops = DeadDropResolver()
        self.heartbeat = None
        return False

    def start_session(self) -> None:
        SESSION.update(
            active=True,
            start_time=datetime.now(timezone.utc),
            targets=[],
            compromised=[],
            last_heartbeat=datetime.now(timezone.utc),
            kill_switch_triggered=False,
        )

    def end_session(self) -> None:
        SESSION["active"] = False
        if self.heartbeat:
            self.heartbeat.stop()
        if self.c2_connection:
            self.c2_connection.stop()

    def execute_command(self, command: str) -> dict[str, Any]:
        if not isinstance(command, str) or not command.strip():
            return {"status": "error", "message": "No command provided"}
        if not SESSION["active"]:
            self.start_session()
        try:
            parts = shlex.split(command)
        except ValueError as exc:
            return {"status": "error", "message": f"Invalid command syntax: {exc}"}
        cmd, args = parts[0].lower(), parts[1:]
        handlers = {
            "init": self.cmd_init,
            "scan": self.cmd_scan,
            "exploit": self.cmd_exploit,
            "pivot": self.cmd_pivot,
            "exfil": self.cmd_exfil,
            "inject": self.cmd_inject,
            "clean": self.cmd_clean,
            "modules": self.cmd_modules,
            "c2": self.cmd_c2,
            "help": self.cmd_help,
            "exit": self.cmd_exit,
        }
        handler = handlers.get(cmd)
        if handler is None:
            return {"status": "error", "message": f"Unknown command: {cmd}"}
        return handler(args)

    @staticmethod
    def _blocked(action: str) -> dict[str, str]:
        return {
            "status": "blocked",
            "action": action,
            "message": f"{action} is disabled in safe mode",
        }

    def cmd_init(self, args: list[str]) -> dict[str, Any]:
        return self.initialize_stealth()

    def cmd_scan(self, args: list[str]) -> dict[str, str]:
        return self._blocked("active scanning")

    def cmd_exploit(self, args: list[str]) -> dict[str, str]:
        return self._blocked("exploit execution")

    def cmd_pivot(self, args: list[str]) -> dict[str, str]:
        return self._blocked("lateral movement")

    def cmd_exfil(self, args: list[str]) -> dict[str, str]:
        return self._blocked("data exfiltration")

    def cmd_inject(self, args: list[str]) -> dict[str, str]:
        return self._blocked("process injection")

    def cmd_clean(self, args: list[str]) -> dict[str, str]:
        return {"status": "success", "message": "No destructive cleanup is configured"}

    def cmd_modules(self, args: list[str]) -> dict[str, Any]:
        if args and args[0].lower() != "list":
            return {"status": "error", "message": "Invalid modules command"}
        return {
            "status": "success",
            "modules": [
                {
                    "name": name,
                    "status": "loaded" if name in MODULES else "unavailable",
                    "error": MODULE_LOAD_ERRORS.get(name),
                }
                for name in CONFIG["modules"]
            ],
        }

    def cmd_c2(self, args: list[str]) -> dict[str, Any]:
        if not args:
            return {"status": "error", "message": "C2 command required"}
        subcmd = args[0].lower()
        if subcmd == "status":
            return {
                "status": "success",
                "c2_status": {
                    "enabled": False,
                    "safe_mode": True,
                    "persistent_connection": False,
                },
            }
        if subcmd == "generate":
            try:
                count = int(args[1]) if len(args) > 1 else 10
                if count < 0 or count > 100:
                    raise ValueError
            except (TypeError, ValueError):
                return {"status": "error", "message": "count must be an integer from 0 to 100"}
            generator = DomainGenerator(count, ("example",))
            return {"status": "success", "domains": generator.generate_domains(count)}
        return {"status": "error", "message": "Invalid C2 command"}

    def cmd_help(self, args: list[str]) -> dict[str, str]:
        return {
            "status": "success",
            "help": (
                "ShadowVoid safe assessment runner\n\n"
                "COMMANDS:\n"
                "  modules list           List loaded local modules\n"
                "  c2 status             Show that network C2 is disabled\n"
                "  c2 generate [count]   Generate offline example names\n"
                "  scan ...              Blocked in safe mode\n"
                "  exploit ...           Blocked in safe mode\n"
                "  pivot ...             Blocked in safe mode\n"
                "  exfil ...             Blocked in safe mode\n"
                "  inject ...            Blocked in safe mode\n"
                "  clean                 No-op cleanup\n"
                "  exit                  End the local session"
            ),
        }

    def cmd_exit(self, args: list[str]) -> dict[str, str]:
        self.end_session()
        return {"status": "success", "message": "Session ended"}


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    core = ShadowVoidCore()
    if argv:
        command = shlex.join(argv)
        result = core.execute_command(command)
        print(json.dumps(result, indent=2, default=str))
        return 0 if result.get("status") != "error" else 2

    print("ShadowVoid safe assessment runner")
    print("Type 'help' for commands, or 'exit' to quit")
    try:
        while SESSION["active"]:
            command = input("sv> ").strip()
            if not command:
                continue
            if command.startswith("!"):
                command = command[1:]
            result = core.execute_command(command)
            print(json.dumps(result, indent=2, default=str))
            if command.split(maxsplit=1)[0].lower() == "exit":
                break
    except (EOFError, KeyboardInterrupt):
        core.end_session()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
