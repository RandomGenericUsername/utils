#!/usr/bin/env python3
"""Demo showing real-time progress querying during pipeline execution."""

import threading
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


class SlowStep(PipelineStep):
    """Step that takes time and reports progress."""

    def __init__(self, step_id_val: str, phases: int):
        self._step_id = step_id_val
        self.phases = phases

    @property
    def step_id(self) -> str:
        return self._step_id

    @property
    def description(self) -> str:
        return f"Slow step {self._step_id}"

    def run(self, context: PipelineContext[Any]) -> PipelineContext[Any]:
        for i in range(self.phases):
            time.sleep(0.5)  # Simulate work
            progress = ((i + 1) / self.phases) * 100
            context.update_step_progress(progress)

        context.results[self.step_id] = "done"
        return context


def progress_monitor(pipeline: Pipeline, stop_event: threading.Event) -> None:
    """Monitor and display progress in real-time."""
    print("\n" + "=" * 80)
    print("REAL-TIME PROGRESS MONITOR")
    print("=" * 80)
    print(
        f"{'Time':<8} {'Overall':<10} {'Step 1':<15} {'Step 2':<15} {'Step 3':<15}"  # noqa: E501
    )
    print("-" * 80)

    start_time = time.time()

    while not stop_event.is_set():
        status = pipeline.get_status()
        elapsed = time.time() - start_time

        # Get individual step progress
        details = status["step_details"]
        step1_prog = details.get("step1", {}).get("internal_progress", 0.0)
        step2_prog = details.get("step2", {}).get("internal_progress", 0.0)
        step3_prog = details.get("step3", {}).get("internal_progress", 0.0)

        # Create progress bars
        def make_bar(progress: float, width: int = 10) -> str:
            filled = int(progress / 100 * width)
            return f"[{'█' * filled}{'░' * (width - filled)}]"

        print(
            f"{elapsed:6.1f}s  "
            f"{status['progress']:5.1f}%  "
            f"{make_bar(step1_prog)} {step1_prog:5.1f}%  "
            f"{make_bar(step2_prog)} {step2_prog:5.1f}%  "
            f"{make_bar(step3_prog)} {step3_prog:5.1f}%",
            end="\r",
        )

        time.sleep(0.1)  # Update every 100ms

    # Final update
    status = pipeline.get_status()
    elapsed = time.time() - start_time
    details = status["step_details"]
    step1_prog = details.get("step1", {}).get("internal_progress", 0.0)
    step2_prog = details.get("step2", {}).get("internal_progress", 0.0)
    step3_prog = details.get("step3", {}).get("internal_progress", 0.0)

    def make_bar(progress: float, width: int = 10) -> str:
        filled = int(progress / 100 * width)
        return f"[{'█' * filled}{'░' * (width - filled)}]"

    print(
        f"{elapsed:6.1f}s  "
        f"{status['progress']:5.1f}%  "
        f"{make_bar(step1_prog)} {step1_prog:5.1f}%  "
        f"{make_bar(step2_prog)} {step2_prog:5.1f}%  "
        f"{make_bar(step3_prog)} {step3_prog:5.1f}%"
    )
    print("\n" + "=" * 80)


def main() -> None:
    """Run the demo."""
    print("=" * 80)
    print("REAL-TIME PROGRESS TRACKING DEMO")
    print("=" * 80)
    print("\nThis demo shows how you can query progress in real-time while")
    print(
        "the pipeline is executing. Perfect for progress bars and status displays!"  # noqa: E501
    )

    # Create context
    context = PipelineContext(
        app_config=MockConfig(), logger_instance=MockLogger()
    )

    # Define pipeline with 3 slow steps
    steps = [
        SlowStep("step1", phases=4),  # 4 phases, 2 seconds total
        SlowStep("step2", phases=6),  # 6 phases, 3 seconds total
        SlowStep("step3", phases=5),  # 5 phases, 2.5 seconds total
    ]

    pipeline = Pipeline(steps=steps)

    # Start progress monitor in separate thread
    stop_event = threading.Event()
    monitor_thread = threading.Thread(
        target=progress_monitor, args=(pipeline, stop_event), daemon=True
    )
    monitor_thread.start()

    # Run pipeline
    result = pipeline.run(context)

    # Stop monitor
    stop_event.set()
    monitor_thread.join()

    print("\n✅ Pipeline completed successfully!")
    print(f"Results: {result.results}")


if __name__ == "__main__":
    main()
