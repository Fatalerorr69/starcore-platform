# ADR-015: Request Correlation via Context Variables

**Status**: Accepted  
**Date**: 2026-07-26  
**Deciders**: STARCORE Development Team

## Context

STARCORE Platform uses async/await and event-driven architecture. Multiple concurrent tasks may emit logs across different modules and providers.

### Problem: Log Correlation

When a user makes a single API request, it may trigger:
1. Blueprint loading
2. Dependency resolution
3. Multiple concurrent provider calls (with `--parallel`)
4. Event emissions (task.started, task.completed, run.completed)
5. Database persistence

All these operations emit logs, but without correlation, it's hard to tie them together:

```json
{"text": "Blueprint loaded", "timestamp": "2026-07-26T10:00:00Z"}
{"text": "Executing task for web-vm", "timestamp": "2026-07-26T10:00:01Z"}  // <-- which request?
{"text": "Provider connection established", "timestamp": "2026-07-26T10:00:02Z"}
```

## Decision

Use **contextvars.ContextVar** to propagate request ID through async execution:

1. **Accept or generate X-Request-ID header** (HTTP level)
2. **Store in ContextVar** (process level)
3. **Auto-propagate through asyncio** (coroutine level)
4. **Include in all logs** (logging level)

## Implementation

### Core Mechanism

```python
# packages/core/correlation.py
import contextvars

_request_id_context = contextvars.ContextVar("request_id", default=None)

def set_request_id(request_id: str) -> None:
    _request_id_context.set(request_id)

def get_request_id() -> str | None:
    return _request_id_context.get()
```

### Middleware Integration

```python
# packages/core/request_id_middleware.py
from fastapi import Request

class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Get or generate request ID
        request_id = resolve_request_id(request.headers.get("x-request-id"))
        
        # Bind to context
        contextualize_request(request_id)
        
        # Process request (auto-propagated to all async calls)
        response = await call_next(request)
        
        # Echo in response
        response.headers["X-Request-ID"] = request_id
        return response
```

### Usage (Automatic)

```bash
# User sends request with custom ID
curl -H "X-Request-ID: user-req-123" http://localhost:8000/blueprints/run

# All logs from this request automatically include:
# {"text": "...", "request_id": "user-req-123", ...}
```

## Why contextvars?

### ✅ Why contextvars is ideal

1. **Designed for async**: Automatically copies context to child tasks
   ```python
   # No manual plumbing needed!
   await asyncio.gather(task1(), task2())  # Both see same request_id
   ```

2. **Zero overhead**: Just a dict lookup per access
   ```python
   logger.contextualize(request_id=get_request_id())  # ~1μs
   ```

3. **Works with asyncio.TaskGroup**, task spawning
   ```python
   async with asyncio.TaskGroup() as tg:
       tg.create_task(task1())  # Inherits context
       tg.create_task(task2())  # Inherits context
   ```

4. **Integrated with loguru**: Auto-inclusion in logs
   ```python
   logger.contextualize(request_id=request_id)
   logger.info("Something happened")  # request_id auto-included
   ```

### ❌ Why NOT thread-local storage
- Doesn't work with async (different threads per task)
- Would require manual propagation

### ❌ Why NOT global state
- Thread-unsafe
- Race conditions under concurrency
- Can't isolate different requests

## Output Example

**Request**: `curl -H "X-Request-ID: run-abc123" http://localhost:8000/blueprints/run`

**Logs**:
```json
{"text": "HTTP request started", "request_id": "run-abc123", "method": "POST", "path": "/blueprints/run"}
{"text": "Loading blueprint", "request_id": "run-abc123"}
{"text": "Planning execution", "request_id": "run-abc123"}
{"text": "Executing wave 1 with 3 tasks", "request_id": "run-abc123"}
{"text": "Connecting to docker provider", "request_id": "run-abc123"}
{"text": "Connecting to proxmox provider", "request_id": "run-abc123"}
{"text": "Executing task 'db' on docker", "request_id": "run-abc123"}
{"text": "Task 'db' succeeded", "request_id": "run-abc123"}
{"text": "Blueprint execution complete", "request_id": "run-abc123"}
{"text": "HTTP response sent", "request_id": "run-abc123", "status_code": 200}
```

**Grep for correlation**:
```bash
jq '.request_id == "run-abc123"' starcore.jsonl | wc -l
# Shows all events tied to this request
```

## Integration with Observability

### Prometheus
```python
# Can tag metrics with request_id
http_request_duration.labels(request_id=get_request_id()).observe(duration)
```

### Jaeger / OpenTelemetry
```python
# Can inject request_id into trace span
span.set_attribute("request_id", get_request_id())
```

### Elasticsearch/ELK
```bash
# Query logs by correlation ID
POST /logs/_search
{"query": {"match": {"request_id": "run-abc123"}}}
```

## Testing

```bash
# Unit test
uv run pytest tests/test_correlation.py -v

# Integration test
uv run pytest tests/integration/test_request_correlation.py -v

# Manual test
curl -H "X-Request-ID: test-123" http://localhost:8000/blueprints/run 2>&1 | grep test-123
```

## Backward Compatibility

✅ **Fully backward compatible**
- No code changes required
- Automatic via middleware
- Graceful fallback (generates UUID if no header)
- Optional (logging still works without correlation)

## References

- [Python contextvars Documentation](https://docs.python.org/3/library/contextvars.html)
- [asyncio Context Propagation](https://docs.python.org/3/library/contextvars.html#asyncio-task-creation)
- [Correlation IDs Best Practices](https://github.com/jaegertracing/jaeger/blob/main/docs/sampling.md)
- [loguru contextualize()](https://loguru.readthedocs.io/en/stable/api/logger.html#contextualize)
- ADR-010: Dependency Success Gates
