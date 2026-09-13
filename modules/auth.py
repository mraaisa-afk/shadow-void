"""Safe authentication-assessment module.

Credential cracking, pass-the-hash, ticket forgery, and key harvesting are not
implemented.  Methods remain as explicit blocked responses for API compatibility
with older clients.
"""

from __future__ import annotations

from typing import Any

from ._safe import blocked


class AuthModule:
    def __init__(self, core=None):
        self.core = core
        self.hashcat_path = None

    def brute_force(self, hash_value: str, hash_type: str, wordlist: str | None = None) -> dict[str, Any]:
        return blocked("credential cracking", hash_type=hash_type)

    def pass_the_hash(self, hash_value: str, target: str, username: str = "administrator") -> dict[str, Any]:
        return blocked("pass-the-hash", target=target, username=username)

    def golden_ticket(
        self,
        domain: str,
        sid: str,
        user: str,
        ntlm_hash: str,
        aes_key: str | None = None,
    ) -> dict[str, Any]:
        return blocked("Kerberos ticket forgery", domain=domain, user=user)

    def harvest_ssh_keys(self, target: str, username: str, key_path: str | None = None) -> dict[str, Any]:
        return blocked("remote key harvesting", target=target, username=username)
