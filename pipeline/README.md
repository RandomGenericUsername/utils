# Dotfiles Pipeline

Flexible pipeline execution framework with support for serial and parallel task execution, featuring comprehensive granular progress tracking.

## Features

- **Serial and Parallel Execution**: Execute tasks sequentially or concurrently
- **Granular Progress Tracking**: Real-time progress updates with automatic weight calculation
- **Type-Safe Context**: Strongly-typed pipeline context with generic app config support
- **Thread-Safe**: Safe for concurrent operations during parallel execution
- **Progress Callbacks**: Optional callbacks for progress monitoring
- **Auto-Completion**: Steps automatically complete to 100% even without explicit progress updates
- **Decorator Support**: `@with_progress_callback` for utility functions
- **Clean Architecture**: Separation of concerns with reusable components

## Installation

This module is part of the dotfiles monorepo and uses UV for dependency management.

## Quick Start

### Basic Pipeline

```python
from task_pipeline import Pipeline, PipelineStep, PipelineContext

# Define your steps
class MyStep(PipelineStep):
    @property
    def step_id(self) -> str:
        return "my_step"

    @property
    def description(self) -> str:
        return "My custom step"

    def run(self, context: PipelineContext) -> PipelineContext:
        # Your logic here
        context.results["output"] = "done"
        return context

# Create and run pipeline
pipeline = Pipeline([MyStep()])
result = pipeline.run(context)
```

### With Granular Progress

```python
class DataProcessingStep(PipelineStep):
    @property
    def step_id(self) -> str:
        return "process_data"

    @property
    def description(self) -> str:
        return "Process data with progress tracking"

    def run(self, context: PipelineContext) -> PipelineContext:
        items = range(100)

        for i, item in enumerate(items):
            process(item)

            # Report progress (0-100% of this step)
            progress = ((i + 1) / len(items)) * 100
            context.update_step_progress(progress)

        return context

# Monitor progress
def on_progress(step_idx, total, name, progress):
    print(f"Overall: {progress:.1f}%")

pipeline = Pipeline([DataProcessingStep()], progress_callback=on_progress)
result = pipeline.run(context)
```

### Parallel Execution

```python
steps = [
    InitStep(),
    [Worker1(), Worker2(), Worker3()],  # Run in parallel
    FinalizeStep()
]

pipeline = Pipeline(steps)
result = pipeline.run(context)
```

## Documentation

- **[Granular Progress Tracking](docs/GRANULAR_PROGRESS.md)** - Comprehensive guide to progress tracking
- **[Examples](examples/)** - Working examples demonstrating various features

## Examples

Run the included examples to see the pipeline in action:

```bash
# Basic granular progress
uv run python examples/demo_granular_progress.py

# Real-time progress monitoring
uv run python examples/demo_realtime_progress.py

# Parallel execution with progress
uv run python examples/demo_parallel_progress.py
```

## Testing

Run the test suite:

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=pipeline --cov-report=html

# Run specific test file
uv run pytest tests/test_progress_tracker.py -v
```

## Dependencies

- `dotfiles-logging` - Logging infrastructure (RichLogger used in PipelineContext)
