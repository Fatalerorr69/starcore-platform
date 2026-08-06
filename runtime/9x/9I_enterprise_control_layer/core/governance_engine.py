"""9I — Enterprise Control Layer: Governance Engine"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import time


class PolicyAction(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"
    AUDIT = "audit"


@dataclass
class Policy:
    name: str
    description: str
    action: PolicyAction
    conditions: dict[str, Any] = field(default_factory=dict)
    priority: int = 5
    enabled: bool = True


@dataclass
class ComplianceEvent:
    event_type: str
    subject: str
    resource: str
    policy_name: str
    decision: PolicyAction
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)


class GovernanceEngine:
    def __init__(self) -> None:
        self._policies: list[Policy] = []
        self._audit_log: list[ComplianceEvent] = []

    def register_policy(self, policy: Policy) -> None:
        self._policies.append(policy)
        self._policies.sort(key=lambda p: p.priority)

    def evaluate(self, subject: str, resource: str, context: dict[str, Any]) -> PolicyAction:
        for policy in self._policies:
            if not policy.enabled:
                continue
            if self._matches(policy, context):
                event = ComplianceEvent(
                    event_type="policy_evaluation",
                    subject=subject,
                    resource=resource,
                    policy_name=policy.name,
                    decision=policy.action,
                    metadata=context,
                )
                self._audit_log.append(event)
                return policy.action
        return PolicyAction.ALLOW

    def _matches(self, policy: Policy, context: dict[str, Any]) -> bool:
        for key, expected in policy.conditions.items():
            if context.get(key) != expected:
                return False
        return True

    def compliance_report(self) -> dict[str, Any]:
        decisions: dict[str, int] = {}
        for event in self._audit_log:
            decisions[event.decision.value] = decisions.get(event.decision.value, 0) + 1
        return {
            "total_evaluations": len(self._audit_log),
            "decisions": decisions,
            "policies_active": sum(1 for p in self._policies if p.enabled),
        }
