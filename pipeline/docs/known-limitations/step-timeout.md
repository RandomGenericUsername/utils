# Known Limitation: Step Timeout NOT Enforced

The `PipelineStep.timeout` property exists but is **NOT currently enforced**.

**Evidence:** `tests/characterization/test_characterization__step_timeout_not_enforced.py` (4 tests)

## Summary

| Aspect | Status |
|--------|--------|
| Property exists | ✅ Yes |
| Property can be set | ✅ Yes |
| Timeout is enforced | ❌ **NO** |

## The Issue

The `timeout` property on `PipelineStep` is defined in the interface:

```python
class PipelineStep(ABC):
    @property
    def timeout(self) -> float | None:
        """Timeout in seconds for step execution."""
        return None
```

**Source:** `src/task_pipeline/core/types.py`, lines 106-108

However, the `TaskExecutor` does **not** enforce this timeout:

```python
class TaskExecutor:
    def execute(self, step: PipelineStep, context: PipelineContext) -> PipelineContext:
        # No timeout enforcement here!
        result = step.run(context)
        return result
```

**Source:** `src/task_pipeline/executors/task_executor.py`

## Demonstrated Behavior

### Step Timeout Property Exists

```python
from task_pipeline import PipelineStep

class MyStep(PipelineStep):
    @property
    def timeout(self) -> float | None:
        return 5.0  # 5 second timeout

step = MyStep()
assert step.timeout == 5.0  # ✅ Property exists
```

**Evidence:** `test_characterization__step_timeout_property_exists`

### Timeout NOT Enforced in Serial Execution

```python
class SlowStep(PipelineStep):
    @property
    def timeout(self) -> float | None:
        return 0.1  # 100ms timeout
    
    def run(self, context):
        time.sleep(0.5)  # Runs for 500ms
        return context

pipeline = Pipeline([SlowStep()])
result = pipeline.run(context)  # Does NOT timeout!
```

**Evidence:** `test_characterization__step_timeout_not_enforced_in_serial_execution`

### Multiple Steps with Timeout NOT Enforced

```python
pipeline = Pipeline([
    SlowStep("step1"),  # 100ms timeout, runs 500ms
    SlowStep("step2"),  # 100ms timeout, runs 500ms
])
result = pipeline.run(context)  # Neither step times out!
```

**Evidence:** `test_characterization__multiple_steps_with_timeout_not_enforced`

## Workarounds

### Use Parallel Group Timeout

For parallel step groups, `ParallelConfig.timeout` **IS enforced**:

```python
from task_pipeline import ParallelConfig

config = ParallelConfig(timeout=5.0)  # This timeout IS enforced
```

**Evidence:** `tests/integration/test_advanced_scenarios.py::test_parallel_group_timeout_enforced`

### Implement Timeout in Step

Handle timeout within your step implementation:

```python
import signal

class TimeoutStep(PipelineStep):
    def run(self, context):
        def handler(signum, frame):
            raise TimeoutError("Step timed out")
        
        signal.signal(signal.SIGALRM, handler)
        signal.alarm(int(self.timeout or 0))
        
        try:
            # Your logic here
            result = do_work()
        finally:
            signal.alarm(0)
        
        return context
```

> ⚠️ **Note:** `signal.alarm` only works on Unix systems and in the main thread.

### Use threading.Timer

```python
import threading

class TimeoutStep(PipelineStep):
    def run(self, context):
        result = [None]
        error = [None]
        
        def target():
            try:
                result[0] = do_work()
            except Exception as e:
                error[0] = e
        
        thread = threading.Thread(target=target)
        thread.start()
        thread.join(timeout=self.timeout)
        
        if thread.is_alive():
            raise TimeoutError(f"Step {self.step_id} timed out")
        
        if error[0]:
            raise error[0]
        
        return context
```

## Status

**TODO:** Implement timeout enforcement in `TaskExecutor.execute()` or remove the `timeout` property from the interface.

## See Also

- [PipelineStep API](../api/pipeline-step.md) — Step interface
- [ParallelConfig API](../api/parallel-config.md) — Parallel timeout (enforced)

