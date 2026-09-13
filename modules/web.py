"""Safe web-assessment module.

No uploads, webshells, SSRF payloads, XXE payloads, or active probing are
performed.  The method signatures are retained for callers migrating from the
old API.
"""

from __future__ import annotations

from typing import Any

from ._safe import blocked


class WebModule:
    def __init__(self, core=None):
        self.core = core

    def deploy_webshell(self, target: str, url_path: str, shell_type: str = "php") -> dict[str, Any]:
        return blocked("webshell deployment", target=target, url=url_path, type=shell_type)

    def ssrf_test(self, target: str, url: str) -> dict[str, Any]:
        return blocked("SSRF testing", target=target, url=url)

    def xxe_test(self, target: str, endpoint: str) -> dict[str, Any]:
        return blocked("XXE testing", target=target, endpoint=endpoint)

    def cms_scan(self, target: str) -> dict[str, Any]:
        return blocked("active CMS scanning", target=target, cms=[], vulnerabilities=[])
