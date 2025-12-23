# Task Pipeline

A Python library for building and executing task pipelines with serial and parallel execution support.

## Installation

```bash
pip install task-pipeline
```

## Quick Start

```python
from task_pipeline import Pipeline, PipelineContext, PipelineStep

# 1. Define your steps by implementing PipelineStep
class GreetStep(PipelineStep):
    @property
    def step_id(self) -> str:
        return "greet"
    
    @property
    def description(self) -> str:
        return "Greets the user"
    
    def run(self, context: PipelineContext) -> PipelineContext:
        context.results["greeting"] = "Hello, World!"
        return context

class FarewellStep(PipelineStep):
    @property
    def step_id(self) -> str:
        return "farewell"
    
    @property
    def description(self) -> str:
        return "Says goodbye"
    
    def run(self, context: PipelineContext) -> PipelineContext:
        context.results["farewell"] = "Goodbye!"
        return context

# 2. Create and run the pipeline
pipeline = Pipeline([GreetStep(), FarewellStep()])
context = PipelineContext(app_config=my_config, logger_instance=my_logger)
result = pipeline.run(context)

print(result.results)  # {'greeting': 'Hello, World!', 'farewell': 'Goodbye!'}
```

**Evidence:** `tests/contract/test_pipeline_api_contract.py::test_pipeline_accepts_single_step`

## Core Concepts

| Concept | Description | Documentation |
|---------|-------------|---------------|
| **Pipeline** | Orchestrates step execution | [API Reference](api/pipeline.md) |
| **PipelineStep** | Abstract interface users implement | [API Reference](api/pipeline-step.md) |
| **PipelineContext** | Carries data between steps | [API Reference](api/pipeline-context.md) |
| **PipelineConfig** | Pipeline-level configuration | [API Reference](api/pipeline-config.md) |
| **ParallelConfig** | Parallel group configuration | [API Reference](api/parallel-config.md) |

## Features

- ✅ **Serial Execution** — Steps run in order ([Guide](guides/serial-execution.md))
- ✅ **Parallel Execution** — Run steps concurrently with AND/OR logic ([Guide](guides/parallel-execution.md))
- ✅ **Error Handling** — Fail-fast or fail-slow modes ([Guide](guides/error-handling.md))
- ✅ **Progress Tracking** — Callbacks for progress monitoring ([Guide](guides/progress-tracking.md))
- ✅ **Context Merging** — Automatic result merging from parallel steps ([Guide](guides/context-merging.md))

## Known Limitations

- ⚠️ **Step Timeout** — Property exists but is NOT enforced ([Details](known-limitations/step-timeout.md))
- ⚠️ **Step Retry** — Property exists but is NOT enforced ([Details](known-limitations/step-retry.md))

## Documentation Index

### API Reference
- [Pipeline](api/pipeline.md) — Main pipeline class
- [PipelineStep](api/pipeline-step.md) — Step interface to implement
- [PipelineContext](api/pipeline-context.md) — Context data structure
- [PipelineConfig](api/pipeline-config.md) — Pipeline configuration
- [ParallelConfig](api/parallel-config.md) — Parallel execution configuration

### Guides
- [Getting Started](guides/getting-started.md) — First pipeline tutorial
- [Serial Execution](guides/serial-execution.md) — Running steps in sequence
- [Parallel Execution](guides/parallel-execution.md) — Running steps concurrently
- [Error Handling](guides/error-handling.md) — Handling failures
- [Progress Tracking](guides/progress-tracking.md) — Monitoring execution
- [Context Merging](guides/context-merging.md) — Merging parallel results

### Reference
- [Test Coverage Matrix](reference/test-coverage-matrix.md) — Maps documentation to tests

---

## Documentation Methodology

This documentation follows the **Tests-First Documentation** approach:

> "Documentation must be grounded in verified behavior. Tests are the primary source of truth."

Every documented behavior references specific tests as evidence. See [Test Coverage Matrix](reference/test-coverage-matrix.md) for the complete mapping.

