# Error Handling

This guide covers how pipelines handle step failures.

**Evidence:** `tests/integration/test_error_handling.py` (6 tests)

## Overview

Two configuration options control error behavior:

| Option | Purpose |
|--------|---------|
| `PipelineConfig.fail_fast` | Pipeline-level error mode |
| `PipelineStep.critical` | Step-level importance |

## Fail-Fast Mode (Default)

With `fail_fast=True` (default), the pipeline stops immediately when a critical step fails.

```python
from task_pipeline import Pipeline, PipelineConfig

pipeline = Pipeline(
    steps=[step1, step2, step3],
    config=PipelineConfig(fail_fast=True)  # Default
)
```

### Behavior

```
Step 1: ✅ Success
Step 2: ❌ Critical Error → Pipeline STOPS, raises RuntimeError
Step 3: ⏭️ Never executed
```

**Evidence:** `test_fail_fast_stops_on_first_critical_error`

### Non-Critical Steps in Fail-Fast

Non-critical steps (`critical=False`) don't stop the pipeline:

```python
class OptionalStep(PipelineStep):
    @property
    def critical(self) -> bool:
        return False  # Non-critical

    def run(self, context):
        raise ValueError("This won't stop the pipeline")
```

```
Step 1: ✅ Success
OptionalStep: ❌ Error (logged, continues)
Step 3: ✅ Runs normally
```

**Evidence:** `test_fail_fast_continues_on_non_critical_error`

## Fail-Slow Mode

With `fail_fast=False`, the pipeline continues execution and accumulates all errors.

```python
pipeline = Pipeline(
    steps=[step1, step2, step3],
    config=PipelineConfig(fail_fast=False)
)
```

### Behavior

```
Step 1: ✅ Success
Step 2: ❌ Error → Recorded in context.errors, continues
Step 3: ✅ Success
Final: All errors available in context.errors
```

**Evidence:** `test_fail_slow_accumulates_all_errors`

### Accessing Errors

```python
result = pipeline.run(context)

if result.errors:
    for error in result.errors:
        print(f"Error: {error}")
```

### Critical Steps in Fail-Slow

Even critical steps don't stop the pipeline in fail-slow mode:

```python
pipeline = Pipeline(
    steps=[critical_step, another_critical_step],
    config=PipelineConfig(fail_fast=False)
)

result = pipeline.run(context)
# Both steps attempted, all errors collected
```

**Evidence:** `test_fail_slow_continues_even_on_critical_error`

> ⚠️ **Note:** This is the current behavior. In fail-slow mode, ALL errors are accumulated, even from critical steps.

## Step Criticality

The `critical` property controls individual step importance:

```python
class CriticalStep(PipelineStep):
    @property
    def critical(self) -> bool:
        return True  # Default - stops pipeline on failure (in fail-fast)

class OptionalStep(PipelineStep):
    @property
    def critical(self) -> bool:
        return False  # Pipeline continues on failure
```

## Behavior Matrix

| `fail_fast` | `step.critical` | On Error |
|-------------|-----------------|----------|
| `True` | `True` | Raises `RuntimeError`, stops pipeline |
| `True` | `False` | Logs error, continues to next step |
| `False` | `True` | Records error, continues execution |
| `False` | `False` | Records error, continues execution |

## Multiple Failures

### In Fail-Slow Mode

```python
pipeline = Pipeline(
    steps=[failing1, failing2, failing3],
    config=PipelineConfig(fail_fast=False)
)

result = pipeline.run(context)
assert len(result.errors) == 3  # All errors collected
```

**Evidence:** `test_multiple_non_critical_failures_all_recorded`

### Successful Steps After Failures

In fail-slow mode, successful steps still run and their results are preserved:

```python
pipeline = Pipeline(
    steps=[failing_step, success_step],
    config=PipelineConfig(fail_fast=False)
)

result = pipeline.run(context)
assert "success_step" in result.results  # Result preserved
assert len(result.errors) == 1  # Error from failing_step
```

**Evidence:** `test_successful_steps_after_non_critical_failures`

## Best Practices

1. **Use fail-fast** for critical workflows where partial completion is harmful
2. **Use fail-slow** for batch processing where you want maximum throughput
3. **Mark optional steps** as `critical=False` to prevent unnecessary failures
4. **Always check `context.errors`** when using fail-slow mode

## See Also

- [PipelineConfig API](../api/pipeline-config.md) — Configuration options
- [PipelineStep API](../api/pipeline-step.md) — Step interface

