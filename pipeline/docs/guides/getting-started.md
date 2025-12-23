# Getting Started

This guide walks you through creating your first pipeline.

## Prerequisites

```bash
pip install task-pipeline
```

## Step 1: Define Your Configuration

Create a configuration class for your application:

```python
from dataclasses import dataclass

@dataclass
class AppConfig:
    name: str
    version: str
    debug: bool = False
```

## Step 2: Create Pipeline Steps

Implement the `PipelineStep` interface for each step:

```python
from task_pipeline import PipelineContext, PipelineStep

class FetchDataStep(PipelineStep):
    @property
    def step_id(self) -> str:
        return "fetch_data"
    
    @property
    def description(self) -> str:
        return "Fetches data from source"
    
    def run(self, context: PipelineContext) -> PipelineContext:
        context.logger_instance.info("Fetching data...")
        
        # Simulate fetching data
        data = ["item1", "item2", "item3"]
        
        # Store result
        context.results[self.step_id] = data
        return context


class ProcessDataStep(PipelineStep):
    @property
    def step_id(self) -> str:
        return "process_data"
    
    @property
    def description(self) -> str:
        return "Processes the fetched data"
    
    def run(self, context: PipelineContext) -> PipelineContext:
        # Read from previous step
        data = context.results.get("fetch_data", [])
        
        context.logger_instance.info(f"Processing {len(data)} items...")
        
        # Process and store result
        processed = [item.upper() for item in data]
        context.results[self.step_id] = processed
        return context


class SaveResultsStep(PipelineStep):
    @property
    def step_id(self) -> str:
        return "save_results"
    
    @property
    def description(self) -> str:
        return "Saves processed results"
    
    def run(self, context: PipelineContext) -> PipelineContext:
        processed = context.results.get("process_data", [])
        
        context.logger_instance.info(f"Saving {len(processed)} results...")
        
        # Simulate saving
        context.results[self.step_id] = {"saved": True, "count": len(processed)}
        return context
```

## Step 3: Create and Run the Pipeline

```python
import logging
from task_pipeline import Pipeline, PipelineContext

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create configuration
config = AppConfig(name="my_app", version="1.0.0")

# Create context
context = PipelineContext(
    app_config=config,
    logger_instance=logger
)

# Create pipeline with steps
pipeline = Pipeline([
    FetchDataStep(),
    ProcessDataStep(),
    SaveResultsStep()
])

# Run the pipeline
result = pipeline.run(context)

# Check results
print(result.results)
# {
#     'fetch_data': ['item1', 'item2', 'item3'],
#     'process_data': ['ITEM1', 'ITEM2', 'ITEM3'],
#     'save_results': {'saved': True, 'count': 3}
# }
```

## Step 4: Add Progress Tracking (Optional)

```python
def progress_callback(step_idx: int, total: int, name: str, progress: float) -> None:
    print(f"[{step_idx}/{total}] {name}: {progress:.1f}%")

pipeline = Pipeline(
    steps=[FetchDataStep(), ProcessDataStep(), SaveResultsStep()],
    progress_callback=progress_callback
)

result = pipeline.run(context)
# Output:
# [0/3] fetch_data: 33.3%
# [1/3] process_data: 66.7%
# [2/3] save_results: 100.0%
```

**Evidence:** `tests/integration/test_progress_tracking.py`

## Next Steps

- [Serial Execution](serial-execution.md) — Run steps in sequence
- [Parallel Execution](parallel-execution.md) — Run steps concurrently
- [Error Handling](error-handling.md) — Handle failures gracefully
- [API Reference](../api/pipeline.md) — Full API documentation

