# PipelineConfig

`PipelineConfig` controls pipeline-level behavior such as error handling mode.

**Source:** `src/task_pipeline/core/types.py`  
**Evidence:** `tests/contract/test_pipeline_api_contract.py`, `tests/integration/test_error_handling.py`

## Overview

```python
from dataclasses import dataclass

@dataclass
class PipelineConfig:
    fail_fast: bool = True
```

## Properties

### `fail_fast: bool`

Controls how the pipeline handles errors.

| Value | Behavior | Evidence |
|-------|----------|----------|
| `True` (default) | Stops on first critical error | `tests/integration/test_error_handling.py::test_fail_fast_stops_on_first_critical_error` |
| `False` | Accumulates all errors, continues execution | `tests/integration/test_error_handling.py::test_fail_slow_accumulates_all_errors` |

## Usage

### Default Configuration (Fail-Fast)

```python
from task_pipeline import Pipeline, PipelineConfig

# These are equivalent
pipeline = Pipeline(steps)
pipeline = Pipeline(steps, config=None)
pipeline = Pipeline(steps, config=PipelineConfig())
pipeline = Pipeline(steps, config=PipelineConfig(fail_fast=True))
```

**Behavior:** Pipeline stops immediately when a critical step fails.

**Evidence:** `test_pipeline_accepts_none_config_uses_defaults`

### Fail-Slow Mode

```python
from task_pipeline import Pipeline, PipelineConfig

pipeline = Pipeline(
    steps=[step1, step2, step3],
    config=PipelineConfig(fail_fast=False)
)
result = pipeline.run(context)

# Check for accumulated errors
if result.errors:
    for error in result.errors:
        print(f"Error: {error}")
```

**Behavior:** Pipeline continues executing all steps, collecting errors in `context.errors`.

**Evidence:** `test_fail_slow_accumulates_all_errors`

## Error Handling Behavior

### With `fail_fast=True` (Default)

```
Step 1: ✅ Success
Step 2: ❌ Critical Error → Pipeline STOPS, raises RuntimeError
Step 3: ⏭️ Never executed
```

### With `fail_fast=False`

```
Step 1: ✅ Success
Step 2: ❌ Critical Error → Recorded in context.errors, continues
Step 3: ✅ Success
Final: All errors available in context.errors
```

## Interaction with Step Criticality

| `fail_fast` | `step.critical` | Behavior |
|-------------|-----------------|----------|
| `True` | `True` | Raises RuntimeError immediately |
| `True` | `False` | Logs error, continues to next step |
| `False` | `True` | Records error, continues execution |
| `False` | `False` | Records error, continues execution |

**Evidence:** `test_fail_fast_continues_on_non_critical_error`, `test_fail_slow_continues_even_on_critical_error`

## See Also

- [Pipeline](pipeline.md) — Main pipeline class
- [Error Handling Guide](../guides/error-handling.md) — Detailed error handling patterns

