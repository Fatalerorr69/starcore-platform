"""8C — Security Fabric: Access Control"""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import secrets


@dataclass
class Principal:
    identity: str
    roles: list[str] = field(default_factory=list)
    token: str = field(default_factory=lambda: secrets.token_hex(32))


class AccessControl:
    def __init__(self) -> None:
        self._principals: dict[str, Principal] = {}
        self._policies: dict[str, list[str]] = {}

    def register(self, principal: Principal) -> None:
        self._principals[principal.identity] = principal

    def grant(self, role: str, resources: list[str]) -> None:
        self._policies[role] = resources

    def authorize(self, identity: str, resource: str) -> bool:
        p = self._principals.get(identity)
        if not p:
            return False
        for role in p.roles:
            if resource in self._policies.get(role, []):
                return True
        return False

    def audit_log(self, identity: str, resource: str, granted: bool) -> dict[str, str]:
        return {
            "identity": identity,
            "resource": resource,
            "decision": "ALLOW" if granted else "DENY",
            "hash": hashlib.sha256(f"{identity}:{resource}".encode()).hexdigest()[:16],
        }
