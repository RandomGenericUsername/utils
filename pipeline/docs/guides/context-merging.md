# Context Merging

When parallel steps complete, their results are merged back into a single context.

**Evidence:** `tests/integration/test_context_merging.py` (3 tests)

## Overview

```
         ┌─ Step A: results["items"] = [1, 2] ─┐
Input ───┼─ Step B: results["items"] = [3, 4] ─┼─── Merged: results["items"] = [1, 2, 3, 4]
         └─ Step C: results["items"] = [5, 6] ─┘
```

The merging strategy depends on the **type** of the values.

## Merge Strategies by Type

### Lists — Concatenation

Lists from parallel steps are concatenated:

```python
class StepA(PipelineStep):
    def run(self, context):
        context.results["items"] = ["a", "b"]
        return context

class StepB(PipelineStep):
    def run(self, context):
        context.results["items"] = ["c", "d"]
        return context

# After parallel execution:
# context.results["items"] = ["a", "b", "c", "d"]
```

**Evidence:** `test_parallel_steps_merge_lists`

### Numbers — Summation

Numeric values (int, float) are summed:

```python
class StepA(PipelineStep):
    def run(self, context):
        context.results["count"] = 10
        return context

class StepB(PipelineStep):
    def run(self, context):
        context.results["count"] = 25
        return context

# After parallel execution:
# context.results["count"] = 35
```

**Evidence:** `test_parallel_steps_sum_numeric_increments`

### Dictionaries — Shallow Merge

Dictionaries are merged using shallow `dict.update()`:

```python
class StepA(PipelineStep):
    def run(self, context):
        context.results["config"] = {"key1": "value1"}
        return context

class StepB(PipelineStep):
    def run(self, context):
        context.results["config"] = {"key2": "value2"}
        return context

# After parallel execution:
# context.results["config"] = {"key1": "value1", "key2": "value2"}
```

**Evidence:** `test_parallel_steps_merge_dicts_shallowly`

> ⚠️ **Warning:** This is a **shallow merge**. Nested dictionaries are NOT recursively merged. Later values overwrite earlier ones.

### Other Types — Last Value Wins

For other types, the last completed step's value is used:

```python
class StepA(PipelineStep):
    def run(self, context):
        context.results["status"] = "from_a"
        return context

class StepB(PipelineStep):
    def run(self, context):
        context.results["status"] = "from_b"
        return context

# After parallel execution:
# context.results["status"] = "from_a" or "from_b" (non-deterministic!)
```

## Merge Behavior Summary

| Type | Strategy | Example |
|------|----------|---------|
| `list` | Concatenate | `[1,2] + [3,4] = [1,2,3,4]` |
| `int`, `float` | Sum | `10 + 25 = 35` |
| `dict` | Shallow update | `{a:1}` + `{b:2}` = `{a:1, b:2}` |
| Other | Last value wins | Non-deterministic |

## Best Practices

### Use Unique Keys

The safest approach is using unique keys per step:

```python
class StepA(PipelineStep):
    def run(self, context):
        context.results["step_a_result"] = {...}  # Unique key
        return context

class StepB(PipelineStep):
    def run(self, context):
        context.results["step_b_result"] = {...}  # Unique key
        return context
```

### Use Appropriate Types

Choose types that match your merge needs:

```python
# ✅ Use lists when you want all values
context.results["all_items"] = [item]

# ✅ Use numbers for counters/totals
context.results["total_processed"] = count

# ⚠️ Be careful with dicts (shallow merge)
context.results["config"] = {"nested": {...}}  # Nested won't merge!
```

### Avoid Conflicts

If multiple steps write to the same non-mergeable key:

```python
# ❌ Problematic - non-deterministic result
Step A: context.results["status"] = "done_a"
Step B: context.results["status"] = "done_b"

# ✅ Better - use unique keys
Step A: context.results["step_a_status"] = "done"
Step B: context.results["step_b_status"] = "done"
```

## Implementation Details

**Source:** `src/task_pipeline/executors/parallel_executor.py`, lines 131-235

The merging logic is implemented in `ParallelTaskExecutor._merge_contexts()`:

1. Creates a copy of the base context
2. Iterates through result contexts
3. Applies type-specific merge for each key

## See Also

- [Parallel Execution](parallel-execution.md) — Parallel execution guide
- [PipelineContext API](../api/pipeline-context.md) — Context data structure

