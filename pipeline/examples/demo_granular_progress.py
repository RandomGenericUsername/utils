#!/usr/bin/env python3
"""Demo script showing granular progress tracking in action."""

import time
from typing import Any

from pipeline import (
    Pipeline,
    PipelineContext,
    PipelineStep,
    with_progress_callback,
)


class MockLogger:
    """Mock logger for demo."""

    def info(self, msg: str) -> None:
        print(f"[INFO] {msg}")

    def error(self, msg: str) -> None:
        print(f"[ERROR] {msg}")


class MockConfig:
    """Mock config for demo."""

    pass


# Example 1: Step with granular progress updates
class DataProcessingStep(PipelineStep):
    """Step that reports granular progress."""

    @property
    def step_id(self) -> str:
        return "data_processing"

    @property
    def description(self) -> str:
        return "Process data with granular progress"

    def run(self, context: PipelineContext[Any]) -> PipelineContext[Any]:
        items = ["item1", "item2", "item3", "item4", "item5"]

        for i, item in enumerate(items):
            # Simulate work
            time.sleep(0.2)

            # Report progress
            progress = ((i + 1) / len(items)) * 100
            context.update_step_progress(progress)
            print(f"  Processing {item}... ({progress:.1f}% of this step)")

        context.results["processed"] = len(items)
        return context


# Example 2: Step that never reports progress (auto-completes)
class SimpleStep(PipelineStep):
    """Step that doesn't report progress - will auto-complete."""

    def __init__(self, step_id_val: str):
        self._step_id = step_id_val

    @property
    def step_id(self) -> str:
        return self._step_id

    @property
    def description(self) -> str:
        return f"Simple step {self._step_id}"

    def run(self, context: PipelineContext[Any]) -> PipelineContext[Any]:
        time.sleep(0.3)
        context.results[self.step_id] = "done"
        print(f"  {self.step_id} completed (no progress updates)")
        return context


# Example 3: Using the decorator with utility functions
@with_progress_callback
def complex_operation(data: str, progress_callback) -> str:
    """Utility function that reports progress."""
    print(f"  Starting complex operation on {data}")

    # Phase 1
    time.sleep(0.15)
    progress_callback(25.0)
    print("    Phase 1 complete (25%)")

    # Phase 2
    time.sleep(0.15)
    progress_callback(50.0)
    print("    Phase 2 complete (50%)")

    # Phase 3
    time.sleep(0.15)
    progress_callback(75.0)
    print("    Phase 3 complete (75%)")

    # Phase 4
    time.sleep(0.15)
    progress_callback(100.0)
    print("    Phase 4 complete (100%)")

    return f"processed_{data}"


class UtilityBasedStep(PipelineStep):
    """Step that delegates to utility function."""

    @property
    def step_id(self) -> str:
        return "utility_based"

    @property
    def description(self) -> str:
        return "Step using utility function with progress"

    def run(self, context: PipelineContext[Any]) -> PipelineContext[Any]:
        result = complex_operation(
            "data", progress_callback=context.update_step_progress
        )
        context.results["utility_result"] = result
        return context


def print_status(pipeline: Pipeline, label: str) -> None:
    """Print current pipeline status."""
    status = pipeline.get_status()
    print(f"\n{label}")
    print(f"  Overall Progress: {status['progress']:.2f}%")
    print(f"  Current Step: {status['current_step']}")
    print(f"  Is Running: {status['is_running']}")
    print("  Step Details:")
    for step_id, details in status["step_details"].items():
        print(f"    {step_id}:")
        print(f"      Internal Progress: {details['internal_progress']:.1f}%")
        print(f"      Max Weight: {details['max_weight']:.2f}%")
        print(f"      Contribution: {details['contribution']:.2f}%")


def main() -> None:
    """Run the demo."""
    print("=" * 70)
    print("GRANULAR PROGRESS TRACKING DEMO")
    print("=" * 70)

    # Create context
    context = PipelineContext(
        app_config=MockConfig(), logger_instance=MockLogger()
    )

    # Define pipeline with 3 steps
    steps = [
        DataProcessingStep(),  # Reports granular progress
        SimpleStep("simple"),  # No progress updates (auto-completes)
        UtilityBasedStep(),  # Uses utility function with progress
    ]

    # Create pipeline with progress callback
    def progress_callback(
        step_idx: int, total: int, name: str, progress: float
    ) -> None:
        print(
            f"\n📊 Progress Update: Step {step_idx + 1}/{total} ({name}) - Overall: {progress:.2f}%"  # noqa: E501
        )

    pipeline = Pipeline(steps=steps, progress_callback=progress_callback)

    # Show initial status
    print_status(pipeline, "📋 Initial Status:")

    print("\n" + "=" * 70)
    print("EXECUTING PIPELINE")
    print("=" * 70)

    # Run pipeline
    print("\n🚀 Starting pipeline execution...\n")
    result = pipeline.run(context)

    # Show final status
    print_status(pipeline, "\n✅ Final Status:")

    # Show results
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"Results: {result.results}")
    print(f"Errors: {result.errors}")

    print("\n" + "=" * 70)
    print("KEY OBSERVATIONS")
    print("=" * 70)
    print(
        "1. DataProcessingStep reported progress 5 times (20%, 40%, 60%, 80%, 100%)"  # noqa: E501
    )
    print("2. SimpleStep never reported progress - auto-completed to 100%")
    print(
        "3. UtilityBasedStep used decorator - reported 4 phases (25%, 50%, 75%, 100%)"  # noqa: E501
    )
    print("4. Each step got equal weight: 33.33% of total progress")
    print("5. Overall progress updated smoothly with granular steps")
    print("=" * 70)


if __name__ == "__main__":
    main()
