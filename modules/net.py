"""Safe network-assessment module.

Traffic interception, ARP poisoning, DNS spoofing, and penetration actions are
intentionally unavailable.
"""

from __future__ import annotations

from typing import Any

from ._safe import blocked


class NetModule:
    def __init__(self, core=None):
        self.core = core

    def arp_poison(self, interface: str, target_ip: str, gateway_ip: str) -> dict[str, Any]:
        return blocked("ARP poisoning", interface=interface, target=target_ip, gateway=gateway_ip)

    def dns_spoof(self, interface: str, target_domain: str, redirect_ip: str) -> dict[str, Any]:
        return blocked("DNS spoofing", interface=interface, domain=target_domain, redirect=redirect_ip)

    def vpn_penetrate(self, vpn_ip: str, target_ip: str, port: int = 22) -> dict[str, Any]:
        return blocked("VPN penetration", vpn=vpn_ip, target=target_ip, port=port)
