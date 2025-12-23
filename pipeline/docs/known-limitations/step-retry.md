# Known Limitation: Step Retry NOT Enforced

The `PipelineStep.retries` property exists but is **NOT currently enforced**.

**Evidence:** `tests/characterization/test_characterization__step_retry_not_enforced.py` (4 tests)

## Summary

| Aspect | Status |
|--------|--------|
| Property exists | ✅ Yes |
| Property can be set | ✅ Yes |
| Retry is enforced | ❌ **NO** |

## The Issue

The `retries` property on `PipelineStep` is defined in the interface:

```python
class PipelineStep(ABC):
    @property
    def retries(self) -> int:
        """Number of retry attempts on failure."""
        return 0
```

**Source:** `src/task_pipeline/core/types.py`, lines 110-112

However, the `TaskExecutor` does **not** implement retry logic:

```python
class TaskExecutor:
    def execute(self, step: PipelineStep, context: PipelineContext) -> PipelineContext:
        # No retry logic here - just calls run() once
        try:
            result = step.run(context)
            return result
        except Exception as e:
            # Immediately handles error, no retry
            ...
```

**Source:** `src/task_pipeline/executors/task_executor.py`

## Demonstrated Behavior

### Step Retries Property Exists

```python
from task_pipeline import PipelineStep

class MyStep(PipelineStep):
    @property
    def retries(self) -> int:
        return 3  # Retry up to 3 times

step = MyStep()
assert step.retries == 3  # ✅ Property exists
```

**Evidence:** `test_characterization__step_retries_property_exists`

### Retries NOT Enforced for Critical Steps

```python
attempt_count = 0

class FailingStep(PipelineStep):
    @property
    def retries(self) -> int:
        return 3  # Should retry 3 times
    
    @property
    def critical(self) -> bool:
        return True
    
    def run(self, context):
        global attempt_count
        attempt_count += 1
        raise ValueError("Always fails")

pipeline = Pipeline([FailingStep()])

try:
    pipeline.run(context)
except RuntimeError:
    pass

assert attempt_count == 1  # Only called ONCE, not 4 times (1 + 3 retries)
```

**Evidence:** `test_characterization__step_retries_not_enforced_critical_step`

### Retries NOT Enforced for Non-Critical Steps

```python
attempt_count = 0

class FailingNonCriticalStep(PipelineStep):
    @property
    def retries(self) -> int:
        return 3
    
    @property
    def critical(self) -> bool:
        return False
    
    def run(self, context):
        global attempt_count
        attempt_count += 1
        raise ValueError("Always fails")

pipeline = Pipeline([FailingNonCriticalStep()])
pipeline.run(context)

assert attempt_count == 1  # Only called ONCE
```

**Evidence:** `test_characterization__step_retries_not_enforced_non_critical_step`

### Zero Retries Works as Expected

```python
class NoRetryStep(PipelineStep):
    @property
    def retries(self) -> int:
        return 0  # Default - no retries

step = NoRetryStep()
assert step.retries == 0  # Works correctly
```

**Evidence:** `test_characterization__step_retries_zero_default_works`

## Workarounds

### Implement Retry in Step

Handle retries within your step implementation:

```python
import time

class RetryableStep(PipelineStep):
    def run(self, context):
        last_error = None
        
        for attempt in range(self.retries + 1):
            try:
                return self._do_work(context)
            except Exception as e:
                last_error = e
                if attempt < self.retries:
                    context.logger_instance.warning(
                        f"Attempt {attempt + 1} failed, retrying..."
                    )
                    time.sleep(1)  # Backoff
        
        raise last_error
    
    def _do_work(self, context):
        # Actual work here
        ...
```

### Use tenacity Library

```python
from tenacity import retry, stop_after_attempt, wait_exponential

class RetryableStep(PipelineStep):
    @property
    def retries(self) -> int:
        return 3
    
    def run(self, context):
        @retry(
            stop=stop_after_attempt(self.retries + 1),
            wait=wait_exponential(multiplier=1, min=1, max=10)
        )
        def do_work():
            # Your logic here
            ...
        
        do_work()
        return context
```

## Status

**TODO:** Implement retry enforcement in `TaskExecutor.execute()` or remove the `retries` property from the interface.

## See Also

- [PipelineStep API](../api/pipeline-step.md) — Step interface
- [Error Handling Guide](../guides/error-handling.md) — Failure handling

