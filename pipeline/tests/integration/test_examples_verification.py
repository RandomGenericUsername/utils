"""Tests that verify example patterns from examples/ directory work correctly.

These tests serve as executable documentation proving that all example
patterns in the examples/ directory are accurate and functional.

Evidence for:
- docs/guides/progress-tracking.md (granular progress)
- docs/guides/parallel-execution.md (parallel steps with progress)
"""

import threading
import time
from typing import Any
from unittest.mock import MagicMock

import pytest

from task_pipeline import (
    Pipeline,
    PipelineContext,
    PipelineStep,
    with_progress_callback,
)


class MockLogger:
    """Mock logger matching example patterns."""

    def info(self, msg: str) -> None:
        pass

    def error(self, msg: str) -> None:
        pass


class MockConfig:
    """Mock config matching example patterns."""

    pass


# =============================================================================
# Pattern 1: Granular Progress (from demo_granular_progress.py)
# =============================================================================


class TestGranularProgressPattern:
    """Tests for granular progress reporting within steps."""

    def test_step_can_report_granular_progress(self) -> None:
        """Step can call context.update_step_progress() to report progress."""
        progress_values: list[float] = []

        class ProgressReportingStep(PipelineStep):
            @property
            def step_id(self) -> str:
                return "progress_step"

            @property
            def description(self) -> str:
                return "Reports granular progress"

            def run(self, context: PipelineContext[Any]) -> PipelineContext[Any]:
                for i in range(5):
                    progress = ((i + 1) / 5) * 100
                    context.update_step_progress(progress)
                    progress_values.append(progress)
                return context

        context = PipelineContext(
            app_config=MockConfig(), logger_instance=MockLogger()
        )
        pipeline = Pipeline([ProgressReportingStep()])
        pipeline.run(context)

        assert progress_values == [20.0, 40.0, 60.0, 80.0, 100.0]

    def test_get_status_returns_step_details(self) -> None:
        """Pipeline.get_status() returns step-level progress details."""
        context = PipelineContext(
            app_config=MockConfig(), logger_instance=MockLogger()
        )

        class SimpleStep(PipelineStep):
            @property
            def step_id(self) -> str:
                return "simple"

            @property
            def description(self) -> str:
                return "Simple step"

            def run(self, context: PipelineContext[Any]) -> PipelineContext[Any]:
                return context

        pipeline = Pipeline([SimpleStep()])
        status = pipeline.get_status()

        assert "progress" in status
        assert "step_details" in status
        assert "is_running" in status
        assert "current_step" in status
        assert "simple" in status["step_details"]

    def test_step_details_include_weight_and_contribution(self) -> None:
        """Step details include max_weight and contribution."""

        class DummyStep(PipelineStep):
            def __init__(self, sid: str):
                self._id = sid

            @property
            def step_id(self) -> str:
                return self._id

            @property
            def description(self) -> str:
                return f"Step {self._id}"

            def run(self, context: PipelineContext[Any]) -> PipelineContext[Any]:
                return context

        pipeline = Pipeline([DummyStep("a"), DummyStep("b"), DummyStep("c")])
        status = pipeline.get_status()

        for step_id in ["a", "b", "c"]:
            details = status["step_details"][step_id]
            assert "max_weight" in details
            assert "contribution" in details
            assert "internal_progress" in details


# =============================================================================
# Pattern 2: with_progress_callback decorator (from demo_granular_progress.py)
# =============================================================================


class TestWithProgressCallbackDecorator:
    """Tests for @with_progress_callback decorator pattern."""

    def test_decorator_injects_noop_when_callback_not_provided(self) -> None:
        """Decorator injects no-op callback when not provided."""

        @with_progress_callback
        def process_data(data: str, progress_callback) -> str:
            progress_callback(50.0)  # Should not raise
            return f"processed_{data}"

        result = process_data("test")
        assert result == "processed_test"

    def test_decorator_uses_provided_callback(self) -> None:
        """Decorator uses callback when provided."""
        received_progress: list[float] = []

        @with_progress_callback
        def process_data(data: str, progress_callback) -> str:
            progress_callback(25.0)
            progress_callback(50.0)
            progress_callback(100.0)
            return data

        process_data("x", progress_callback=received_progress.append)
        assert received_progress == [25.0, 50.0, 100.0]

    def test_decorator_works_with_step_update_method(self) -> None:
        """Decorator can use context.update_step_progress as callback."""

        @with_progress_callback
        def utility_function(items: list, progress_callback) -> int:
            for i, item in enumerate(items):
                progress_callback((i + 1) / len(items) * 100)
            return len(items)

        class StepWithUtility(PipelineStep):
            @property
            def step_id(self) -> str:
                return "utility_step"

            @property
            def description(self) -> str:
                return "Step using utility"

            def run(self, context: PipelineContext[Any]) -> PipelineContext[Any]:
                count = utility_function(
                    [1, 2, 3], progress_callback=context.update_step_progress
                )
                context.results["count"] = count
                return context

        context = PipelineContext(
            app_config=MockConfig(), logger_instance=MockLogger()
        )
        pipeline = Pipeline([StepWithUtility()])
        result = pipeline.run(context)

        assert result.results["count"] == 3


# =============================================================================
# Pattern 3: Parallel Progress (from demo_parallel_progress.py)
# =============================================================================


class TestParallelProgressPattern:
    """Tests for parallel execution with progress tracking."""

    def test_parallel_steps_each_have_weight(self) -> None:
        """Parallel steps share their group's weight equally."""

        class ParallelStep(PipelineStep):
            def __init__(self, sid: str):
                self._id = sid

            @property
            def step_id(self) -> str:
                return self._id

            @property
            def description(self) -> str:
                return f"Parallel step {self._id}"

            def run(self, context: PipelineContext[Any]) -> PipelineContext[Any]:
                return context

        # Serial -> Parallel group -> Serial
        steps = [
            ParallelStep("init"),
            [ParallelStep("worker1"), ParallelStep("worker2"), ParallelStep("worker3")],
            ParallelStep("finalize"),
        ]

        pipeline = Pipeline(steps)
        status = pipeline.get_status()

        # 3 top-level items, so each gets ~33.33%
        init_weight = status["step_details"]["init"]["max_weight"]
        assert 33.0 <= init_weight <= 34.0

        # Parallel workers share their group's 33.33% equally
        w1_weight = status["step_details"]["worker1"]["max_weight"]
        assert 11.0 <= w1_weight <= 11.5  # ~11.11%

    def test_parallel_steps_can_report_individual_progress(self) -> None:
        """Each parallel step can report its own progress."""

        class ProgressStep(PipelineStep):
            def __init__(self, sid: str, phases: int):
                self._id = sid
                self.phases = phases

            @property
            def step_id(self) -> str:
                return self._id

            @property
            def description(self) -> str:
                return f"Step {self._id}"

            def run(self, context: PipelineContext[Any]) -> PipelineContext[Any]:
                for i in range(self.phases):
                    context.update_step_progress((i + 1) / self.phases * 100)
                context.results[self._id] = "done"
                return context

        context = PipelineContext(
            app_config=MockConfig(), logger_instance=MockLogger()
        )

        steps = [[ProgressStep("fast", 2), ProgressStep("slow", 4)]]

        pipeline = Pipeline(steps)
        result = pipeline.run(context)

        assert result.results["fast"] == "done"
        assert result.results["slow"] == "done"


# =============================================================================
# Pattern 4: Real-time Progress (from demo_realtime_progress.py)
# =============================================================================


class TestRealtimeProgressPattern:
    """Tests for querying progress during execution."""

    def test_get_status_can_be_called_during_execution(self) -> None:
        """Pipeline.get_status() can be called while pipeline is running."""
        statuses_during_run: list[dict] = []
        pipeline_ref: list[Pipeline] = []

        class SlowStep(PipelineStep):
            @property
            def step_id(self) -> str:
                return "slow"

            @property
            def description(self) -> str:
                return "Slow step"

            def run(self, context: PipelineContext[Any]) -> PipelineContext[Any]:
                # Query status during execution
                if pipeline_ref:
                    statuses_during_run.append(pipeline_ref[0].get_status())
                return context

        context = PipelineContext(
            app_config=MockConfig(), logger_instance=MockLogger()
        )

        pipeline = Pipeline([SlowStep()])
        pipeline_ref.append(pipeline)
        pipeline.run(context)

        assert len(statuses_during_run) == 1
        assert statuses_during_run[0]["is_running"] is True

    def test_is_running_reflects_execution_state(self) -> None:
        """Pipeline.is_running() and get_status()['is_running'] are accurate."""

        class CheckingStep(PipelineStep):
            def __init__(self):
                self.was_running = False

            @property
            def step_id(self) -> str:
                return "checker"

            @property
            def description(self) -> str:
                return "Checking step"

            def run(self, context: PipelineContext[Any]) -> PipelineContext[Any]:
                return context

        context = PipelineContext(
            app_config=MockConfig(), logger_instance=MockLogger()
        )

        pipeline = Pipeline([CheckingStep()])

        # Before run
        assert pipeline.is_running() is False
        assert pipeline.get_status()["is_running"] is False

        pipeline.run(context)

        # After run
        assert pipeline.is_running() is False
        assert pipeline.get_status()["is_running"] is False
