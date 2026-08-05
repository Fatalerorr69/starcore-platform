#!/usr/bin/env python3
"""
STARCORE Session Ledger CLI.

Použití:
  uv run python .starcore/scripts/ledger.py list
  uv run python .starcore/scripts/ledger.py current
  uv run python .starcore/scripts/ledger.py start --session-id "..." --branch "..." --head "..."
  uv run python .starcore/scripts/ledger.py end --next-action "..."
  uv run python .starcore/scripts/ledger.py add-prompt PROM-001
  uv run python .starcore/scripts/ledger.py add-decision "Použít asyncio.create_task"
  uv run python .starcore/scripts/ledger.py add-risk R-001
  uv run python .starcore/scripts/ledger.py add-approval "Push na dev větev schválen"
  uv run python .starcore/scripts/ledger.py add-blocker "CI selhal"
  uv run python .starcore/scripts/ledger.py add-file --type created "path/to/file.py"
  uv run python .starcore/scripts/ledger.py add-test --passed 569 --failed 0 --coverage 100.0
  uv run python .starcore/scripts/ledger.py add-command "uv run pytest -q"
  uv run python .starcore/scripts/ledger.py add-request "Implementuj .starcore/ memory layer"
  uv run python .starcore/scripts/ledger.py reconstruct SESSION_ID
  uv run python .starcore/scripts/ledger.py load SESSION_ID
  uv run python .starcore/scripts/ledger.py validate
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

_SCRIPT_DIR = Path(__file__).parent
_STARCORE_DIR = _SCRIPT_DIR.parent
_LEDGER_PATH = _STARCORE_DIR / "sessions" / "ledger.yaml"
_ARCHIVE_DIR = _STARCORE_DIR / "sessions" / "archive"

sys.path.insert(0, str(_SCRIPT_DIR))
from models import SessionEntry, now_iso  # noqa: E402


def _load_ledger() -> dict:
    if not _LEDGER_PATH.exists():
        return {"schema_version": "1.0", "sessions": []}
    with open(_LEDGER_PATH) as f:
        data = yaml.safe_load(f) or {}
    if "sessions" not in data:
        data["sessions"] = []
    return data


def _save_ledger(data: dict) -> None:
    _LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(_LEDGER_PATH, "w") as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)


def _get_sessions(data: dict) -> list[SessionEntry]:
    return [SessionEntry.from_dict(s) for s in data.get("sessions", [])]


def _active_session(sessions: list[SessionEntry]) -> SessionEntry | None:
    return next((s for s in sessions if s.is_active()), None)


def _find_session(sessions: list[SessionEntry], session_id: str) -> SessionEntry | None:
    return next((s for s in sessions if s.session_id == session_id), None)


def _update_session(data: dict, updated: SessionEntry) -> None:
    sessions = [
        updated.to_dict() if s["session_id"] == updated.session_id else s for s in data["sessions"]
    ]
    data["sessions"] = sessions


# ── Commands ──────────────────────────────────────────────────────────────────


def cmd_list(args: argparse.Namespace) -> int:  # noqa: ARG001
    data = _load_ledger()
    sessions = _get_sessions(data)
    if not sessions:
        print("Žádné sezení v ledgeru.")
        return 0

    print(f"{'SESSION_ID':<45} {'BRANCH':<45} {'HEAD':<10} {'STATUS'}")
    print("-" * 115)
    for s in sessions:
        status = "ACTIVE" if s.is_active() else "CLOSED"
        branch = s.branch
        if len(branch) > 43:
            branch = branch[:41] + ".."
        print(f"{s.session_id:<45} {branch:<45} {s.head[:8]:<10} {status}")
    return 0


def cmd_current(args: argparse.Namespace) -> int:  # noqa: ARG001
    data = _load_ledger()
    sessions = _get_sessions(data)
    active = _active_session(sessions)
    if not active:
        print("Žádné aktivní sezení.")
        return 1

    d = active.to_dict()
    for key, val in d.items():
        if val is not None and val != [] and val != "":
            if isinstance(val, list):
                print(f"  {key}:")
                for item in val[:10]:
                    print(f"    - {item}")
                if len(val) > 10:
                    print(f"    ... (+{len(val) - 10} dalších)")
            else:
                print(f"  {key:<22}: {val}")
    return 0


def cmd_start(args: argparse.Namespace) -> int:
    data = _load_ledger()
    sessions = _get_sessions(data)
    existing_active = _active_session(sessions)
    if existing_active:
        print(
            f"VAROVÁNÍ: Aktivní sezení '{existing_active.session_id}' stále otevřeno. "
            "Uzavři ho pomocí 'end' před zahájením nového.",
            file=sys.stderr,
        )
        return 1

    session = SessionEntry(
        session_id=args.session_id,
        start_time=now_iso(),
        branch=args.branch,
        head=args.head,
    )
    data["sessions"].append(session.to_dict())
    _save_ledger(data)
    print(f"OK: Sezení '{args.session_id}' zahájeno.")
    return 0


def cmd_end(args: argparse.Namespace) -> int:
    data = _load_ledger()
    sessions = _get_sessions(data)
    active = _active_session(sessions)
    if not active:
        print("CHYBA: Žádné aktivní sezení k uzavření.", file=sys.stderr)
        return 1

    active.end_time = now_iso()
    if args.next_action:
        active.next_action = args.next_action
    if args.head:
        active.head = args.head

    _update_session(data, active)
    _save_ledger(data)

    # Archive to markdown
    _archive_session(active)

    print(f"OK: Sezení '{active.session_id}' uzavřeno.")
    return 0


def _archive_session(session: SessionEntry) -> None:
    _ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    date_prefix = session.start_time[:10]
    slug = session.session_id.replace("/", "-")[:40]
    archive_path = _ARCHIVE_DIR / f"{date_prefix}-{slug}.md"

    lines = [
        f"# Session Archive: {session.session_id}",
        "",
        f"**Start:** {session.start_time}  ",
        f"**End:** {session.end_time or 'N/A'}  ",
        f"**Branch:** `{session.branch}`  ",
        f"**HEAD:** `{session.head}`",
        "",
    ]

    def _section(title: str, items: list) -> list[str]:
        if not items:
            return []
        out = [f"## {title}", ""]
        for item in items:
            if isinstance(item, dict):
                out.append(
                    f"- [{item.get('timestamp', '')[:10]}] "
                    f"{item.get('passed', 0)} passed / "
                    f"{item.get('coverage', 0)}% coverage"
                )
            else:
                out.append(f"- {item}")
        out.append("")
        return out

    lines += _section("User Requests", session.user_requests)
    lines += _section("Prompts Used", session.prompts_used)
    lines += _section("Decisions", session.decisions)
    lines += _section("Risks", session.risks)
    lines += _section("Approvals", session.approvals)
    lines += _section("Blockers", session.blockers)
    lines += _section("Files Created", session.files_created)
    lines += _section("Files Modified", session.files_modified)
    lines += _section("Tests Executed", session.tests_executed)
    lines += _section("Commands Executed", session.commands_executed)

    if session.next_action:
        lines += ["## Next Action", "", session.next_action, ""]

    archive_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  Archivováno: {archive_path.name}")


def _cmd_add_to_list(session_id: str | None, field: str, value: object) -> int:
    data = _load_ledger()
    sessions = _get_sessions(data)

    if session_id:
        session = _find_session(sessions, session_id)
        if not session:
            print(f"CHYBA: Sezení '{session_id}' nenalezeno.", file=sys.stderr)
            return 1
    else:
        session = _active_session(sessions)
        if not session:
            print("CHYBA: Žádné aktivní sezení.", file=sys.stderr)
            return 1

    lst: list = getattr(session, field)
    if value not in lst:
        lst.append(value)
    _update_session(data, session)
    _save_ledger(data)
    print(f"OK: Přidáno do {field} v sezení '{session.session_id}'.")
    return 0


def cmd_add_prompt(args: argparse.Namespace) -> int:
    return _cmd_add_to_list(getattr(args, "session_id", None), "prompts_used", args.prompt_id)


def cmd_add_decision(args: argparse.Namespace) -> int:
    return _cmd_add_to_list(getattr(args, "session_id", None), "decisions", args.text)


def cmd_add_risk(args: argparse.Namespace) -> int:
    return _cmd_add_to_list(getattr(args, "session_id", None), "risks", args.risk_id)


def cmd_add_approval(args: argparse.Namespace) -> int:
    return _cmd_add_to_list(getattr(args, "session_id", None), "approvals", args.text)


def cmd_add_blocker(args: argparse.Namespace) -> int:
    return _cmd_add_to_list(getattr(args, "session_id", None), "blockers", args.text)


def cmd_add_request(args: argparse.Namespace) -> int:
    return _cmd_add_to_list(getattr(args, "session_id", None), "user_requests", args.text)


def cmd_add_command(args: argparse.Namespace) -> int:
    return _cmd_add_to_list(getattr(args, "session_id", None), "commands_executed", args.cmd)


def cmd_add_file(args: argparse.Namespace) -> int:
    field_map = {"created": "files_created", "modified": "files_modified", "read": "files_read"}
    field = field_map.get(args.file_type)
    if not field:
        print(f"CHYBA: Neznámý typ souboru '{args.file_type}'.", file=sys.stderr)
        return 1
    return _cmd_add_to_list(getattr(args, "session_id", None), field, args.path)


def cmd_add_test(args: argparse.Namespace) -> int:
    data = _load_ledger()
    sessions = _get_sessions(data)
    session = _active_session(sessions)
    if not session:
        print("CHYBA: Žádné aktivní sezení.", file=sys.stderr)
        return 1

    run = {
        "timestamp": now_iso(),
        "passed": args.passed,
        "failed": args.failed,
        "coverage": args.coverage,
        "command": args.test_cmd or "uv run pytest -q --cov",
    }
    session.tests_executed.append(run)
    _update_session(data, session)
    _save_ledger(data)
    print(f"OK: Test run přidán ({args.passed} passed, {args.coverage}% coverage).")
    return 0


def cmd_reconstruct(args: argparse.Namespace) -> int:
    data = _load_ledger()
    sessions = _get_sessions(data)
    session = _find_session(sessions, args.session_id)
    if not session:
        print(f"CHYBA: Sezení '{args.session_id}' nenalezeno.", file=sys.stderr)
        return 1

    print(f"\n=== Rekonstrukce sezení: {session.session_id} ===")
    print(f"  Branch:    {session.branch}")
    print(f"  HEAD:      {session.head}")
    print(f"  Start:     {session.start_time}")
    print(f"  End:       {session.end_time or 'AKTIVNÍ'}")
    print(f"  Status:    {'ACTIVE' if session.is_active() else 'CLOSED'}")
    print()

    if session.user_requests:
        print("  Požadavky uživatele:")
        for r in session.user_requests:
            print(f"    → {r[:80]}")

    if session.prompts_used:
        print(f"  Použité prompty: {', '.join(session.prompts_used)}")

    if session.decisions:
        print("  Rozhodnutí:")
        for d in session.decisions:
            print(f"    • {d[:80]}")

    if session.risks:
        print(f"  Rizika: {', '.join(session.risks)}")

    if session.blockers:
        print("  Blokátory:")
        for b in session.blockers:
            print(f"    ⚠ {b[:80]}")

    if session.tests_executed:
        last = session.tests_executed[-1]
        print(
            f"  Poslední test run: {last.get('passed', 0)} passed, "
            f"{last.get('coverage', 0)}% coverage"
        )

    if session.next_action:
        print(f"\n  Příští akce: {session.next_action}")

    return 0


def cmd_load(args: argparse.Namespace) -> int:
    data = _load_ledger()
    sessions = _get_sessions(data)
    session = _find_session(sessions, args.session_id)
    if not session:
        # Try loading from archive
        slug = args.session_id.replace("/", "-")[:40]
        archives = list(_ARCHIVE_DIR.glob(f"*{slug}*.md"))
        if archives:
            print(f"Nalezen archiv: {archives[0]}")
            print(archives[0].read_text())
            return 0
        print(
            f"CHYBA: Sezení '{args.session_id}' nenalezeno v ledgeru ani archivu.",
            file=sys.stderr,
        )
        return 1

    return cmd_reconstruct(args)


def cmd_validate(args: argparse.Namespace) -> int:  # noqa: ARG001
    data = _load_ledger()
    sessions = _get_sessions(data)
    errors: list[str] = []
    active_count = 0

    for s in sessions:
        if s.is_active():
            active_count += 1
        if not s.branch:
            errors.append(f"{s.session_id}: chybí branch")
        if not s.head:
            errors.append(f"{s.session_id}: chybí head")

    if active_count > 1:
        errors.append(f"Více než jedno aktivní sezení ({active_count})")

    if errors:
        print("VALIDACE SELHALA:")
        for err in errors:
            print(f"  ERROR: {err}")
        return 1

    print(
        f"VALIDACE OK: {len(sessions)} sezení "
        f"({active_count} aktivní, {len(sessions) - active_count} uzavřeno)."
    )
    return 0


# ── Main ──────────────────────────────────────────────────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser(prog="ledger", description="STARCORE Session Ledger CLI")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("list", help="Vypsat sezení")
    sub.add_parser("current", help="Zobrazit aktivní sezení")

    p_start = sub.add_parser("start", help="Zahájit nové sezení")
    p_start.add_argument("--session-id", required=True)
    p_start.add_argument("--branch", required=True)
    p_start.add_argument("--head", required=True)

    p_end = sub.add_parser("end", help="Uzavřít aktivní sezení")
    p_end.add_argument("--next-action", default="")
    p_end.add_argument("--head")

    p_ap = sub.add_parser("add-prompt", help="Přidat použitý prompt")
    p_ap.add_argument("prompt_id")
    p_ap.add_argument("--session-id")

    p_ad = sub.add_parser("add-decision", help="Přidat rozhodnutí")
    p_ad.add_argument("text")
    p_ad.add_argument("--session-id")

    p_ar = sub.add_parser("add-risk", help="Přidat riziko")
    p_ar.add_argument("risk_id")
    p_ar.add_argument("--session-id")

    p_aa = sub.add_parser("add-approval", help="Přidat schválení")
    p_aa.add_argument("text")
    p_aa.add_argument("--session-id")

    p_ab = sub.add_parser("add-blocker", help="Přidat blokátor")
    p_ab.add_argument("text")
    p_ab.add_argument("--session-id")

    p_areq = sub.add_parser("add-request", help="Přidat user request")
    p_areq.add_argument("text")
    p_areq.add_argument("--session-id")

    p_acmd = sub.add_parser("add-command", help="Přidat spuštěný příkaz")
    p_acmd.add_argument("cmd")
    p_acmd.add_argument("--session-id")

    p_af = sub.add_parser("add-file", help="Přidat soubor")
    p_af.add_argument("path")
    p_af.add_argument(
        "--type", dest="file_type", choices=["created", "modified", "read"], required=True
    )
    p_af.add_argument("--session-id")

    p_at = sub.add_parser("add-test", help="Přidat test run")
    p_at.add_argument("--passed", type=int, required=True)
    p_at.add_argument("--failed", type=int, default=0)
    p_at.add_argument("--coverage", type=float, default=100.0)
    p_at.add_argument("--cmd", dest="test_cmd")

    p_rc = sub.add_parser("reconstruct", help="Rekonstruovat sezení")
    p_rc.add_argument("session_id")

    p_load = sub.add_parser("load", help="Načíst předchozí sezení")
    p_load.add_argument("session_id")

    sub.add_parser("validate", help="Ověřit integritu ledgeru")

    args = parser.parse_args()

    dispatch = {
        "list": cmd_list,
        "current": cmd_current,
        "start": cmd_start,
        "end": cmd_end,
        "add-prompt": cmd_add_prompt,
        "add-decision": cmd_add_decision,
        "add-risk": cmd_add_risk,
        "add-approval": cmd_add_approval,
        "add-blocker": cmd_add_blocker,
        "add-request": cmd_add_request,
        "add-command": cmd_add_command,
        "add-file": cmd_add_file,
        "add-test": cmd_add_test,
        "reconstruct": cmd_reconstruct,
        "load": cmd_load,
        "validate": cmd_validate,
    }

    if args.command not in dispatch:
        parser.print_help()
        return 1

    return dispatch[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
