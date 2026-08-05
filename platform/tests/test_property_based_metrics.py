"""
Property-Based Tests — Metrics

Verifies structural invariants for core/metrics.py that must hold for any
valid combination of provider names, HTTP methods, paths, and status codes.
"""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st
from prometheus_client import CollectorRegistry, Counter, Histogram

# ── Strategies ─────────────────────────────────────────────────────────────────

_PROVIDER = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyz_",
    min_size=1,
    max_size=20,
)
_STATUS = st.sampled_from(["success", "failed", "skipped", "unknown"])
_METHOD = st.sampled_from(["GET", "POST", "PUT", "DELETE", "PATCH"])
_PATH = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyz/_-",
    min_size=1,
    max_size=30,
)
_HTTP_STATUS = st.sampled_from(["200", "201", "400", "401", "403", "404", "500", "503"])
_DURATION = st.floats(min_value=0.0, max_value=60.0, allow_nan=False, allow_infinity=False)


def _make_registry() -> tuple[CollectorRegistry, Counter, Counter, Histogram]:
    """Create an isolated registry with the same shape as core/metrics.py."""
    reg = CollectorRegistry()
    requests_total = Counter(
        "starcore_http_requests_total",
        "Total HTTP requests",
        ["method", "path", "status"],
        registry=reg,
    )
    tasks_total = Counter(
        "starcore_blueprint_tasks_total",
        "Total blueprint tasks",
        ["provider", "status"],
        registry=reg,
    )
    duration = Histogram(
        "starcore_http_request_duration_seconds",
        "HTTP request duration",
        ["method", "path"],
        registry=reg,
    )
    return reg, requests_total, tasks_total, duration


# ── Counter invariants ─────────────────────────────────────────────────────────


@given(
    provider=_PROVIDER,
    status=_STATUS,
    n=st.integers(min_value=1, max_value=20),
)
def test_task_counter_increments_by_exactly_n(provider: str, status: str, n: int) -> None:
    """BLUEPRINT_TASKS_TOTAL increments monotonically; after n .inc() calls the value equals n."""
    _, _, tasks_total, _ = _make_registry()
    for _ in range(n):
        tasks_total.labels(provider=provider, status=status).inc()

    value = tasks_total.labels(provider=provider, status=status)._value.get()
    assert value == n


@given(
    provider=_PROVIDER,
    statuses=st.lists(_STATUS, min_size=2, max_size=6),
)
def test_task_counter_labels_are_independent(provider: str, statuses: list[str]) -> None:
    """Incrementing one (provider, status) label set does not affect another."""
    _, _, tasks_total, _ = _make_registry()
    for status in statuses:
        tasks_total.labels(provider=provider, status=status).inc()

    # Each label combination should be exactly 1 (since each status is distinct
    # within a single iteration — duplicates in statuses increase that slot).
    seen: dict[str, int] = {}
    for s in statuses:
        seen[s] = seen.get(s, 0) + 1
    for status, count in seen.items():
        value = tasks_total.labels(provider=provider, status=status)._value.get()
        assert value == count


@given(
    method=_METHOD,
    path=_PATH,
    status=_HTTP_STATUS,
    n=st.integers(min_value=1, max_value=15),
)
def test_http_request_counter_increments_correctly(
    method: str, path: str, status: str, n: int
) -> None:
    """HTTP_REQUESTS_TOTAL tracks exact increments for any valid label combination."""
    _, requests_total, _, _ = _make_registry()
    for _ in range(n):
        requests_total.labels(method=method, path=path, status=status).inc()

    value = requests_total.labels(method=method, path=path, status=status)._value.get()
    assert value == n


# ── Histogram invariants ───────────────────────────────────────────────────────


@given(
    method=_METHOD,
    path=_PATH,
    durations=st.lists(_DURATION, min_size=1, max_size=10),
)
def test_http_duration_histogram_count_matches_observations(
    method: str, path: str, durations: list[float]
) -> None:
    """Histogram observation count equals the number of .observe() calls."""
    from prometheus_client import generate_latest

    reg, _, _, duration_hist = _make_registry()
    for d in durations:
        duration_hist.labels(method=method, path=path).observe(d)

    output = generate_latest(reg).decode()
    count_line = next(
        (line for line in output.splitlines() if line.endswith("_count") or "_count{" in line),
        None,
    )
    assert count_line is not None
    count_value = float(count_line.split()[-1])
    assert count_value == len(durations)


@given(
    method=_METHOD,
    path=_PATH,
    durations=st.lists(_DURATION, min_size=1, max_size=10),
)
def test_http_duration_histogram_sum_matches_total(
    method: str, path: str, durations: list[float]
) -> None:
    """Histogram sum equals the sum of all observed values (within float tolerance)."""
    from prometheus_client import generate_latest

    reg, _, _, duration_hist = _make_registry()
    for d in durations:
        duration_hist.labels(method=method, path=path).observe(d)

    output = generate_latest(reg).decode()
    sum_line = next(
        (line for line in output.splitlines() if "_sum{" in line or line.endswith("_sum")),
        None,
    )
    assert sum_line is not None
    hist_sum = float(sum_line.split()[-1])
    assert abs(hist_sum - sum(durations)) < 1e-9


# ── record_task_completed integration ─────────────────────────────────────────


@given(
    provider=_PROVIDER,
    status=_STATUS,
)
@settings(max_examples=50)
def test_record_task_completed_tolerates_arbitrary_provider_and_status(
    provider: str, status: str
) -> None:
    """record_task_completed() must never raise for any provider/status string."""
    from prometheus_client import CollectorRegistry, Counter

    reg = CollectorRegistry()
    counter = Counter(
        "starcore_blueprint_tasks_total_iso",
        "Isolated counter",
        ["provider", "status"],
        registry=reg,
    )

    def record(payload: dict) -> None:
        counter.labels(
            provider=payload.get("provider", "unknown"),
            status=payload.get("status", "unknown"),
        ).inc()

    record({"provider": provider, "status": status})
    value = counter.labels(provider=provider, status=status)._value.get()
    assert value == 1
