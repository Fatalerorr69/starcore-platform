"""Tests for 9I Enterprise Control Layer"""
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest() -> None:
    data = json.loads((Path(__file__).parent.parent / "registry" / "manifest.json").read_text())
    assert data["layer"] == "9I"


def test_policy_allow() -> None:
    from governance_engine import GovernanceEngine, Policy, PolicyAction
    gov = GovernanceEngine()
    gov.register_policy(Policy("allow-all", "Allow all", PolicyAction.ALLOW, {}))
    decision = gov.evaluate("user-1", "resource-X", {})
    assert decision == PolicyAction.ALLOW


def test_policy_deny() -> None:
    from governance_engine import GovernanceEngine, Policy, PolicyAction
    gov = GovernanceEngine()
    gov.register_policy(Policy("deny-external", "Deny external", PolicyAction.DENY,
                               {"origin": "external"}, priority=1))
    decision = gov.evaluate("ext-user", "db", {"origin": "external"})
    assert decision == PolicyAction.DENY


def test_compliance_report() -> None:
    from governance_engine import GovernanceEngine, Policy, PolicyAction
    gov = GovernanceEngine()
    gov.register_policy(Policy("audit-all", "Audit everything", PolicyAction.AUDIT, {}))
    gov.evaluate("u1", "r1", {})
    gov.evaluate("u2", "r2", {})
    report = gov.compliance_report()
    assert report["total_evaluations"] == 2
