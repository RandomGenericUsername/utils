# Parallel Execution

Parallel execution runs multiple steps concurrently using thread pools.

**Evidence:** `tests/integration/test_execution_flows.py`, `tests/integration/test_advanced_scenarios.py`

## Overview

```
         ┌─ Step A ─┐
Input ───┼─ Step B ─┼─── Merged Output
         └─ Step C ─┘
```

Steps in a parallel group:
1. Run concurrently in separate threads
2. Each receives a **copy** of the input context
3. Results are **merged** after all complete

## Basic Usage

Wrap steps in a list to create a parallel group:

```python
from task_pipeline import Pipeline

# Serial: step1 → step2 → step3
Pipeline([step1, step2, step3])

# Parallel: step1, step2, step3 run concurrently
Pipeline([[step1, step2, step3]])
```

## AND Logic (Default)

All steps must succeed for the group to succeed.

```python
pipeline = Pipeline([[step1, step2, step3]])
# Uses AND logic by default
```

| Scenario | Result |
|----------|--------|
| All succeed | ✅ Group succeeds |
| Any fails | ❌ Group fails |

**Evidence:** `test_parallel_and_all_steps_succeed`, `test_parallel_and_fails_when_one_step_fails`

## OR Logic

At least one step must succeed for the group to succeed.

```python
from task_pipeline import ParallelConfig, LogicOperator

config = ParallelConfig(operator=LogicOperator.OR)
# Apply via ParallelTaskExecutor
```

| Scenario | Result |
|----------|--------|
| All succeed | ✅ Group succeeds |
| At least one succeeds | ✅ Group succeeds |
| All fail | ❌ Group fails |

**Evidence:** `test_parallel_or_succeeds_when_one_step_succeeds`

## Context Isolation

Each parallel step gets its own **deep copy** of the context:

```python
class StepA(PipelineStep):
    def run(self, context):
        context.results["shared_key"] = "from_A"
        return context

class StepB(PipelineStep):
    def run(self, context):
        # Cannot see StepA's changes during execution!
        # context.results["shared_key"] does NOT exist here
        context.results["shared_key"] = "from_B"
        return context
```

After completion, results are merged (later values may overwrite).

**Evidence:** `test_parallel_steps_have_isolated_contexts`

## Parallel Group Timeout

Set a timeout for the entire parallel group:

```python
from task_pipeline import ParallelConfig

config = ParallelConfig(timeout=30.0)  # 30 seconds
```

| Scenario | Behavior |
|----------|----------|
| All steps complete in time | ✅ Success |
| Any step exceeds timeout | ❌ `TimeoutError` raised |

**Evidence:** `test_parallel_group_timeout_enforced`, `test_parallel_group_completes_within_timeout`

> ⚠️ **Note:** This is the **group-level timeout**. Individual step timeouts are NOT enforced. See [Known Limitations](../known-limitations/step-timeout.md).

## Mixed Serial and Parallel

Combine serial and parallel execution:

```python
pipeline = Pipeline([
    step1,              # Serial
    [step2, step3],     # Parallel group
    step4               # Serial
])
```

Execution flow:
```
step1 → (step2 || step3) → step4
```

**Evidence:** `test_serial_then_parallel_then_serial`

## Multiple Parallel Groups

```python
pipeline = Pipeline([
    [step1, step2],     # Parallel group 1
    [step3, step4]      # Parallel group 2
])
```

Execution flow:
```
(step1 || step2) → (step3 || step4)
```

**Evidence:** `test_multiple_parallel_groups_in_sequence`

## Thread Safety

Parallel execution is thread-safe:

- Each step runs in its own thread
- Contexts are isolated (deep copied)
- Results are merged after completion

**Evidence:** `test_parallel_execution_is_thread_safe`

## When to Use Parallel Execution

✅ **Use parallel when:**
- Steps are independent
- Steps access different resources
- You want faster execution

❌ **Use serial when:**
- Steps depend on previous results
- Steps access shared resources
- Order matters

## Progress Tracking in Parallel Steps

Each parallel step can report granular progress independently:

```python
class ParallelStep(PipelineStep):
    def __init__(self, step_id: str, phases: int):
        self._step_id = step_id
        self.phases = phases

    @property
    def step_id(self) -> str:
        return self._step_id

    def run(self, context: PipelineContext) -> PipelineContext:
        for i in range(self.phases):
            # Do work...
            progress = ((i + 1) / self.phases) * 100
            context.update_step_progress(progress)

        context.results[self.step_id] = "done"
        return context

# Parallel steps with different workloads
pipeline = Pipeline([
    [
        ParallelStep("fast", phases=2),
        ParallelStep("slow", phases=10),
    ]
])
```

Each step's progress is weighted based on its share of the overall pipeline.

**Evidence:** `test_parallel_steps_can_report_individual_progress`

## Step Weight Distribution

Weights are distributed based on pipeline structure:

```python
pipeline = Pipeline([
    init_step,              # 33.33% weight
    [worker1, worker2, worker3],  # 33.33% shared (11.11% each)
    finalize_step,          # 33.33% weight
])

status = pipeline.get_status()
# status["step_details"]["init"]["max_weight"] ≈ 33.33
# status["step_details"]["worker1"]["max_weight"] ≈ 11.11
```

**Evidence:** `test_parallel_steps_each_have_weight`

## See Also

- [Context Merging](context-merging.md) — How results are merged
- [Serial Execution](serial-execution.md) — Sequential execution
- [Progress Tracking](progress-tracking.md) — Granular progress reporting
- [ParallelConfig API](../api/parallel-config.md) — Configuration options

