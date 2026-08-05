#!/usr/bin/env python3
"""
STARCORE Interactive Decision Engine CLI.

Použití:
  uv run python .starcore/scripts/decision_engine.py render --file report.yaml
  uv run python .starcore/scripts/decision_engine.py render -        (stdin)
  uv run python .starcore/scripts/decision_engine.py parse-choice "Varianta 1"
  uv run python .starcore/scripts/decision_engine.py check-safety "git push --force"
  uv run python .starcore/scripts/decision_engine.py format
  uv run python .starcore/scripts/decision_engine.py log --decision "Zvolena varianta 1"
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

_SCRIPT_DIR = Path(__file__).parent
_STARCORE_DIR = _SCRIPT_DIR.parent

# ── Safety keywords ───────────────────────────────────────────────────────────

_SAFETY_PATTERNS: list[str] = [
    r"\bmerge\b",
    r"\bpush\b",
    r"\bdelete\b",
    r"\bdrop\b",
    r"\bremove\b",
    r"\breset\b",
    r"--force",
    r"-f\b",
    r"force.?push",
    r"\binfrastructure\b",
    r"\bproduction\b",
    r"\bprod\b",
    r"\bsecret\b",
    r"\bcredential\b",
    r"\bpassword\b",
    r"\btoken\b",
    r"api.?key",
    r"rm\s+-rf",
    r"truncate\b",
    r"drop\s+table",
    r"git\s+clean",
    r"git\s+reset\s+--hard",
    r"git\s+push.*--force",
]

# ── Choice parsing ────────────────────────────────────────────────────────────

# (pattern, extractor) — returns int choice or None
_NUMERIC_PATTERNS: list[tuple[str, Any]] = [
    (r"^\s*(\d+)\s*$", lambda m: int(m.group(1))),
    (r"varianta\s+(\d+)", lambda m: int(m.group(1))),
    (r"vyber\s+(\d+)", lambda m: int(m.group(1))),
    (r"volba\s+(\d+)", lambda m: int(m.group(1))),
    (r"mo[žz]nost\s+(\d+)", lambda m: int(m.group(1))),
    (r"\[(\d+)\]", lambda m: int(m.group(1))),
    (r"^(\d+)\s*[.:]", lambda m: int(m.group(1))),
]

# Keyword → canonical choice number (1 = recommended variant)
_KEYWORD_MAP: dict[str, int] = {
    "pokračuj": 1,
    "pokračovat": 1,
    "doporučená varianta": 1,
    "proveď doporučenou variantu": 1,
    "proveď doporučenou": 1,
    "doporučenou": 1,
    "audit": 4,
    "pokračovat v auditu": 4,
    "detail": 5,
    "zobrazit detail": 5,
    "vlastní": 6,
    "vlastní instrukce": 6,
}

# Natural-language action verbs that are NOT a choice number — returned as-is
_ACTION_PREFIXES = ("oprav", "zobraz", "implementuj", "spusť", "zkontroluj", "vyřeš")


def parse_choice(text: str) -> int | str | None:
    """
    Parse user choice text to a canonical form.

    Returns:
        int   — numeric choice (1-N)
        str   — semantic action (e.g. "oprav r-001")
        None  — unrecognised input
    """
    stripped = text.strip()
    if not stripped:
        return None

    lower = stripped.lower()

    # Multi-word keyword map (longest match first)
    for keyword in sorted(_KEYWORD_MAP, key=len, reverse=True):
        if keyword in lower:
            return _KEYWORD_MAP[keyword]

    # Numeric pattern matching
    for pattern, extractor in _NUMERIC_PATTERNS:
        m = re.search(pattern, lower, re.IGNORECASE)
        if m:
            return extractor(m)

    # Semantic action verbs → return normalised string for caller
    for prefix in _ACTION_PREFIXES:
        if lower.startswith(prefix):
            return lower

    return None


def cmd_parse_choice(args: argparse.Namespace) -> int:
    result = parse_choice(args.text)
    if result is None:
        print(f"CHYBA: Nerozpoznaná volba: '{args.text}'", file=sys.stderr)
        return 1
    print(f"choice={result}")
    return 0


# ── Safety check ──────────────────────────────────────────────────────────────


def requires_confirmation(operation: str) -> tuple[bool, list[str]]:
    """
    Check whether an operation requires explicit user confirmation.

    Returns (requires: bool, matched_patterns: list[str]).
    """
    lower = operation.lower()
    matched = [p for p in _SAFETY_PATTERNS if re.search(p, lower)]
    return bool(matched), matched


def cmd_check_safety(args: argparse.Namespace) -> int:
    needs_confirm, matched = requires_confirmation(args.operation)
    if needs_confirm:
        print("REQUIRES_CONFIRMATION")
        reasons = ", ".join(matched[:3])
        print(f"Operace vyžaduje explicitní potvrzení (detekováno: {reasons}).")
        return 2  # Exit 2 = requires confirmation (distinct from error=1)
    print("SAFE")
    return 0


# ── Report rendering ──────────────────────────────────────────────────────────

_SEPARATOR = "─" * 72

_REPORT_TEMPLATE = """\
{separator}
## STAV
{stav}

## CO BYLO ZJIŠTĚNO
{zjisteno}

## CO BYLO OVĚŘENO
{overeno}

## RIZIKA
{rizika}

## DOPORUČENÍ

### Doporučená varianta
[1] {doporuceni}

### Alternativy
{alternativy_block}
## DOPAD
{dopad}

## RIZIKO
{riziko_uroven}

## ROLLBACK
{rollback}

## DALŠÍ KROK
{dalsi_krok}
{separator}
Čekám na tvoji volbu.
"""


def _build_alternativy(items: list[str], base_index: int = 2) -> str:
    lines = []
    for i, text in enumerate(items, start=base_index):
        lines.append(f"[{i}] {text}")
    return "\n".join(lines) + "\n" if lines else ""


def render_report(data: dict[str, Any]) -> str:
    """Render a Czech decision report from structured data."""
    alternativy: list[str] = data.get("alternativy", [])
    add_standard = data.get("standard_choices", True)

    extra: list[str] = []
    if add_standard:
        extra = [
            "Pokračovat v auditu",
            "Zobrazit detail",
            "Vlastní instrukce",
        ]

    all_alts = alternativy + extra
    alternativy_block = _build_alternativy(all_alts, base_index=2)

    zjisteno = data.get("zjisteno", "—")
    if isinstance(zjisteno, list):
        zjisteno = "\n".join(f"- {item}" for item in zjisteno)

    overeno = data.get("overeno", "—")
    if isinstance(overeno, list):
        overeno = "\n".join(f"- {item}" for item in overeno)

    rizika = data.get("rizika", "—")
    if isinstance(rizika, list):
        rizika = "\n".join(f"- {item}" for item in rizika)

    return _REPORT_TEMPLATE.format(
        separator=_SEPARATOR,
        stav=data.get("stav", "—"),
        zjisteno=zjisteno,
        overeno=overeno,
        rizika=rizika,
        doporuceni=data.get("doporuceni", "—"),
        alternativy_block=alternativy_block,
        dopad=data.get("dopad", "—"),
        riziko_uroven=data.get("riziko_uroven", "—"),
        rollback=data.get("rollback", "—"),
        dalsi_krok=data.get("dalsi_krok", "Čekám na volbu [1]–[N]."),
    )


def _load_data(source: str) -> dict[str, Any]:
    """Load YAML or JSON from a file path or '-' (stdin)."""
    import yaml  # stdlib-free fallback only in tests; yaml is always available

    if source == "-":
        raw = sys.stdin.read()
    else:
        path = Path(source)
        if not path.exists():
            raise FileNotFoundError(f"Soubor '{source}' nenalezen.")
        raw = path.read_text()

    # Try YAML first (superset of JSON)
    try:
        data = yaml.safe_load(raw)
    except Exception:
        data = json.loads(raw)

    if not isinstance(data, dict):
        raise ValueError("Vstup musí být YAML/JSON objekt (dict).")
    return data


def cmd_render(args: argparse.Namespace) -> int:
    try:
        data = _load_data(args.file)
    except (FileNotFoundError, ValueError, Exception) as exc:
        print(f"CHYBA: {exc}", file=sys.stderr)
        return 1
    print(render_report(data))
    return 0


def cmd_format(_args: argparse.Namespace) -> int:
    """Print an empty template with placeholder values."""
    template = {
        "stav": "OK | CHYBA | VAROVÁNÍ",
        "zjisteno": ["Zjištění 1", "Zjištění 2"],
        "overeno": ["Ověřeno 1", "Ověřeno 2"],
        "rizika": ["R-XXX: popis [HIGH/MED/LOW]"],
        "doporuceni": "Popis doporučené akce",
        "alternativy": ["Alternativa A", "Alternativa B"],
        "dopad": "Popis dopadu",
        "riziko_uroven": "LOW | MEDIUM | HIGH",
        "rollback": "git revert HEAD",
        "dalsi_krok": "Čekám na volbu [1]–[N].",
        "standard_choices": True,
    }
    print(render_report(template))
    return 0


# ── Decision logging ──────────────────────────────────────────────────────────


def cmd_log(args: argparse.Namespace) -> int:
    """Log a decision to the active session ledger via ledger.py."""
    ledger_script = _SCRIPT_DIR / "ledger.py"
    if not ledger_script.exists():
        print("CHYBA: ledger.py nenalezen.", file=sys.stderr)
        return 1

    cmd = [
        sys.executable,
        str(ledger_script),
        "add-decision",
        "--text",
        args.decision,
    ]
    if args.session_id:
        cmd += ["--session-id", args.session_id]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        return result.returncode
    print(result.stdout, end="")
    return 0


# ── Main ──────────────────────────────────────────────────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="decision_engine",
        description="STARCORE Interactive Decision Engine CLI",
    )
    sub = parser.add_subparsers(dest="command")

    # render
    p_render = sub.add_parser("render", help="Vykreslit decision report ze YAML/JSON")
    p_render.add_argument(
        "--file",
        default="-",
        help="Cesta k YAML/JSON souboru nebo '-' pro stdin (výchozí: stdin)",
    )

    # parse-choice
    p_pc = sub.add_parser("parse-choice", help="Parsovat volbu uživatele na kanonický tvar")
    p_pc.add_argument("text", help="Text volby (číslo, klíčové slovo, věta)")

    # check-safety
    p_cs = sub.add_parser("check-safety", help="Ověřit, zda operace vyžaduje potvrzení")
    p_cs.add_argument("operation", help="Popis nebo příkaz operace")

    # format
    sub.add_parser("format", help="Zobrazit prázdnou šablonu reportu")

    # log
    p_log = sub.add_parser("log", help="Zalogovat rozhodnutí do session ledgeru")
    p_log.add_argument("--decision", required=True, help="Text rozhodnutí")
    p_log.add_argument("--session-id", default=None, help="ID sezení (výchozí: aktivní)")

    args = parser.parse_args()

    dispatch = {
        "render": cmd_render,
        "parse-choice": cmd_parse_choice,
        "check-safety": cmd_check_safety,
        "format": cmd_format,
        "log": cmd_log,
    }

    if args.command not in dispatch:
        parser.print_help()
        return 1

    return dispatch[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
