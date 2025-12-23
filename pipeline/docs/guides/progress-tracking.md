# Progress Tracking

Monitor pipeline execution with progress callbacks.

**Evidence:** `tests/integration/test_progress_tracking.py` (7 tests)

## Overview

Pass a callback function to receive progress updates during execution:

```python
def my_callback(step_idx: int, total: int, name: str, progress: float) -> None:
    print(f"[{step_idx}/{total}] {name}: {progress:.1f}%")

pipeline = Pipeline(steps, progress_callback=my_callback)
```

## Callback Signature

```python
Callable[[int, int, str, float], None]
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `step_idx` | `int` | Current step index (0-based) |
| `total` | `int` | Total number of steps |
| `name` | `str` | Current step's `step_id` |
| `progress` | `float` | Overall progress percentage (0.0 - 100.0) |

**Evidence:** `test_progress_callback_invoked_for_each_step`

## Basic Usage

```python
from task_pipeline import Pipeline, PipelineContext

progress_log = []

def track_progress(step_idx, total, name, progress):
    progress_log.append({
        "step": step_idx,
        "total": total,
        "name": name,
        "progress": progress
    })

pipeline = Pipeline(
    steps=[step1, step2, step3],
    progress_callback=track_progress
)

result = pipeline.run(context)

# progress_log contains all updates
for entry in progress_log:
    print(f"{entry['name']}: {entry['progress']:.1f}%")
```

## Progress Values

Progress increases monotonically through execution:

```python
# For 3 steps:
# Step 0 complete: ~33.3%
# Step 1 complete: ~66.7%
# Step 2 complete: 100.0%
```

**Evidence:** `test_progress_callback_receives_increasing_progress`

### Reaching 100%

Progress reaches exactly 100% when all steps complete:

```python
final_progress = None

def track(step_idx, total, name, progress):
    global final_progress
    final_progress = progress

pipeline = Pipeline(steps, progress_callback=track)
pipeline.run(context)

assert final_progress == 100.0
```

**Evidence:** `test_progress_callback_reaches_100_percent`

## Progress with Parallel Steps

For parallel groups, progress is tracked at the group level:

```python
pipeline = Pipeline([
    step1,              # Progress update after completion
    [step2, step3],     # Single progress update for whole group
    step4               # Progress update after completion
])
```

**Evidence:** `test_progress_callback_with_parallel_steps`

## Without Progress Callback

Pipelines work fine without a progress callback:

```python
# No callback - silent execution
pipeline = Pipeline(steps)
result = pipeline.run(context)

# Explicit None - same behavior
pipeline = Pipeline(steps, progress_callback=None)
```

**Evidence:** `test_pipeline_works_without_progress_callback`, `test_pipeline_with_none_callback_explicit`

## Mixed Serial and Parallel

```python
pipeline = Pipeline([
    serial_step,        # 1 unit
    [p1, p2, p3],       # 1 unit (group)
    another_serial      # 1 unit
])
# Total: 3 units for progress calculation
```

**Evidence:** `test_progress_with_mixed_serial_and_parallel`

## Granular Progress Within Steps

Steps can report their own internal progress using `context.update_step_progress()`:

```python
class DataProcessingStep(PipelineStep):
    def run(self, context: PipelineContext) -> PipelineContext:
        items = ["item1", "item2", "item3", "item4", "item5"]

        for i, item in enumerate(items):
            # Do work...
            progress = ((i + 1) / len(items)) * 100
            context.update_step_progress(progress)

        return context
```

This allows fine-grained progress updates within a single step.

**Evidence:** `test_step_can_report_granular_progress`

## Querying Progress with get_status()

Use `Pipeline.get_status()` to query progress at any time:

```python
pipeline = Pipeline(steps)
status = pipeline.get_status()

print(status["progress"])       # Overall progress (0-100)
print(status["current_step"])   # Current step ID or None
print(status["is_running"])     # True during execution

# Per-step details
for step_id, details in status["step_details"].items():
    print(f"{step_id}: {details['internal_progress']:.1f}%")
    print(f"  Weight: {details['max_weight']:.2f}%")
    print(f"  Contribution: {details['contribution']:.2f}%")
```

**Evidence:** `test_get_status_returns_step_details`

## Real-Time Progress Monitoring

Query progress from another thread during execution:

```python
import threading

def monitor(pipeline: Pipeline, stop_event: threading.Event):
    while not stop_event.is_set():
        status = pipeline.get_status()
        print(f"Progress: {status['progress']:.1f}%")
        time.sleep(0.1)

# Start monitor in background
stop_event = threading.Event()
thread = threading.Thread(target=monitor, args=(pipeline, stop_event))
thread.start()

# Run pipeline
result = pipeline.run(context)

# Stop monitor
stop_event.set()
thread.join()
```

**Evidence:** `test_get_status_can_be_called_during_execution`

## The @with_progress_callback Decorator

Use this decorator for utility functions that need progress reporting:

```python
from task_pipeline import with_progress_callback

@with_progress_callback
def complex_operation(data: str, progress_callback) -> str:
    progress_callback(25.0)   # Phase 1 complete
    progress_callback(50.0)   # Phase 2 complete
    progress_callback(100.0)  # Done
    return f"processed_{data}"

# Can call without callback (no-op injected)
result = complex_operation("data")

# Or with callback for progress updates
result = complex_operation("data", progress_callback=my_callback)

# In a step, use context.update_step_progress
class MyStep(PipelineStep):
    def run(self, context):
        complex_operation("data", progress_callback=context.update_step_progress)
        return context
```

**Evidence:** `test_decorator_injects_noop_when_callback_not_provided`, `test_decorator_works_with_step_update_method`

## UI Integration

```python
from rich.progress import Progress

with Progress() as rich_progress:
    task = rich_progress.add_task("Pipeline", total=100)

    def update_ui(step_idx, total, name, progress):
        rich_progress.update(task, completed=progress, description=name)

    pipeline = Pipeline(steps, progress_callback=update_ui)
    pipeline.run(context)
```

## Best Practices

1. **Keep callbacks fast** — They run in the main execution path
2. **Don't throw exceptions** — Errors in callbacks may affect execution
3. **Use for monitoring only** — Don't modify state in callbacks
4. **Thread safety** — `get_status()` is safe to call from any thread

## See Also

- [Pipeline API](../api/pipeline.md) — Progress callback parameter
- [Getting Started](getting-started.md) — Basic pipeline setup

