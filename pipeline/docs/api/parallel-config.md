# ParallelConfig

`ParallelConfig` controls behavior of parallel step groups.

**Source:** `src/task_pipeline/core/types.py`, lines 130-141  
**Evidence:** `tests/integration/test_execution_flows.py`, `tests/integration/test_advanced_scenarios.py`

## Overview

```python
from dataclasses import dataclass
from task_pipeline import LogicOperator

@dataclass
class ParallelConfig:
    operator: LogicOperator = LogicOperator.AND
    max_workers: int | None = None
    timeout: float | None = None
    show_task_identifiers: bool = True
    use_visual_separators: bool = False
```

## Properties

### `operator: LogicOperator`

Determines success criteria for the parallel group.

| Value | Behavior | Evidence |
|-------|----------|----------|
| `LogicOperator.AND` (default) | All steps must succeed | `test_parallel_and_all_steps_succeed` |
| `LogicOperator.OR` | At least one step must succeed | `test_parallel_or_succeeds_when_one_step_succeeds` |

```python
from task_pipeline import ParallelConfig, LogicOperator

# AND logic - all must succeed
config = ParallelConfig(operator=LogicOperator.AND)

# OR logic - at least one must succeed
config = ParallelConfig(operator=LogicOperator.OR)
```

### `max_workers: int | None`

Maximum number of concurrent workers. `None` means use default (typically CPU count).

```python
# Limit to 4 concurrent workers
config = ParallelConfig(max_workers=4)
```

**Evidence:** `tests/test_parallel_executor.py::test_execute_with_max_workers_limit`

### `timeout: float | None`

Timeout in seconds for the entire parallel group. `None` means no timeout.

```python
# 30 second timeout for the entire group
config = ParallelConfig(timeout=30.0)
```

| Scenario | Behavior | Evidence |
|----------|----------|----------|
| Steps complete within timeout | ✅ Success | `test_parallel_group_completes_within_timeout` |
| Steps exceed timeout | ❌ TimeoutError raised | `test_parallel_group_timeout_enforced` |

> **Note:** This is the **group-level timeout**, which IS enforced. Individual step timeouts are NOT enforced. See [Known Limitations](../known-limitations/step-timeout.md).

### `show_task_identifiers: bool`

Whether to show task identifiers in logging output. Default: `True`.

### `use_visual_separators: bool`

Whether to use visual separators in logging output. Default: `False`.

## Usage

### Basic Parallel Group

```python
from task_pipeline import Pipeline, ParallelConfig, LogicOperator

# Create parallel group with AND logic
parallel_steps = [step1, step2, step3]
pipeline = Pipeline([parallel_steps])  # Uses default AND logic
```

### Parallel Group with OR Logic

```python
from task_pipeline import Pipeline, ParallelConfig, LogicOperator

# At least one step must succeed
parallel_config = ParallelConfig(operator=LogicOperator.OR)
# Note: ParallelConfig is applied via ParallelTaskExecutor, not directly in Pipeline
```

### Parallel Group with Timeout

```python
from task_pipeline import ParallelConfig

config = ParallelConfig(timeout=10.0)  # 10 second timeout
```

## LogicOperator Enum

```python
from enum import Enum

class LogicOperator(Enum):
    AND = "and"  # All steps must succeed
    OR = "or"    # At least one step must succeed
```

**Source:** `src/task_pipeline/core/types.py`, lines 78-83

### AND Logic Behavior

```
Step 1: ✅ Success
Step 2: ✅ Success  → Group: ✅ SUCCESS
Step 3: ✅ Success
```

```
Step 1: ✅ Success
Step 2: ❌ Failure  → Group: ❌ FAILURE
Step 3: ✅ Success
```

**Evidence:** `test_parallel_and_all_steps_succeed`, `test_parallel_and_fails_when_one_step_fails`

### OR Logic Behavior

```
Step 1: ❌ Failure
Step 2: ✅ Success  → Group: ✅ SUCCESS
Step 3: ❌ Failure
```

```
Step 1: ❌ Failure
Step 2: ❌ Failure  → Group: ❌ FAILURE
Step 3: ❌ Failure
```

**Evidence:** `test_parallel_or_succeeds_when_one_step_succeeds`, `test_parallel_or_succeeds_when_all_steps_succeed`

## See Also

- [Parallel Execution Guide](../guides/parallel-execution.md) — Detailed parallel patterns
- [Context Merging Guide](../guides/context-merging.md) — How results are merged
- [Pipeline](pipeline.md) — Main pipeline class

