# Testing with GitHub Copilot

This guide shows best practices for using GitHub Copilot to write tests for STARCORE Platform.

## Overview

GitHub Copilot excels at generating test code, especially:
- Unit tests for utility functions
- Parametrized tests with multiple scenarios
- Hypothesis property-based tests
- Test fixtures and conftest setup

## Getting Started

### 1. **Inline Test Generation**

Start typing a test function and let Copilot suggest:

```python
def test_retry_config_calculate_delay():
    """Test exponential backoff calculation."""
    # Copilot suggests: config = RetryConfig(max_retries=3, base_delay=1.0, exponential_base=2.0)
```

**Tip**: Use descriptive test names so Copilot understands the intent.

### 2. **Copilot Chat for Test Ideas**

Press `Ctrl+L` in VS Code to open Copilot Chat:

```
💬 "Generate unit tests for ExecutionPlanner.create_plan() with edge cases"
💬 "Write Hypothesis property test for TaskGraph circular dependency detection"
💬 "Create parametrized pytest tests for all provider implementations"
```

### 3. **Test Coverage Analysis**

```
💬 "Show me uncovered branches in packages/orchestrator/scheduler.py"
💬 "Generate tests for error paths in provider.execute()"
```

## Test Patterns

### Unit Tests (Simple)

**Prompt to Copilot Chat**:
```
"Generate pytest test for RetryConfig.calculate_delay() with different attempt numbers"
```

**Copilot generates**:
```python
import pytest
from provider_sdk.retry import RetryConfig


class TestRetryConfig:
    def test_calculate_delay_exponential(self):
        config = RetryConfig(base_delay=1.0, exponential_base=2.0, jitter=False)
        assert config.calculate_delay(0) == 1.0
        assert config.calculate_delay(1) == 2.0
        assert config.calculate_delay(2) == 4.0
    
    def test_calculate_delay_with_jitter(self):
        config = RetryConfig(base_delay=1.0, jitter=True)
        delay = config.calculate_delay(0)
        assert 0 <= delay <= 1.0
    
    def test_calculate_delay_max_delay(self):
        config = RetryConfig(base_delay=1.0, max_delay=10.0, exponential_base=2.0, jitter=False)
        # After several attempts, should cap at max_delay
        assert config.calculate_delay(5) == 10.0
```

**Review Copilot's output**:
- ✅ Are the test cases comprehensive?
- ✅ Do they cover edge cases (zero, negative, boundary values)?
- ✅ Are assertions clear and specific?

### Parametrized Tests

**Prompt**:
```
"Generate parametrized pytest test for TimeoutStrategy with CANCEL, WAIT_AND_MARK, IGNORE"
```

**Copilot generates**:
```python
import pytest
from orchestrator.timeout import TimeoutStrategy, TimeoutConfig


@pytest.mark.parametrize("strategy", [
    TimeoutStrategy.CANCEL,
    TimeoutStrategy.WAIT_AND_MARK,
    TimeoutStrategy.IGNORE,
])
def test_timeout_config_strategies(strategy):
    config = TimeoutConfig(timeout_seconds=5.0, strategy=strategy)
    assert config.strategy == strategy
    assert config.is_enabled()
```

### Property-Based Tests (Hypothesis)

**Prompt**:
```
"Generate Hypothesis property test for ExecutionPlanner ensuring topological sort is valid"
```

**Copilot generates**:
```python
from hypothesis import given, strategies as st
import pytest
from blueprints.planner import ExecutionPlanner
from blueprints.models import Blueprint, Resource


@given(
    resources=st.lists(
        st.builds(
            Resource,
            name=st.text(min_size=1),
            provider=st.just("docker"),
            kind=st.just("container"),
        ),
        min_size=1,
        max_size=10,
        unique_by=lambda r: r.name,
    )
)
def test_execution_plan_topologically_sorted(resources):
    """Property: execution plan respects dependency order."""
    blueprint = Blueprint(name="test", version="1.0.0", resources=resources)
    planner = ExecutionPlanner()
    plan = planner.create_plan(blueprint)
    
    # All resources should appear in plan
    assert len(plan) == len(resources)
    
    # No resource should appear before its dependencies
    seen = set()
    for step in plan:
        for dep in step.get("depends_on", []):
            assert dep in seen, f"Dependency {dep} not before {step['resource']}"
        seen.add(step["resource"])
```

## Test Fixtures

**Prompt**:
```
"Generate pytest fixtures for mocking Docker and Proxmox providers"
```

**Copilot generates** (add to `tests/conftest.py`):
```python
import pytest
from unittest.mock import AsyncMock, MagicMock
from providers.docker.provider import DockerProvider
from providers.proxmox.provider import ProxmoxProvider


@pytest.fixture
async def mock_docker_provider():
    provider = DockerProvider()
    provider.client = MagicMock()
    provider.connect = AsyncMock(return_value=True)
    provider.health = AsyncMock(return_value={"status": "ok"})
    provider.list_resources = AsyncMock(return_value=[])
    provider.execute = AsyncMock()
    return provider


@pytest.fixture
async def mock_proxmox_provider():
    provider = ProxmoxProvider()
    provider.client = MagicMock()
    provider.connect = AsyncMock(return_value=True)
    provider.health = AsyncMock(return_value={"status": "ok"})
    provider.list_resources = AsyncMock(return_value=[])
    provider.execute = AsyncMock()
    return provider
```

## Integration Tests

**Prompt**:
```
"Generate integration test for full blueprint execution with timeout"
```

**Copilot generates**:
```python
import pytest
from blueprints.models import Blueprint, Resource
from blueprints.executor import BlueprintExecutor
from orchestrator.timeout import TimeoutConfig


@pytest.mark.asyncio
async def test_blueprint_execution_with_timeout(mock_docker_provider):
    """Integration: Execute blueprint with timeout."""
    blueprint = Blueprint(
        name="test",
        version="1.0.0",
        resources=[
            Resource(
                name="web-container",
                provider="docker",
                kind="container",
                config={"image": "nginx:latest"},
            )
        ],
    )
    
    executor = BlueprintExecutor()
    tasks = await executor.execute(blueprint)
    
    assert len(tasks) == 1
    assert tasks[0].status.value == "success"
```

## Best Practices

### ✅ Do's

1. **Review generated tests carefully**
   - Copilot may miss edge cases
   - Verify assertions are correct
   - Check for mocking errors

2. **Use descriptive test names**
   - `test_retry_config_exponential_backoff()`
   - Better than `test_config()`

3. **Combine Copilot with manual testing**
   - Let Copilot write the skeleton
   - Add custom assertions
   - Add domain-specific edge cases

4. **Test async code properly**
   - Use `@pytest.mark.asyncio`
   - Use `AsyncMock` for async functions
   - Test concurrent execution with `asyncio.gather()`

### ❌ Don'ts

1. **Don't accept 100% of Copilot suggestions**
   - Tests may be incomplete
   - Edge cases might be missing
   - Mocking could be wrong

2. **Don't skip coverage requirements**
   - Run `make test-cov` regularly
   - 100% coverage is mandatory
   - Copilot-generated tests still need coverage verification

3. **Don't test implementation details**
   - Test behavior, not internal state
   - Copilot sometimes generates brittle tests

4. **Don't ignore test failures**
   - Flaky tests need investigation
   - Timeout-based tests need careful tuning

## Workflow

### Step 1: Write test skeleton
```python
def test_my_feature():
    """Test description."""
    # TODO: Setup
    # TODO: Act
    # TODO: Assert
```

### Step 2: Ask Copilot Chat
```
💬 "Complete this test for retry logic with multiple scenarios"
```

### Step 3: Review and refine
```python
# Copilot generated version
# Review:
# - ✅ Is setup correct?
# - ✅ Are mocks realistic?
# - ✅ Are assertions comprehensive?
# - ✅ Does it test the right thing?
```

### Step 4: Run and verify coverage
```bash
make test-cov
```

### Step 5: Iterate
```
💬 "Add test for error case when connection fails"
```

## Common Test Scenarios

### Scenario 1: Retry logic
```
💬 "Generate test showing retry succeeds after 2 failures"
```

### Scenario 2: Timeout handling
```
💬 "Generate test for task timeout with CANCEL strategy"
```

### Scenario 3: Request correlation
```
💬 "Generate test showing request ID propagates through async calls"
```

### Scenario 4: Circular dependencies
```
💬 "Generate test detecting circular dependencies in blueprint"
```

## Debugging Failed Tests

When Copilot-generated tests fail:

1. **Check test output**
   ```bash
   make test-verbose
   ```

2. **Ask Copilot to debug**
   ```
   💬 "Why would this test fail with 'assert error' message?"
   ```

3. **Add print debugging**
   ```python
   print(f"Debug: {variable}")
   pytest -s tests/test_file.py::test_name
   ```

4. **Check mocking setup**
   ```
   💬 "Show me correct AsyncMock setup for this function"
   ```

## Resources

- [Hypothesis Documentation](https://hypothesis.readthedocs.io/)
- [pytest Documentation](https://docs.pytest.org/)
- [Copilot Testing Tips](https://github.blog/2023-02-codespaces-google-cloud-marketplace/)
- [STARCORE Development Guide](development.md)

---

**Happy testing with Copilot!** 🚀
