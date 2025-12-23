# PipelineContext

`PipelineContext` is the data structure that carries state between pipeline steps.

**Source:** `src/task_pipeline/core/types.py`, lines 14-76  
**Evidence:** `tests/test_pipeline_context.py` (18 tests)

## Overview

```python
from dataclasses import dataclass, field
from typing import Generic, TypeVar

AppConfig = TypeVar("AppConfig")

@dataclass
class PipelineContext(Generic[AppConfig]):
    app_config: AppConfig
    logger_instance: Any
    results: dict[str, Any] = field(default_factory=dict)
    errors: list[Exception] = field(default_factory=list)
    # ... additional fields
```

## Type Parameter

`PipelineContext` is generic over your application's configuration type:

```python
from dataclasses import dataclass
from task_pipeline import PipelineContext

@dataclass
class MyAppConfig:
    name: str
    version: str
    debug: bool = False

# Create typed context
context: PipelineContext[MyAppConfig] = PipelineContext(
    app_config=MyAppConfig(name="my_app", version="1.0.0"),
    logger_instance=logger
)

# Type-safe access to app_config
print(context.app_config.name)  # IDE provides autocomplete
```

## Required Fields

### `app_config: AppConfig`

Your application's configuration object. Can be any type.

```python
context = PipelineContext(
    app_config={"setting": "value"},  # dict
    logger_instance=logger
)

context = PipelineContext(
    app_config=MyConfig(),  # dataclass
    logger_instance=logger
)
```

**Evidence:** `test_context_creation_with_app_config`

### `logger_instance`

Logger instance for step logging. Expected to have `info()`, `error()`, `warning()` methods.

```python
import logging

logger = logging.getLogger(__name__)
context = PipelineContext(
    app_config=config,
    logger_instance=logger
)
```

**Evidence:** `test_context_creation_with_logger`

## Default Fields

### `results: dict[str, Any]`

Dictionary for storing step results. Initialized as empty dict.

```python
context = PipelineContext(app_config=config, logger_instance=logger)
print(context.results)  # {}

# Steps store results here
context.results["my_step"] = {"processed": 100}
```

**Evidence:** `test_context_results_dict_default`

### `errors: list[Exception]`

List of accumulated errors. Used in fail-slow mode.

```python
if context.errors:
    for error in context.errors:
        print(f"Error occurred: {error}")
```

## Usage in Steps

```python
from task_pipeline import PipelineContext, PipelineStep

class MyStep(PipelineStep):
    @property
    def step_id(self) -> str:
        return "my_step"
    
    @property
    def description(self) -> str:
        return "Example step"
    
    def run(self, context: PipelineContext) -> PipelineContext:
        # Access application config
        config = context.app_config
        
        # Use logger
        context.logger_instance.info(f"Processing with {config}")
        
        # Read results from previous steps
        previous_result = context.results.get("previous_step")
        
        # Store this step's results
        context.results[self.step_id] = {
            "status": "complete",
            "data": processed_data
        }
        
        # Must return context
        return context
```

## Context in Parallel Execution

When steps run in parallel:

1. Each step receives a **deep copy** of the context
2. Steps cannot see each other's modifications during execution
3. After completion, results are **merged** back

```python
# Parallel step 1 sees: context.results = {"serial_step": "done"}
# Parallel step 2 sees: context.results = {"serial_step": "done"}
# After parallel group: context.results = {
#     "serial_step": "done",
#     "parallel_1": "result1",
#     "parallel_2": "result2"
# }
```

**Evidence:** `tests/integration/test_advanced_scenarios.py::test_parallel_steps_have_isolated_contexts`

## See Also

- [PipelineStep](pipeline-step.md) — How to use context in steps
- [Context Merging Guide](../guides/context-merging.md) — How parallel results merge

