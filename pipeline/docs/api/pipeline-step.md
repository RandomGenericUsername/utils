# PipelineStep Interface

`PipelineStep` is the abstract base class that users must implement to create pipeline steps.

**Source:** `src/task_pipeline/core/types.py`, lines 85-128  
**Evidence:** `tests/contract/test_pipelinestep_interface_contract.py` (17 tests)

## Overview

```python
from abc import ABC, abstractmethod
from task_pipeline import PipelineContext

class PipelineStep(ABC):
    @property
    @abstractmethod
    def step_id(self) -> str: ...
    
    @property
    @abstractmethod
    def description(self) -> str: ...
    
    @abstractmethod
    def run(self, context: PipelineContext) -> PipelineContext: ...
    
    # Optional properties with defaults
    @property
    def timeout(self) -> float | None: return None
    
    @property
    def retries(self) -> int: return 0
    
    @property
    def critical(self) -> bool: return True
```

## Abstract Base Class

`PipelineStep` cannot be instantiated directly. You must create a concrete subclass.

```python
from task_pipeline import PipelineStep

# ❌ This raises TypeError
step = PipelineStep()

# ✅ Create a concrete implementation instead
class MyStep(PipelineStep):
    # ... implement required properties and methods
```

**Evidence:** `test_pipelinestep_cannot_be_instantiated_directly`

## Required Properties

### `step_id: str`

A unique identifier for the step. Used in logging and result storage.

```python
@property
def step_id(self) -> str:
    return "my_unique_step_id"
```

**Evidence:** `test_step_id_returns_string`

### `description: str`

A human-readable description of what the step does.

```python
@property
def description(self) -> str:
    return "Processes user data and stores results"
```

**Evidence:** `test_description_returns_string`

## Required Methods

### `run(context: PipelineContext) -> PipelineContext`

The main execution method. Receives a context, performs work, and returns the (possibly modified) context.

```python
def run(self, context: PipelineContext) -> PipelineContext:
    # Access app config
    config = context.app_config
    
    # Access logger
    context.logger_instance.info(f"Running {self.step_id}")
    
    # Store results
    context.results[self.step_id] = {"processed": True}
    
    # Must return context
    return context
```

**Evidence:** `test_run_accepts_pipeline_context`, `test_run_returns_pipeline_context`

## Optional Properties

These properties have default values but can be overridden.

### `timeout: float | None`

Step execution timeout in seconds. Default: `None` (no timeout).

```python
@property
def timeout(self) -> float | None:
    return 30.0  # 30 second timeout
```

**Evidence:** `test_timeout_default_is_none`, `test_timeout_can_be_overridden`

> ⚠️ **Warning:** This property exists but is **NOT currently enforced**. See [Known Limitations](../known-limitations/step-timeout.md).

### `retries: int`

Number of retry attempts on failure. Default: `0` (no retries).

```python
@property
def retries(self) -> int:
    return 3  # Retry up to 3 times
```

**Evidence:** `test_retries_default_is_zero`, `test_retries_can_be_overridden`

> ⚠️ **Warning:** This property exists but is **NOT currently enforced**. See [Known Limitations](../known-limitations/step-retry.md).

### `critical: bool`

Whether step failure should halt the pipeline. Default: `True`.

```python
@property
def critical(self) -> bool:
    return False  # Non-critical - pipeline continues on failure
```

**Evidence:** `test_critical_default_is_true`, `test_critical_can_be_overridden`

## Complete Example

```python
from typing import Any
from task_pipeline import PipelineContext, PipelineStep

class DataProcessingStep(PipelineStep):
    def __init__(self, source: str):
        self._source = source
    
    @property
    def step_id(self) -> str:
        return f"process_{self._source}"
    
    @property
    def description(self) -> str:
        return f"Processes data from {self._source}"
    
    @property
    def critical(self) -> bool:
        return True  # Pipeline stops if this fails
    
    def run(self, context: PipelineContext) -> PipelineContext:
        context.logger_instance.info(f"Processing {self._source}...")
        context.results[self.step_id] = {"source": self._source, "status": "complete"}
        return context
```

**Evidence:** `test_complete_implementation_can_be_instantiated`, `test_complete_implementation_is_functional`

