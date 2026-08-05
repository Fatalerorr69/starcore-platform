#!/usr/bin/env python3
"""
STARCORE Prompt Registry CLI.

Použití:
  uv run python .starcore/scripts/registry.py list
  uv run python .starcore/scripts/registry.py list --status ACTIVE
  uv run python .starcore/scripts/registry.py list --type MASTER
  uv run python .starcore/scripts/registry.py get PROM-001
  uv run python .starcore/scripts/registry.py register --name "..." --type MASTER --purpose "..."
  uv run python .starcore/scripts/registry.py update PROM-001 --status DEPRECATED
  uv run python .starcore/scripts/registry.py supersede PROM-001 --by PROM-006
  uv run python .starcore/scripts/registry.py search "timeout"
  uv run python .starcore/scripts/registry.py versions PROM-001
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

# Resolve registry path relative to this script's location
_SCRIPT_DIR = Path(__file__).parent
_STARCORE_DIR = _SCRIPT_DIR.parent
_REGISTRY_PATH = _STARCORE_DIR / "prompts" / "registry.yaml"

sys.path.insert(0, str(_SCRIPT_DIR))
from models import PromptEntry, PromptSource, PromptStatus, PromptType, now_iso  # noqa: E402


def _load_registry() -> dict:
    if not _REGISTRY_PATH.exists():
        return {"schema_version": "1.0", "prompts": []}
    with open(_REGISTRY_PATH) as f:
        data = yaml.safe_load(f) or {}
    if "prompts" not in data:
        data["prompts"] = []
    return data


def _save_registry(data: dict) -> None:
    _REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(_REGISTRY_PATH, "w") as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)


def _get_entries(data: dict) -> list[PromptEntry]:
    return [PromptEntry.from_dict(p) for p in data.get("prompts", [])]


def _find_entry(entries: list[PromptEntry], prompt_id: str) -> PromptEntry | None:
    return next((e for e in entries if e.id == prompt_id), None)


def _next_id(entries: list[PromptEntry]) -> str:
    ids = [e.id for e in entries if e.id.startswith("PROM-")]
    if not ids:
        return "PROM-001"
    nums = []
    for pid in ids:
        try:
            nums.append(int(pid.split("-")[1]))
        except (IndexError, ValueError):
            pass
    return f"PROM-{(max(nums) + 1):03d}" if nums else "PROM-001"


# ── Commands ──────────────────────────────────────────────────────────────────


def cmd_list(args: argparse.Namespace) -> int:
    data = _load_registry()
    entries = _get_entries(data)

    if args.status:
        entries = [e for e in entries if e.status.value == args.status]
    if args.type:
        entries = [e for e in entries if e.type.value == args.type]
    if args.session:
        entries = [e for e in entries if e.session_id == args.session]

    if not entries:
        print("Žádné záznamy nebyly nalezeny.")
        return 0

    print(f"{'ID':<12} {'NAME':<50} {'VER':<6} {'TYPE':<16} {'STATUS':<12} {'SESSION'}")
    print("-" * 110)
    for e in entries:
        sid = e.session_id or "-"
        if len(sid) > 20:
            sid = sid[:18] + ".."
        print(
            f"{e.id:<12} {e.name[:49]:<50} {e.version:<6} {e.type.value:<16} "
            f"{e.status.value:<12} {sid}"
        )
    return 0


def cmd_get(args: argparse.Namespace) -> int:
    data = _load_registry()
    entries = _get_entries(data)
    entry = _find_entry(entries, args.id)
    if not entry:
        print(f"CHYBA: Prompt '{args.id}' nenalezen.", file=sys.stderr)
        return 1

    d = entry.to_dict()
    for key, val in d.items():
        if val is not None and val != [] and val != "":
            print(f"  {key:<18}: {val}")
    return 0


def cmd_register(args: argparse.Namespace) -> int:
    data = _load_registry()
    entries = _get_entries(data)

    prompt_id = args.id or _next_id(entries)

    if _find_entry(entries, prompt_id):
        print(f"CHYBA: Prompt '{prompt_id}' existuje. Použij 'update'.", file=sys.stderr)
        return 1

    now = now_iso()
    entry = PromptEntry(
        id=prompt_id,
        name=args.name,
        version=args.version or "1.0",
        type=PromptType(args.type),
        purpose=args.purpose or "",
        status=PromptStatus(args.status or "DRAFT"),
        source=PromptSource(args.source or "USER"),
        created_at=now,
        updated_at=now,
        phase=args.phase,
        supersedes=args.supersedes,
        dependencies=args.dependencies or [],
        session_id=args.session_id,
        description=args.description or "",
    )

    data["prompts"].append(entry.to_dict())
    _save_registry(data)
    print(f"OK: Prompt '{prompt_id}' zaregistrován (status={entry.status.value}).")
    return 0


def cmd_update(args: argparse.Namespace) -> int:
    data = _load_registry()
    entries = _get_entries(data)
    entry = _find_entry(entries, args.id)
    if not entry:
        print(f"CHYBA: Prompt '{args.id}' nenalezen.", file=sys.stderr)
        return 1

    if args.status:
        entry.status = PromptStatus(args.status)
    if args.version:
        entry.version = args.version
    if args.purpose:
        entry.purpose = args.purpose
    if args.session_id:
        entry.session_id = args.session_id
    if args.description:
        entry.description = args.description
    if args.phase:
        entry.phase = args.phase
    if args.tags:
        entry.tags = args.tags
    entry.updated_at = now_iso()

    data["prompts"] = [e.to_dict() if e.id != args.id else entry.to_dict() for e in entries]
    _save_registry(data)
    print(f"OK: Prompt '{args.id}' aktualizován.")
    return 0


def cmd_supersede(args: argparse.Namespace) -> int:
    data = _load_registry()
    entries = _get_entries(data)

    old = _find_entry(entries, args.id)
    if not old:
        print(f"CHYBA: Prompt '{args.id}' nenalezen.", file=sys.stderr)
        return 1
    new = _find_entry(entries, args.by)
    if not new:
        print(f"CHYBA: Nahrazující prompt '{args.by}' nenalezen.", file=sys.stderr)
        return 1

    old.status = PromptStatus.SUPERSEDED
    old.superseded_by = args.by
    old.updated_at = now_iso()

    new.supersedes = args.id
    new.updated_at = now_iso()

    updated = []
    for e in entries:
        if e.id == old.id:
            updated.append(old.to_dict())
        elif e.id == new.id:
            updated.append(new.to_dict())
        else:
            updated.append(e.to_dict())
    data["prompts"] = updated
    _save_registry(data)
    print(f"OK: '{args.id}' → SUPERSEDED (nahrazen '{args.by}').")
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    data = _load_registry()
    entries = _get_entries(data)
    q = args.query.lower()

    matches = [
        e
        for e in entries
        if q in e.name.lower()
        or q in e.purpose.lower()
        or q in e.description.lower()
        or q in e.id.lower()
        or any(q in t.lower() for t in e.tags)
    ]

    if not matches:
        print(f"Žádné výsledky pro '{args.query}'.")
        return 0

    print(f"Nalezeno {len(matches)} výsledků pro '{args.query}':")
    for e in matches:
        print(f"  {e.id}  [{e.status.value}]  {e.name}  —  {e.purpose[:60]}")
    return 0


def cmd_versions(args: argparse.Namespace) -> int:
    data = _load_registry()
    entries = _get_entries(data)

    base_name = None
    entry = _find_entry(entries, args.id)
    if entry:
        base_name = entry.name.split("v")[0].strip()

    related = [
        e
        for e in entries
        if e.id == args.id
        or e.supersedes == args.id
        or e.superseded_by == args.id
        or (base_name and base_name in e.name)
    ]

    if not related:
        print(f"Žádné verze pro '{args.id}'.")
        return 0

    print(f"Verze pro '{args.id}':")
    for e in sorted(related, key=lambda x: x.created_at):
        arrow = ""
        if e.superseded_by:
            arrow = f" → nahrazen {e.superseded_by}"
        elif e.supersedes:
            arrow = f" ← nahrazuje {e.supersedes}"
        print(f"  {e.id}  v{e.version}  [{e.status.value}]  {e.name}{arrow}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:  # noqa: ARG001
    data = _load_registry()
    entries = _get_entries(data)
    errors: list[str] = []

    ids = [e.id for e in entries]

    for e in entries:
        errors.extend(
            f"{e.id}: dependency '{dep}' nenalezena" for dep in e.dependencies if dep not in ids
        )
        if e.supersedes and e.supersedes not in ids:
            errors.append(f"{e.id}: supersedes '{e.supersedes}' nenalezena")
        if e.superseded_by and e.superseded_by not in ids:
            errors.append(f"{e.id}: superseded_by '{e.superseded_by}' nenalezena")
        if e.status == PromptStatus.SUPERSEDED and not e.superseded_by:
            errors.append(f"{e.id}: status=SUPERSEDED ale superseded_by je prázdné")

    if errors:
        print("VALIDACE SELHALA:")
        for err in errors:
            print(f"  ERROR: {err}")
        return 1

    print(f"VALIDACE OK: {len(entries)} promptů, žádné chyby.")
    return 0


# ── Main ──────────────────────────────────────────────────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="registry",
        description="STARCORE Prompt Registry CLI",
    )
    sub = parser.add_subparsers(dest="command")

    # list
    p_list = sub.add_parser("list", help="Vypsat prompty")
    p_list.add_argument("--status", choices=[s.value for s in PromptStatus])
    p_list.add_argument("--type", choices=[t.value for t in PromptType])
    p_list.add_argument("--session")

    # get
    p_get = sub.add_parser("get", help="Detail promptu")
    p_get.add_argument("id")

    # register
    p_reg = sub.add_parser("register", help="Zaregistrovat nový prompt")
    p_reg.add_argument("--id", default=None)
    p_reg.add_argument("--name", required=True)
    p_reg.add_argument("--version", default="1.0")
    p_reg.add_argument("--type", choices=[t.value for t in PromptType], required=True)
    p_reg.add_argument("--purpose", default="")
    p_reg.add_argument("--status", choices=[s.value for s in PromptStatus], default="DRAFT")
    p_reg.add_argument("--source", choices=[s.value for s in PromptSource], default="USER")
    p_reg.add_argument("--phase")
    p_reg.add_argument("--supersedes")
    p_reg.add_argument("--dependencies", nargs="*", default=[])
    p_reg.add_argument("--session-id")
    p_reg.add_argument("--description", default="")

    # update
    p_upd = sub.add_parser("update", help="Aktualizovat prompt")
    p_upd.add_argument("id")
    p_upd.add_argument("--status", choices=[s.value for s in PromptStatus])
    p_upd.add_argument("--version")
    p_upd.add_argument("--purpose")
    p_upd.add_argument("--session-id")
    p_upd.add_argument("--description")
    p_upd.add_argument("--phase")
    p_upd.add_argument("--tags", nargs="*")

    # supersede
    p_sup = sub.add_parser("supersede", help="Označit prompt jako SUPERSEDED")
    p_sup.add_argument("id")
    p_sup.add_argument("--by", required=True, metavar="NEW_ID")

    # search
    p_srch = sub.add_parser("search", help="Fulltextové hledání")
    p_srch.add_argument("query")

    # versions
    p_ver = sub.add_parser("versions", help="Zobrazit verze/historii promptu")
    p_ver.add_argument("id")

    # validate
    sub.add_parser("validate", help="Ověřit integritu registru")

    args = parser.parse_args()

    dispatch = {
        "list": cmd_list,
        "get": cmd_get,
        "register": cmd_register,
        "update": cmd_update,
        "supersede": cmd_supersede,
        "search": cmd_search,
        "versions": cmd_versions,
        "validate": cmd_validate,
    }

    if args.command not in dispatch:
        parser.print_help()
        return 1

    return dispatch[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
