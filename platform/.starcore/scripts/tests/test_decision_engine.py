#!/usr/bin/env python3
"""
Standalone unit tests for decision_engine.py.

Nejsou součástí hlavního pytest suite (coverage scope = packages/, apps/).
Spusť: uv run python .starcore/scripts/tests/test_decision_engine.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make parent importable
sys.path.insert(0, str(Path(__file__).parent.parent))

from decision_engine import (  # noqa: E402
    parse_choice,
    render_report,
    requires_confirmation,
)

_PASS = 0
_FAIL = 0


def check(label: str, actual: object, expected: object) -> None:
    global _PASS, _FAIL
    if actual == expected:
        print(f"  PASS  {label}")
        _PASS += 1
    else:
        print(f"  FAIL  {label}")
        print(f"         expected: {expected!r}")
        print(f"         actual:   {actual!r}")
        _FAIL += 1


# ── parse_choice ──────────────────────────────────────────────────────────────

print("\nparse_choice:")
check("bare digit '1'", parse_choice("1"), 1)
check("bare digit '42'", parse_choice("42"), 42)
check("'Varianta 1'", parse_choice("Varianta 1"), 1)
check("'varianta 3'", parse_choice("varianta 3"), 3)
check("'Vyber 2'", parse_choice("Vyber 2"), 2)
check("'Volba 5'", parse_choice("Volba 5"), 5)
check("'[3]'", parse_choice("[3]"), 3)
check("'3.'", parse_choice("3."), 3)
check("'pokračuj'", parse_choice("pokračuj"), 1)
check("'Pokračovat'", parse_choice("Pokračovat"), 1)
check("'Proveď doporučenou variantu'", parse_choice("Proveď doporučenou variantu"), 1)
check("'doporučenou'", parse_choice("doporučenou"), 1)
check("'audit'", parse_choice("audit"), 4)
check("'Pokračovat v auditu'", parse_choice("Pokračovat v auditu"), 4)
check("'detail'", parse_choice("detail"), 5)
check("'Zobrazit detail'", parse_choice("Zobrazit detail"), 5)
check("'vlastní instrukce'", parse_choice("vlastní instrukce"), 6)
check("semantic 'Oprav R-001'", parse_choice("Oprav R-001"), "oprav r-001")
check("semantic 'zobraz R-010'", parse_choice("zobraz R-010"), "zobraz r-010")
check(
    "semantic 'Implementuj variantu'",
    parse_choice("Implementuj variantu"),
    "implementuj variantu",
)
check("empty string → None", parse_choice(""), None)
check("whitespace → None", parse_choice("   "), None)

# ── requires_confirmation ─────────────────────────────────────────────────────

print("\nrequires_confirmation:")
safe_ops = [
    "uv run pytest -q",
    "uv run ruff check .",
    "git status",
    "git log --oneline -5",
    "cat .starcore/README.md",
]
unsafe_ops = [
    "git push --force",
    "git push origin main --force",
    "git reset --hard HEAD~1",
    "git clean -fd",
    "rm -rf /tmp/test",
    "drop table users",
    "deploy to production",
    "delete branch feature/old",
    "merge pull request",
    "set STARCORE_API_KEY=...",
]

for op in safe_ops:
    needs, _ = requires_confirmation(op)
    check(f"SAFE: '{op[:40]}'", needs, False)

for op in unsafe_ops:
    needs, matched = requires_confirmation(op)
    check(f"UNSAFE: '{op[:40]}'", needs, True)

# ── render_report ─────────────────────────────────────────────────────────────

print("\nrender_report:")
report = render_report(
    {
        "stav": "OK",
        "zjisteno": ["Zjištění A", "Zjištění B"],
        "overeno": "Ověřeno vše",
        "rizika": "Žádná",
        "doporuceni": "Proveď akci X",
        "alternativy": ["Alternativa Y", "Alternativa Z"],
        "dopad": "Nízký",
        "riziko_uroven": "LOW",
        "rollback": "git revert HEAD",
        "dalsi_krok": "Čekám.",
        "standard_choices": True,
    }
)
check("contains STAV", "## STAV" in report, True)
check("contains zjisteni A", "Zjištění A" in report, True)
check("contains [1] doporuceni", "[1] Proveď akci X" in report, True)
check("contains [2] alt Y", "[2] Alternativa Y" in report, True)
check("contains [3] alt Z", "[3] Alternativa Z" in report, True)
check("contains [4] audit", "[4] Pokračovat v auditu" in report, True)
check("contains [5] detail", "[5] Zobrazit detail" in report, True)
check("contains [6] vlastni", "[6] Vlastní instrukce" in report, True)
check("contains Čekám", "Čekám na tvoji volbu." in report, True)
check("contains ROLLBACK", "## ROLLBACK" in report, True)

# without standard choices
report2 = render_report(
    {
        "stav": "CHYBA",
        "zjisteno": "X",
        "overeno": "Y",
        "rizika": "Z",
        "doporuceni": "Fix it",
        "alternativy": [],
        "dopad": "—",
        "riziko_uroven": "HIGH",
        "rollback": "restore",
        "standard_choices": False,
    }
)
check("no standard choices → no audit entry", "Pokračovat v auditu" not in report2, True)

# list-based zjisteno formatting
report3 = render_report(
    {
        "stav": "OK",
        "zjisteno": ["Item 1", "Item 2"],
        "overeno": [],
        "rizika": [],
        "doporuceni": "X",
        "standard_choices": False,
    }
)
check("list zjisteno formatted", "- Item 1" in report3 and "- Item 2" in report3, True)

# ── Summary ───────────────────────────────────────────────────────────────────

total = _PASS + _FAIL
print(f"\n{'=' * 50}")
print(f"VÝSLEDEK: {_PASS}/{total} testů prošlo", end="")
if _FAIL:
    print(f"  ({_FAIL} SELHALO)")
    sys.exit(1)
else:
    print("  ✓")
    sys.exit(0)
