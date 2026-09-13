"""Safe wireless-assessment module.

Rogue access points, forced association, and active wireless exploitation are
not implemented.
"""

from __future__ import annotations

from typing import Any

from ._safe import blocked


class WirelessModule:
    def __init__(self, core=None):
        self.core = core

    def evil_twin(self, interface: str, ssid: str, channel: int | None = None) -> dict[str, Any]:
        return blocked("evil-twin access point", interface=interface, ssid=ssid, channel=channel)

    def karma_attack(self, interface: str) -> dict[str, Any]:
        return blocked("Karma wireless attack", interface=interface)

    def ble_scan(self, interface: str, duration: int = 10) -> dict[str, Any]:
        return blocked("active BLE scanning", interface=interface, duration=duration, devices=[])
