"""Safe reconnaissance module.

The former implementation launched arp-scan, NetBIOS probes, DNS lookups, and
Tor/I2P discovery against arbitrary targets.  This module now reports that
active reconnaissance is unavailable and performs no network I/O.
"""

from __future__ import annotations

from typing import Any

from ._safe import blocked


class ReconModule:
    def __init__(self, core=None):
        self.core = core
        self.tor_router = None

    def scan(self, target: str, scan_type: str = "full") -> dict[str, Any]:
        return blocked("active reconnaissance", target=target, scan_type=scan_type, scans={})

    def scan_onion(self, target: str) -> dict[str, Any]:
        return blocked("private-service reconnaissance", target=target, services=[])

    def scan_i2p(self, target: str) -> dict[str, Any]:
        return blocked("private-service reconnaissance", target=target, services=[])

    def scan_arp(self, target: str) -> dict[str, Any]:
        return blocked("ARP scanning", target=target, hosts=[])

    def scan_netbios(self, target: str) -> dict[str, Any]:
        return blocked("NetBIOS scanning", target=target, hosts=[])

    def scan_cloud(self, target: str) -> dict[str, Any]:
        return blocked("cloud asset discovery", target=target, assets=[])
