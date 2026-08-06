"""Tests for 15E AGI Safety & Alignment Layer"""
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


def test_manifest() -> None:
    data = json.loads((Path(__file__).parent.parent / "registry" / "manifest.json").read_text())
    assert data["layer"] == "15E"


def test_safe_action_passes() -> None:
    from safety_alignment import SafetyAlignmentLayer, SafetyConstraint, AlignmentDimension, SafetyLevel
    layer = SafetyAlignmentLayer()
    layer.register_constraint(SafetyConstraint(
        "no_delete", "Block destructive actions",
        AlignmentDimension.HARMLESSNESS,
        check=lambda a: a.get("action_type") != "delete",
        blocking=True,
    ))
    result = layer.assess("a1", {"action_type": "read", "target": "logs"})
    assert result.safety_level == SafetyLevel.SAFE


def test_blocked_action() -> None:
    from safety_alignment import SafetyAlignmentLayer, SafetyConstraint, AlignmentDimension, SafetyLevel
    layer = SafetyAlignmentLayer()
    layer.register_constraint(SafetyConstraint(
        "no_delete", "Block destructive actions",
        AlignmentDimension.HARMLESSNESS,
        check=lambda a: a.get("action_type") != "delete",
        blocking=True,
    ))
    result = layer.assess("a2", {"action_type": "delete", "target": "production_db"})
    assert result.safety_level == SafetyLevel.BLOCKED
    assert "no_delete" in result.violations


def test_safety_report() -> None:
    from safety_alignment import SafetyAlignmentLayer, SafetyConstraint, AlignmentDimension
    layer = SafetyAlignmentLayer()
    layer.register_constraint(SafetyConstraint(
        "safe_check", "test", AlignmentDimension.HONESTY,
        check=lambda a: a.get("honest", True),
        blocking=False,
    ))
    layer.assess("a1", {"honest": True})
    layer.assess("a2", {"honest": False})
    report = layer.safety_report()
    assert report["total_assessments"] == 2


def test_multiple_dimensions() -> None:
    from safety_alignment import SafetyAlignmentLayer, SafetyConstraint, AlignmentDimension, SafetyLevel
    layer = SafetyAlignmentLayer()
    layer.register_constraint(SafetyConstraint(
        "helpful", "Must have purpose",
        AlignmentDimension.HELPFULNESS,
        check=lambda a: "purpose" in a,
        blocking=False,
    ))
    layer.register_constraint(SafetyConstraint(
        "harmless", "No harm",
        AlignmentDimension.HARMLESSNESS,
        check=lambda a: not a.get("harmful", False),
        blocking=True,
    ))
    result = layer.assess("a3", {"purpose": "reporting", "harmful": False})
    assert result.safety_level == SafetyLevel.SAFE
