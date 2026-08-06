"""15E — AGI Safety & Alignment Layer: Value Aligner + Constraint Enforcer"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import time


class SafetyLevel(str, Enum):
    SAFE = "safe"
    CAUTION = "caution"
    UNSAFE = "unsafe"
    BLOCKED = "blocked"


class AlignmentDimension(str, Enum):
    HELPFULNESS = "helpfulness"
    HARMLESSNESS = "harmlessness"
    HONESTY = "honesty"
    AUTONOMY_PRESERVATION = "autonomy_preservation"
    NON_DECEPTION = "non_deception"


@dataclass
class SafetyConstraint:
    name: str
    description: str
    dimension: AlignmentDimension
    check: Any  # callable: (action: dict) -> bool
    priority: int = 5
    blocking: bool = True


@dataclass
class AlignmentAssessment:
    action_id: str
    action: dict[str, Any]
    safety_level: SafetyLevel
    violations: list[str] = field(default_factory=list)
    passed_checks: list[str] = field(default_factory=list)
    recommendation: str = ""
    timestamp: float = field(default_factory=time.time)


@dataclass
class OversightEvent:
    event_type: str
    action: dict[str, Any]
    assessment: AlignmentAssessment
    requires_human_review: bool = False
    timestamp: float = field(default_factory=time.time)


class SafetyAlignmentLayer:
    """Multi-dimensional safety and value alignment enforcement."""

    def __init__(self) -> None:
        self._constraints: list[SafetyConstraint] = []
        self._audit_log: list[AlignmentAssessment] = []
        self._oversight_log: list[OversightEvent] = []
        self._blocked_actions: int = 0

    def register_constraint(self, constraint: SafetyConstraint) -> None:
        self._constraints.append(constraint)
        self._constraints.sort(key=lambda c: c.priority)

    def assess(self, action_id: str, action: dict[str, Any]) -> AlignmentAssessment:
        violations: list[str] = []
        passed: list[str] = []
        blocking_violation = False

        for constraint in self._constraints:
            try:
                passed_check = constraint.check(action)
            except Exception:
                passed_check = False

            if passed_check:
                passed.append(constraint.name)
            else:
                violations.append(constraint.name)
                if constraint.blocking:
                    blocking_violation = True

        if blocking_violation:
            level = SafetyLevel.BLOCKED
            self._blocked_actions += 1
            recommendation = "Action blocked due to safety constraint violation."
        elif violations:
            level = SafetyLevel.CAUTION
            recommendation = f"Proceed with caution. Soft violations: {', '.join(violations)}"
        else:
            level = SafetyLevel.SAFE
            recommendation = "Action appears aligned."

        assessment = AlignmentAssessment(
            action_id=action_id,
            action=action,
            safety_level=level,
            violations=violations,
            passed_checks=passed,
            recommendation=recommendation,
        )
        self._audit_log.append(assessment)

        requires_review = level in (SafetyLevel.BLOCKED, SafetyLevel.CAUTION)
        self._oversight_log.append(OversightEvent(
            event_type="assessment",
            action=action,
            assessment=assessment,
            requires_human_review=requires_review,
        ))
        return assessment

    def safety_report(self) -> dict[str, Any]:
        total = len(self._audit_log)
        levels: dict[str, int] = {}
        for a in self._audit_log:
            levels[a.safety_level.value] = levels.get(a.safety_level.value, 0) + 1
        return {
            "total_assessments": total,
            "blocked": self._blocked_actions,
            "safety_distribution": levels,
            "constraints_active": len(self._constraints),
            "pending_human_review": sum(
                1 for e in self._oversight_log if e.requires_human_review
            ),
        }
