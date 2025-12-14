#!/usr/bin/env python3
"""Demo showing granular progress with parallel execution."""

import time
from typing import Any

from pipeline import Pipeline, PipelineContext, PipelineStep


class MockLogger:
    """Mock logger for demo."""

    def info(self, msg: str) -> None:
        pass

    def error(self, msg: str) -> None:
        pass


class MockConfig:
    """Mock config for demo."""

    pass


class ParallelStep(PipelineStep):
    """Step that reports progress and can run in parallel."""

    def __init__(self, step_id_val: str, duration: float, phases: int):
        self._step_id = step_id_val
        self.duration = duration
        self.phases = phases

    @property
    def step_id(self) -> str:
        return self._step_id

    @property
    def description(self) -> str:
        return f"Parallel step {self._step_id}"

    def run(self, context: PipelineContext[Any]) -> PipelineContext[Any]:
        phase_duration = self.duration / self.phases

        for i in range(self.phases):
            time.sleep(phase_duration)
            progress = ((i + 1) / self.phases) * 100
            context.update_step_progress(progress)
            print(
                f"  [{self.step_id}] Phase {i + 1}/{self.phases} complete ({progress:.0f}%)"  # noqa: E501
            )

        context.results[self.step_id] = f"completed in {self.duration}s"
        return context


def main() -> None:
    """Run the demo."""
    print("=" * 80)
    print("PARALLEL EXECUTION WITH GRANULAR PROGRESS")
    print("=" * 80)
    print(
        "\nThis demo shows how granular progress works with parallel execution."  # noqa: E501
    )
    print("Notice how parallel steps share their group's weight equally.\n")

    # Create context
    context = PipelineContext(
        app_config=MockConfig(), logger_instance=MockLogger()
    )

    # Define pipeline: serial -> parallel -> serial
    steps = [
        ParallelStep("init", duration=1.0, phases=2),
        [  # Parallel group - these 3 steps run concurrently
            ParallelStep("worker1", duration=2.0, phases=4),
            ParallelStep("worker2", duration=1.5, phases=3),
            ParallelStep("worker3", duration=2.5, phases=5),
        ],
        ParallelStep("finalize", duration=1.0, phases=2),
    ]

    # Progress callback
    def progress_callback(
        step_idx: int, total: int, name: str, progress: float
    ) -> None:
        print(
            f"\n📊 Step {step_idx + 1}/{total} completed ({name}) - Overall: {progress:.2f}%"  # noqa: E501
        )

    pipeline = Pipeline(steps=steps, progress_callback=progress_callback)

    # Show initial status
    status = pipeline.get_status()
    print("📋 Initial Status:")
    print(f"  Overall Progress: {status['progress']:.2f}%")
    print("  Step Weights:")
    for step_id, details in status["step_details"].items():
        print(f"    {step_id}: {details['max_weight']:.2f}% max weight")

    print("\n" + "=" * 80)
    print("EXECUTING PIPELINE")
    print("=" * 80)

    # Run pipeline
    start_time = time.time()
    print("\n🚀 Starting execution...\n")
    result = pipeline.run(context)
    elapsed = time.time() - start_time

    # Show final status
    print("\n" + "=" * 80)
    print("FINAL STATUS")
    print("=" * 80)
    status = pipeline.get_status()
    print(f"Overall Progress: {status['progress']:.2f}%")
    print(f"Total Time: {elapsed:.2f}s")
    print("\nStep Details:")
    for step_id, details in status["step_details"].items():
        print(f"  {step_id}:")
        print(f"    Internal Progress: {details['internal_progress']:.1f}%")
        print(f"    Max Weight: {details['max_weight']:.2f}%")
        print(f"    Contribution: {details['contribution']:.2f}%")

    print(f"\nResults: {result.results}")

    print("\n" + "=" * 80)
    print("KEY OBSERVATIONS")
    print("=" * 80)
    print("1. Step 'init' got 33.33% weight (1 of 3 top-level steps)")
    print("2. Parallel group got 33.33% weight, divided among 3 workers:")
    print("   - worker1: 11.11% max weight")
    print("   - worker2: 11.11% max weight")
    print("   - worker3: 11.11% max weight")
    print("3. Step 'finalize' got 33.33% weight")
    print("4. Parallel steps ran concurrently (total time < sum of durations)")
    print("5. Each step reported granular progress within its weight")
    print("=" * 80)


if __name__ == "__main__":
    main()
