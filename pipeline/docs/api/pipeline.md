# Pipeline Class

`Pipeline` is the main class for orchestrating step execution.

**Source:** `src/task_pipeline/pipeline.py`, lines 17-225  
**Evidence:** `tests/contract/test_pipeline_api_contract.py` (17 tests)

## Overview

```python
from task_pipeline import Pipeline, PipelineConfig, PipelineContext

# Create a pipeline
pipeline = Pipeline(
    steps=[step1, step2, step3],
    config=PipelineConfig(fail_fast=True),
    progress_callback=my_callback
)

# Run the pipeline
result = pipeline.run(context)
```

## Constructor

```python
def __init__(
    self,
    steps: list[TaskStep],
    config: PipelineConfig | None = None,
    progress_callback: Callable[[int, int, str, float], None] | None = None
)
```

### Parameters

#### `steps: list[TaskStep]`

List of steps or parallel step groups to execute.

| Input | Behavior | Evidence |
|-------|----------|----------|
| Empty list `[]` | Valid, returns unmodified context | `test_pipeline_accepts_empty_steps_list` |
| Single step `[step]` | Executes single step | `test_pipeline_accepts_single_step` |
| Multiple steps `[s1, s2]` | Executes in order | `test_pipeline_accepts_multiple_serial_steps` |
| Parallel group `[[s1, s2]]` | Executes concurrently | `test_pipeline_accepts_parallel_step_group` |
| Mixed `[s1, [s2, s3], s4]` | Serial → Parallel → Serial | `test_pipeline_accepts_mixed_serial_and_parallel_steps` |

#### `config: PipelineConfig | None`

Pipeline configuration. If `None`, uses default `PipelineConfig()`.

```python
# These are equivalent
Pipeline(steps)
Pipeline(steps, config=None)
Pipeline(steps, config=PipelineConfig())
```

**Evidence:** `test_pipeline_accepts_none_config_uses_defaults`, `test_pipeline_accepts_custom_config`

#### `progress_callback: Callable[[int, int, str, float], None] | None`

Optional callback for progress tracking.

**Signature:** `(step_index: int, total_steps: int, step_name: str, progress: float) -> None`

```python
def my_callback(step_idx: int, total: int, name: str, progress: float) -> None:
    print(f"Step {step_idx}/{total}: {name} - {progress:.1f}%")

pipeline = Pipeline(steps, progress_callback=my_callback)
```

**Evidence:** `test_pipeline_accepts_progress_callback_function`, `test_pipeline_accepts_none_progress_callback`

## Methods

### `run(context: PipelineContext) -> PipelineContext`

Executes the pipeline with the given context.

```python
def run(self, context: PipelineContext[AppConfig]) -> PipelineContext[AppConfig]
```

| Aspect | Behavior | Evidence |
|--------|----------|----------|
| Accepts `PipelineContext` | ✅ | `test_run_accepts_pipeline_context` |
| Returns `PipelineContext` | ✅ | `test_run_returns_pipeline_context` |
| Modifies `context.results` | ✅ | `test_run_returns_modified_context_with_results` |
| Preserves original fields | ✅ | `test_run_preserves_original_context_fields` |

**Example:**

```python
from task_pipeline import Pipeline, PipelineContext

context = PipelineContext(app_config=config, logger_instance=logger)
result = pipeline.run(context)

# Access results
print(result.results)  # {'step1': ..., 'step2': ...}
```

### `create(steps, config) -> Pipeline` (Factory Method)

Alternative factory method for creating pipelines.

```python
@classmethod
def create(
    cls,
    steps: list[TaskStep],
    config: PipelineConfig | None = None
) -> Pipeline
```

**Example:**

```python
pipeline = Pipeline.create([step1, step2], PipelineConfig(fail_fast=False))
```

**Evidence:** `test_create_factory_method_exists`, `test_create_accepts_steps_and_config`, `test_create_returns_pipeline_instance`, `test_create_pipeline_is_functional`

## Properties

### `config: PipelineConfig`

Returns the pipeline configuration.

```python
pipeline = Pipeline(steps, config=PipelineConfig(fail_fast=False))
print(pipeline.config.fail_fast)  # False
```

## Usage Patterns

### Serial Execution

```python
pipeline = Pipeline([step1, step2, step3])
result = pipeline.run(context)
# Executes: step1 → step2 → step3
```

### Parallel Execution

```python
from task_pipeline import ParallelConfig, LogicOperator

parallel_group = [step1, step2, step3]  # List = parallel
pipeline = Pipeline([parallel_group])
result = pipeline.run(context)
# Executes: step1, step2, step3 concurrently
```

### Mixed Execution

```python
pipeline = Pipeline([
    step1,              # Serial
    [step2, step3],     # Parallel group
    step4               # Serial
])
# Executes: step1 → (step2 || step3) → step4
```

## See Also

- [PipelineStep](pipeline-step.md) — Interface to implement
- [PipelineConfig](pipeline-config.md) — Configuration options
- [PipelineContext](pipeline-context.md) — Context data structure
- [ParallelConfig](parallel-config.md) — Parallel execution options

