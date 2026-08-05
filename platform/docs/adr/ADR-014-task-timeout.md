# ADR-014: Task Timeout Support

> **Note (2026-07-26):** The environment variables `STARCORE_TASK_TIMEOUT_SECONDS` and
> `STARCORE_TASK_TIMEOUT_STRATEGY` described in this document are **not wired into
> `Settings` or the scheduler**. `execute_with_timeout` exists in
> `orchestrator/timeout.py` but is not called by `Scheduler` or `BlueprintExecutor`.
> The deliberate deferral of this integration is documented in
> [ADR-016](ADR-016-task-timeout-integration.md).

**Status**: Accepted  
**Date**: 2026-07-26  
**Deciders**: STARCORE Development Team

## Context

STARCORE Platform executes infrastructure blueprints against Proxmox and Docker providers. Some provider operations may hang indefinitely due to:
- Network connectivity issues
- Provider API bugs
- Resource constraints
- Incorrect provider configuration

With `--parallel` execution, a single hung task blocks an entire "wave" of concurrent tasks, potentially stalling the entire orchestration run indefinitely.

## Problem

Currently, there is no timeout mechanism for task execution. A hung provider operation will hang the orchestrator.

### Example
```bash
uv run starcore blueprint run blueprint.yaml --parallel
# Stuck forever if any provider.execute() hangs
```

## Decision

Implement task timeout support with three configurable strategies:

### 1. **CANCEL** (Default)
- Immediately cancel the task if it exceeds timeout
- Mark task as `FAILED` with timeout error
- Continue with next wave
- **Use case**: Strict deadline requirements, invalid blueprints

### 2. **WAIT_AND_MARK** 
- Wait a bit longer for graceful completion
- If still not done, mark as timed out (don't cancel)
- Task state may be partially updated on provider
- **Use case**: Flaky providers that need grace period

### 3. **IGNORE**
- Log warning but continue waiting
- No enforced timeout (fire-and-forget)
- **Use case**: Future use, monitoring-only scenarios

## Implementation

```python
from orchestrator.timeout import TimeoutConfig, TimeoutStrategy, execute_with_timeout

# Configuration
config = TimeoutConfig(
    timeout_seconds=300.0,          # 5 minutes
    strategy=TimeoutStrategy.CANCEL,  # or WAIT_AND_MARK, IGNORE
)

# Usage
await execute_with_timeout(
    coro=provider.execute(task),
    config=config,
    task_id=task.id,
    resource=task.resource,
)
```

## Environment Variables

> **Planned, not yet implemented.** No `STARCORE_TASK_TIMEOUT_SECONDS` or
> `STARCORE_TASK_TIMEOUT_STRATEGY` field exists in `core/config.py`. Scheduler
> wiring is deferred pending per-task `timeout_seconds` in the blueprint schema
> (see ADR-016). Once that field is added, a per-task `TimeoutConfig` can be
> constructed from it at runtime without any global env var.

## Rationale

1. **asyncio.wait_for()** is the right primitive
   - Lightweight, no thread overhead
   - Standard library, well-tested
   - Works with async context propagation

2. **Multiple strategies** provide flexibility
   - CANCEL: Strict, prevents hangs
   - WAIT_AND_MARK: Graceful degradation for flaky providers
   - IGNORE: Future extensibility

3. **Configuration-driven** vs. hardcoded
   - Different environments need different timeouts
   - Homelabs may have slow I/O, enterprise datacenters are fast
   - Users should control timeout behavior per task via the blueprint schema
     (once per-task `timeout_seconds` is added; see ADR-016)

4. **Backward compatible**
   - Timeout disabled by default (timeout_seconds=None)
   - Existing code requires no changes
   - Gradual adoption

## Consequences

### Positive
- ✅ Prevents orchestrator hangs
- ✅ Better error diagnostics (timeout vs. silence)
- ✅ Enables SLA compliance (strict timeouts)
- ✅ Works seamlessly with parallel execution
- ✅ Observable in logs and metrics

### Negative
- ❌ Need to tune timeouts per environment
- ❌ May incorrectly timeout slow-but-valid operations
- ❌ Adds complexity to provider implementations

### Neutral
- Adds observability/debugging capability
- Requires per-task timeout tuning once the blueprint schema supports it

## Alternatives Considered

### 1. Thread-based timeout (Rejected)
- Complex, hard to cancel safely
- Resource overhead
- Doesn't work well with async/await

### 2. Process-level timeout (Rejected)
- Too coarse-grained (affects entire process)
- Hard to recover from
- Not suitable for orchestration

### 3. Fixed global timeout (Rejected)
- Different providers have different characteristics
- Blueprint complexity varies
- Environment-specific (homelab vs. enterprise)

## Testing

```bash
# Unit tests (covering all TimeoutConfig / TimeoutStrategy / execute_with_timeout paths)
uv run pytest tests/test_timeout.py -v

# Property-based tests
uv run pytest tests/test_property_based_timeout.py -v
```

## References

- [asyncio.wait_for()](https://docs.python.org/3/library/asyncio-task.html#asyncio.wait_for)
- [Task Timeout Pattern](https://en.wikipedia.org/wiki/Timeout_(computing))
- ADR-010: Dependency Success Gates
