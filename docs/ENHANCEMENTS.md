# STARCORE Platform Enhancements

**Version**: 0.1.0  
**Date**: 2026-07-26  
**Branch**: `chore/copilot-integration-and-enhancements`

## Overview

This package implements production-ready enhancements to STARCORE Platform:

1. ✅ **GitHub Copilot Integration** – IDE configuration, coding guidelines
2. ✅ **Retry Logic with Exponential Backoff** – Resilient provider connections
3. ✅ **Task Timeout Support** – Prevent hung tasks, configurable strategies
4. ✅ **Request Correlation** – X-Request-ID propagation for observability
5. ✅ **Automation Scripts** – One-command setup and verification
6. ✅ **Documentation** – Testing guides, ADRs, upgrade instructions

---

## Installation & Setup

### Quick Start (Automated)

```bash
# Clone and setup
git clone https://github.com/Fatalerorr69/starcore-platform.git
cd starcore-platform
git checkout chore/copilot-integration-and-enhancements

# Run master setup script
bash scripts/setup-copilot.sh

# Verify integration
bash scripts/verify-integration.sh
```

### Manual Setup

1. **Install GitHub Copilot**
   ```bash
   # VS Code
   code --install-extension github.copilot
   code --install-extension github.copilot-chat
   code --install-extension charliermarsh.ruff
   ```

2. **Verify IDE Configuration**
   ```bash
   # Check .vscode/settings.json is loaded
   code --version
   ```

3. **Verify Python Environment**
   ```bash
   uv sync --extra dev
   uv run pyright --version
   ```

---

## New Features

### 1. Retry Logic (`packages/provider_sdk/retry.py`)

**Problem**: Provider connections may fail transiently (network hiccups, timeouts).  
**Solution**: Exponential backoff retry with jitter.

**Usage**:
```python
from provider_sdk.retry import RetryConfig, attempt_with_retry

config = RetryConfig(
    max_retries=3,
    base_delay=1.0,
    max_delay=30.0,
    exponential_base=2.0,
    jitter=True,
)

result = await attempt_with_retry(
    operation=provider.connect,
    config=config,
    operation_name="connect to Proxmox",
)
```

**Key Features**:
- ✅ Configurable max retries, delays, exponential base
- ✅ Jitter prevents "thundering herd"
- ✅ Selective exception retrying (configurable)
- ✅ Comprehensive logging
- ✅ Non-retryable exceptions fail fast

**Defaults**:
- `max_retries=3`
- `base_delay=1.0s`
- `max_delay=30.0s`
- `exponential_base=2.0`
- Retryable: `ConnectionError`, `TimeoutError`, `OSError`

### 2. Task Timeout Support (`packages/orchestrator/timeout.py`)

**Problem**: Long-running tasks can hang the orchestrator.  
**Solution**: Configurable timeout with three strategies.

**Usage**:
```python
from orchestrator.timeout import TimeoutConfig, TimeoutStrategy, execute_with_timeout

config = TimeoutConfig(
    timeout_seconds=300.0,  # 5 minutes
    strategy=TimeoutStrategy.CANCEL,
)

try:
    result = await execute_with_timeout(
        coro=provider.execute(task),
        config=config,
        task_id=task.id,
        resource=task.resource,
    )
except TaskTimeoutError as exc:
    logger.error(f"Task timed out: {exc}")
    task.status = TaskStatus.FAILED
    task.result = {"error": str(exc)}
```

**Strategies**:
- `CANCEL` (default): Immediately cancel the task
- `WAIT_AND_MARK`: Wait a bit longer, then mark as timed out
- `IGNORE`: Log warning but continue (useful for fire-and-forget)

**Configuration** (environment variables):
```bash
STARCORE_TASK_TIMEOUT_SECONDS=300
STARCORE_TASK_TIMEOUT_STRATEGY=cancel
```

### 3. Request Correlation (`packages/core/correlation.py`)

**Problem**: Distributed logs across async tasks are hard to correlate.  
**Solution**: X-Request-ID header + contextvars propagation.

**Usage** (automatic via middleware):
```bash
curl -H "X-Request-ID: my-correlation-id" http://localhost:8000/blueprints/run
# Response includes: X-Request-ID: my-correlation-id
```

**All logs from this request** will include `request_id=my-correlation-id`:
```json
{"text": "Starting blueprint execution", "request_id": "my-correlation-id", ...}
```

**Propagation**: Automatic across all `await` calls (via asyncio.contextvars).

---

## Configuration

### Environment Variables

```bash
# Retry behavior (global defaults)
STARCORE_PROVIDER_RETRY_MAX_RETRIES=3
STARCORE_PROVIDER_RETRY_BASE_DELAY=1.0
STARCORE_PROVIDER_RETRY_MAX_DELAY=30.0

# Task timeout
STARCORE_TASK_TIMEOUT_SECONDS=300
STARCORE_TASK_TIMEOUT_STRATEGY=cancel  # cancel|wait_and_mark|ignore

# Request correlation
STARCORE_REQUEST_ID_HEADER=X-Request-ID  # Custom header name
```

### Per-Provider Configuration

```python
# In provider __init__ or settings
from provider_sdk import RetryConfig

class MyProvider(BaseProvider):
    retry_config = RetryConfig(
        max_retries=5,
        base_delay=0.5,
        exponential_base=1.5,
    )
```

---

## Testing

### Unit Tests

```bash
# Test retry logic
uv run pytest tests/test_retry.py -v

# Test timeout
uv run pytest tests/test_timeout.py -v

# Test correlation
uv run pytest tests/test_correlation.py -v

# All with coverage
uv run pytest tests/ -v --cov --cov-fail-under=100
```

### Integration Tests

```bash
# Test retry with real provider
uv run pytest tests/integration/test_provider_retry.py -v

# Test timeout in parallel execution
uv run pytest tests/integration/test_scheduler_timeout.py -v
```

---

## Backward Compatibility

✅ **Fully backward compatible**

- Retry logic is **optional** (providers can opt-in)
- Timeout is **disabled by default** (can be enabled per-task)
- Request correlation is **automatic** (no code changes required)
- All existing code continues to work without modification

---

## Migration Guide

### For Provider Implementations

**Before** (no retry):
```python
async def connect(self) -> bool:
    self.client = await proxmoxer.ProxmoxAsync(...)
    return True
```

**After** (with retry):
```python
from provider_sdk import attempt_with_retry, RetryConfig

async def connect(self) -> bool:
    async def _connect():
        self.client = await proxmoxer.ProxmoxAsync(...)
        return True
    
    await attempt_with_retry(
        _connect,
        config=self.retry_config,
        operation_name=f"connect to {self.name}",
    )
    return True
```

### For Executors

**Before** (no timeout):
```python
await provider.execute(task)
```

**After** (with timeout):
```python
from orchestrator.timeout import execute_with_timeout, TimeoutConfig

config = TimeoutConfig(timeout_seconds=300.0)
await execute_with_timeout(
    provider.execute(task),
    config=config,
    task_id=task.id,
    resource=task.resource,
)
```

---

## Architecture Decision Records (ADRs)

### ADR-014: Task Timeout Support

**Status**: Accepted  
**Date**: 2026-07-26

**Problem**:  
Long-running provider operations can hang the entire orchestrator, especially with `--parallel` execution. Need timeout mechanism.

**Decision**:  
Implement `TimeoutConfig` with three strategies (CANCEL/WAIT_AND_MARK/IGNORE) to handle different timeout scenarios flexibly.

**Rationale**:
- CANCEL (default): Fail fast for incorrect blueprints
- WAIT_AND_MARK: Graceful degradation for flaky providers
- IGNORE: Fire-and-forget scenarios (future use)

**Consequences**:
- Tasks can now fail due to timeout (new TaskStatus)
- Need to configure timeouts appropriately per environment
- Better observability of long-running operations

### ADR-015: Request Correlation

**Status**: Accepted  
**Date**: 2026-07-26

**Problem**:  
With async concurrency and event-driven architecture, logs from related operations are scattered. Need correlation mechanism.

**Decision**:  
Use `contextvars.ContextVar` to propagate X-Request-ID through async context. Automatic via middleware, no code changes needed.

**Rationale**:
- contextvars is designed for this exact use case
- Automatically propagates through all `await` calls
- Works with asyncio.gather() and task spawning
- Zero performance overhead when not using correlation

**Consequences**:
- All logs automatically include request_id
- Easier distributed debugging
- Can integrate with tracing systems (Jaeger, etc.)

---

## Performance Considerations

### Retry Logic
- **Overhead**: Minimal (just timing and exception handling)
- **Memory**: O(1) per operation
- **Network**: May send more requests if misconfigured (jitter helps)

### Task Timeout
- **Overhead**: Negligible (asyncio.wait_for() is efficient)
- **Memory**: O(1) per task
- **Latency**: Zero if timeout not exceeded

### Request Correlation
- **Overhead**: Negligible (<1µs per contextvars access)
- **Memory**: O(1) per active request
- **Logging**: Adds ~20 bytes per log line

---

## Troubleshooting

### Retries happening too frequently

**Problem**: Providers are retrying when they shouldn't  
**Solution**: Adjust `RetryConfig`:

```python
config = RetryConfig(
    max_retries=1,  # Only retry once
    retryable_exceptions=(ConnectionError,),  # Only retry specific errors
)
```

### Tasks timing out unexpectedly

**Problem**: Timeout is too aggressive  
**Solution**: Increase timeout:

```bash
export STARCORE_TASK_TIMEOUT_SECONDS=600  # 10 minutes
uv run starcore blueprint run blueprint.yaml
```

### Request IDs not appearing in logs

**Problem**: Correlation not working  
**Solution**: Check middleware is loaded in FastAPI app:

```python
from core.request_id_middleware import RequestIdMiddleware
app.add_middleware(RequestIdMiddleware)
```

---

## Roadmap

- [ ] Circuit breaker pattern for provider failures
- [ ] Adaptive timeout based on task history
- [ ] Distributed tracing integration (Jaeger)
- [ ] Metrics dashboard for retry/timeout stats
- [ ] Rate limiting per provider

---

## Related Documentation

- [Testing with Copilot](./testing-with-copilot.md) – Testing strategies
- [Development](./development.md) – Development workflow
- [ADRs](./adr/ADR-001-blueprint-dependency-execution.md) – Architectural decisions

---

**Questions?** Open an issue or check [GitHub Discussions](https://github.com/Fatalerorr69/starcore-platform/discussions)
