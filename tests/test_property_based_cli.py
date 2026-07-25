"""
Property-Based Tests — CLI

Verifies structural invariants for three pure-logic pieces in apps/cli/main.py:

  1. STATUS_COLORS lookup — the "white" fallback, known vs unknown status keys.
  2. Task-status count accumulation — the counting pattern used in runs_list.
  3. Snapshot payload construction — _run_snapshot_action always passes node/vmid
     and conditionally passes snapshot_name/description.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

from hypothesis import given
from hypothesis import strategies as st

from apps.cli.main import STATUS_COLORS, _run_snapshot_action

# ── Strategies ─────────────────────────────────────────────────────────────────

_KNOWN_STATUS = st.sampled_from(sorted(STATUS_COLORS))
_UNKNOWN_STATUS = st.text(min_size=1).filter(lambda s: s not in STATUS_COLORS)
_TASK_STATUS = st.sampled_from(["success", "failed", "skipped", "running", "pending"])
_NODE = st.text(alphabet="abcdefghijklmnopqrstuvwxyz", min_size=1, max_size=16)
_VMID = st.integers(min_value=100, max_value=9999)
_OPT_LABEL = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyz-",
    min_size=0,
    max_size=20,
)


# ── STATUS_COLORS properties ────────────────────────────────────────────────────


@given(status=st.text())
def test_status_color_lookup_never_returns_empty_string(status: str) -> None:
    """STATUS_COLORS.get(s, "white") always returns a non-empty string for any input."""
    assert STATUS_COLORS.get(status, "white") != ""


@given(status=_KNOWN_STATUS)
def test_status_color_known_status_returns_its_declared_color(status: str) -> None:
    """Each declared status maps to the exact color stored in STATUS_COLORS."""
    assert STATUS_COLORS[status] == STATUS_COLORS.get(status, "white")


@given(status=_UNKNOWN_STATUS)
def test_status_color_unknown_status_returns_white(status: str) -> None:
    """Any status not in STATUS_COLORS falls back to 'white'."""
    assert STATUS_COLORS.get(status, "white") == "white"


# ── Task-status count accumulation ─────────────────────────────────────────────
#
# Replicates the counting pattern from runs_list (apps/cli/main.py lines 122-126)
# in isolation:
#   counts[task.status] = counts.get(task.status, 0) + 1


def _count_statuses(statuses: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for status in statuses:
        counts[status] = counts.get(status, 0) + 1
    return counts


@given(statuses=st.lists(_TASK_STATUS, max_size=20))
def test_count_accumulation_sum_equals_total_tasks(statuses: list[str]) -> None:
    """Sum of all status counts always equals the total number of tasks."""
    assert sum(_count_statuses(statuses).values()) == len(statuses)


@given(statuses=st.lists(_TASK_STATUS, min_size=1, max_size=20))
def test_count_accumulation_keys_match_unique_statuses(statuses: list[str]) -> None:
    """Count dict keys exactly equal the set of distinct statuses in the input list."""
    assert set(_count_statuses(statuses).keys()) == set(statuses)


@given(statuses=st.lists(_TASK_STATUS, min_size=1, max_size=20))
def test_count_accumulation_every_count_is_positive(statuses: list[str]) -> None:
    """Every count value is a positive integer (no status can produce a zero count)."""
    assert all(v > 0 for v in _count_statuses(statuses).values())


@given(
    status=_TASK_STATUS,
    n=st.integers(min_value=1, max_value=10),
)
def test_count_accumulation_single_status_list_has_one_entry(status: str, n: int) -> None:
    """A homogeneous list of n identical statuses produces exactly {status: n}."""
    assert _count_statuses([status] * n) == {status: n}


@given(statuses=st.lists(_TASK_STATUS, max_size=20))
def test_count_accumulation_distinct_keys_le_total_tasks(statuses: list[str]) -> None:
    """The number of distinct status keys is always ≤ the total number of tasks."""
    assert len(_count_statuses(statuses)) <= len(statuses)


# ── Snapshot payload construction ──────────────────────────────────────────────


def _fake_task() -> MagicMock:
    t = MagicMock()
    t.status.value = "success"
    t.result = {}
    return t


@given(node=_NODE, vmid=_VMID)
def test_snapshot_action_payload_always_contains_node_and_vmid(node: str, vmid: int) -> None:
    """_run_snapshot_action always passes node and vmid in the payload dict."""
    with patch(
        "apps.cli.main.execute_resource_action", new=AsyncMock(return_value=_fake_task())
    ) as mock_exec:
        _run_snapshot_action("snapshot-list", node, vmid, "vm")

    payload = mock_exec.call_args.kwargs["payload"]
    assert payload["node"] == node
    assert payload["vmid"] == vmid


@given(node=_NODE, vmid=_VMID, snapshot_name=_OPT_LABEL)
def test_snapshot_action_snapshot_name_in_payload_iff_truthy(
    node: str, vmid: int, snapshot_name: str
) -> None:
    """snapshot_name is in the payload iff the argument is a non-empty string."""
    with patch(
        "apps.cli.main.execute_resource_action", new=AsyncMock(return_value=_fake_task())
    ) as mock_exec:
        _run_snapshot_action("snapshot-create", node, vmid, "vm", snapshot_name=snapshot_name)

    payload = mock_exec.call_args.kwargs["payload"]
    if snapshot_name:
        assert payload.get("snapshot_name") == snapshot_name
    else:
        assert "snapshot_name" not in payload


@given(node=_NODE, vmid=_VMID, description=_OPT_LABEL)
def test_snapshot_action_description_in_payload_iff_truthy(
    node: str, vmid: int, description: str
) -> None:
    """description is in the payload iff the argument is a non-empty string."""
    with patch(
        "apps.cli.main.execute_resource_action", new=AsyncMock(return_value=_fake_task())
    ) as mock_exec:
        _run_snapshot_action("snapshot-create", node, vmid, "vm", description=description)

    payload = mock_exec.call_args.kwargs["payload"]
    if description:
        assert payload.get("description") == description
    else:
        assert "description" not in payload


@given(node=_NODE, vmid=_VMID)
def test_snapshot_action_resource_string_is_node_colon_vmid(node: str, vmid: int) -> None:
    """_run_snapshot_action always passes '{node}:{vmid}' as the resource argument."""
    with patch(
        "apps.cli.main.execute_resource_action", new=AsyncMock(return_value=_fake_task())
    ) as mock_exec:
        _run_snapshot_action("snapshot-list", node, vmid, "vm")

    assert mock_exec.call_args.args[2] == f"{node}:{vmid}"
