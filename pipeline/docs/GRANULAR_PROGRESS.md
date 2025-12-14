# Granular Progress Tracking

The pipeline module provides a comprehensive granular progress tracking system that allows steps to report their internal progress in real-time.

## Overview

The progress tracking system consists of three main components:

1. **ProgressTracker** - Thread-safe progress tracking with automatic weight calculation
2. **PipelineContext.update_step_progress()** - Method for steps to report progress
3. **@with_progress_callback** - Decorator for utility functions to support optional progress reporting

## Key Features

- **Equal Weight Distribution**: Each step gets equal maximum percentage (e.g., 20% for 5 steps)
- **Granular Updates**: Steps can report internal progress (0-100%) which is scaled by their weight
- **Auto-Completion**: Steps that never call `update_step_progress()` auto-complete to 100% when finished
- **Thread-Safe**: Safe for concurrent updates during parallel execution
- **Parallel Support**: Parallel groups divide their weight equally among sub-steps
- **Real-Time Querying**: Progress can be queried at any time via `pipeline.get_status()`

## Basic Usage

### Simple Step with Progress Updates

```python
from task_pipeline import Pipeline, PipelineStep, PipelineContext

class DataProcessingStep(PipelineStep):
    @property
    def step_id(self) -> str:
        return "data_processing"

    @property
    def description(self) -> str:
        return "Process data items"

    def run(self, context: PipelineContext) -> PipelineContext:
        items = ["item1", "item2", "item3", "item4", "item5"]

        for i, item in enumerate(items):
            # Do work
            process_item(item)

            # Report progress (0-100% of THIS step)
            progress = ((i + 1) / len(items)) * 100
            context.update_step_progress(progress)

        return context
```

### Step Without Progress Updates (Auto-Completion)

```python
class SimpleStep(PipelineStep):
    @property
    def step_id(self) -> str:
        return "simple"

    @property
    def description(self) -> str:
        return "Simple step"

    def run(self, context: PipelineContext) -> PipelineContext:
        # Do work but never call update_step_progress
        do_work()

        # This step will auto-complete to 100% when finished
        return context
```

## Using the Decorator for Utility Functions

When your steps delegate to utility functions, use the `@with_progress_callback` decorator:

```python
from task_pipeline import with_progress_callback

@with_progress_callback
def generate_color_scheme(wallpaper_path: str, progress_callback):
    """Generate color scheme with progress reporting."""

    # Phase 1: Load wallpaper
    load_wallpaper(wallpaper_path)
    progress_callback(25.0)

    # Phase 2: Extract colors
    extract_colors()
    progress_callback(50.0)

    # Phase 3: Generate scheme
    generate_scheme()
    progress_callback(75.0)

    # Phase 4: Save
    save_scheme()
    progress_callback(100.0)

    return scheme


class GenerateColorSchemeStep(PipelineStep):
    def run(self, context: PipelineContext) -> PipelineContext:
        # Pass context's progress method as callback
        scheme = generate_color_scheme(
            wallpaper_path,
            progress_callback=context.update_step_progress
        )

        context.results["scheme"] = scheme
        return context


# Can also call without progress tracking
scheme = generate_color_scheme(wallpaper_path)  # Decorator injects no-op
```

## Progress Querying

### Get Current Status

```python
pipeline = Pipeline(steps=[step1, step2, step3])

# Before execution
status = pipeline.get_status()
# {
#     "progress": 0.0,
#     "current_step": None,
#     "is_running": False,
#     "step_details": {
#         "step1": {"internal_progress": 0.0, "max_weight": 33.33, "contribution": 0.0},
#         "step2": {"internal_progress": 0.0, "max_weight": 33.33, "contribution": 0.0},
#         "step3": {"internal_progress": 0.0, "max_weight": 33.33, "contribution": 0.0}
#     }
# }

# During execution (from another thread)
status = pipeline.get_status()
# {
#     "progress": 45.5,
#     "current_step": "step2",
#     "is_running": True,
#     "step_details": {
#         "step1": {"internal_progress": 100.0, "max_weight": 33.33, "contribution": 33.33},
#         "step2": {"internal_progress": 36.6, "max_weight": 33.33, "contribution": 12.2},
#         "step3": {"internal_progress": 0.0, "max_weight": 33.33, "contribution": 0.0}
#     }
# }
```

### Progress Callback

```python
def progress_callback(step_idx, total_steps, step_name, overall_progress):
    print(f"Step {step_idx + 1}/{total_steps} ({step_name}): {overall_progress:.1f}%")

pipeline = Pipeline(steps=[step1, step2, step3], progress_callback=progress_callback)
pipeline.run(context)

# Output:
# Step 1/3 (step1): 33.3%
# Step 2/3 (step2): 66.7%
# Step 3/3 (step3): 100.0%
```

## Weight Calculation

### Serial Steps

```python
steps = [step1, step2, step3]
# Each step gets: 100 / 3 = 33.33% max weight
```

### Parallel Groups

```python
steps = [
    step1,                              # 33.33% weight
    [parallel1, parallel2, parallel3],  # 33.33% weight total
    step2                               # 33.33% weight
]
# parallel1, parallel2, parallel3 each get: 33.33 / 3 = 11.11% weight
```

## Examples

See the `examples/` directory for complete working examples:

- `demo_granular_progress.py` - Basic granular progress demonstration
- `demo_realtime_progress.py` - Real-time progress monitoring with progress bars
- `demo_parallel_progress.py` - Granular progress with parallel execution

Run examples:
```bash
uv run python examples/demo_granular_progress.py
uv run python examples/demo_realtime_progress.py
uv run python examples/demo_parallel_progress.py
```
