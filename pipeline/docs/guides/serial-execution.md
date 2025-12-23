# Serial Execution

Serial execution runs steps one after another, in order.

**Evidence:** `tests/integration/test_execution_flows.py::TestSerialExecution` (3 tests)

## Overview

```
Step 1 → Step 2 → Step 3
```

Each step:
1. Receives the context from the previous step
2. Performs its work
3. Passes the (possibly modified) context to the next step

## Basic Usage

```python
from task_pipeline import Pipeline, PipelineContext

pipeline = Pipeline([
    step1,  # Runs first
    step2,  # Runs second (after step1 completes)
    step3   # Runs third (after step2 completes)
])

result = pipeline.run(context)
```

**Evidence:** `test_serial_execution_runs_steps_in_order`

## Context Flow

Context modifications flow from step to step:

```python
class Step1(PipelineStep):
    def run(self, context):
        context.results["step1"] = "value1"
        return context

class Step2(PipelineStep):
    def run(self, context):
        # Can read Step1's result
        step1_result = context.results["step1"]  # "value1"
        context.results["step2"] = f"received: {step1_result}"
        return context
```

**Evidence:** `test_serial_execution_context_flows_between_steps`

## Empty Pipeline

An empty pipeline returns the context unmodified:

```python
pipeline = Pipeline([])  # No steps
result = pipeline.run(context)

assert result.results == context.results  # Unchanged
```

**Evidence:** `test_empty_pipeline_returns_unmodified_context`

## Execution Order Guarantee

Steps are executed in the exact order they appear in the list:

```python
execution_order = []

class OrderTrackingStep(PipelineStep):
    def __init__(self, name):
        self._name = name
    
    @property
    def step_id(self) -> str:
        return self._name
    
    @property
    def description(self) -> str:
        return f"Step {self._name}"
    
    def run(self, context):
        execution_order.append(self._name)
        return context

pipeline = Pipeline([
    OrderTrackingStep("A"),
    OrderTrackingStep("B"),
    OrderTrackingStep("C")
])

pipeline.run(context)

assert execution_order == ["A", "B", "C"]
```

## Error Handling in Serial Execution

When a step fails in serial execution:

### Fail-Fast Mode (Default)

```python
from task_pipeline import Pipeline, PipelineConfig

pipeline = Pipeline(
    steps=[step1, failing_step, step3],
    config=PipelineConfig(fail_fast=True)  # Default
)

# step1 runs ✅
# failing_step raises error ❌
# step3 never runs ⏭️
```

### Fail-Slow Mode

```python
pipeline = Pipeline(
    steps=[step1, failing_step, step3],
    config=PipelineConfig(fail_fast=False)
)

# step1 runs ✅
# failing_step fails, error recorded ❌
# step3 still runs ✅
# Errors available in result.errors
```

See [Error Handling Guide](error-handling.md) for details.

## When to Use Serial Execution

✅ **Use serial execution when:**
- Steps have dependencies on previous steps' results
- Order of operations matters
- Steps modify shared resources that need sequential access

❌ **Consider parallel execution when:**
- Steps are independent of each other
- You want to reduce total execution time
- Steps access different resources

## See Also

- [Parallel Execution](parallel-execution.md) — Run steps concurrently
- [Error Handling](error-handling.md) — Handle step failures
- [Pipeline API](../api/pipeline.md) — Full API reference

