"""Characterization test: Step-level timeout property exists but is NOT enforced.

Evidence Anchors:
- PipelineStep.timeout property: pipeline/src/task_pipeline/core/types.py:115-117
- TaskExecutor.execute: pipeline/src/task_pipeline/executors/task_executor.py:27-28
- No timeout enforcement logic in TaskExecutor

Current Behavior:
- PipelineStep has a `timeout` property that defaults to None
- Subclasses can override this property to return a timeout value
- However, TaskExecutor.execute() does NOT enforce this timeout
- The step.run() method is called directly without any timeout wrapper

Note: Parallel group timeout IS implemented via ParallelConfig.timeout
(see test_parallel_executor.py:361-375), but individual step timeout is not.

TODO: Decide if step-level timeout should be implemented or if the property
should be removed/deprecated.
"""

import pytest
import time
from typing import Any

from task_pipeline import PipelineStep, PipelineContext, Pipeline


class SlowStepWithTimeout(PipelineStep):
    """Test step that takes longer than its declared timeout."""

    def __init__(self, step_id: str, sleep_duration: float, timeout_value: float):
        """Initialize slow step with timeout.

        Args:
            step_id: Step identifier
            sleep_duration: How long to sleep (seconds)
            timeout_value: Declared timeout value (NOT enforced)
        """
        self._step_id = step_id
        self._sleep_duration = sleep_duration
        self._timeout_value = timeout_value

    @property
    def step_id(self) -> str:
        return self._step_id

    @property
    def description(self) -> str:
        return f"Slow step with timeout {self._timeout_value}s"

    @property
    def timeout(self) -> float | None:
        """Return timeout value (NOT enforced by executor)."""
        return self._timeout_value

    def run(self, context: PipelineContext[Any]) -> PipelineContext[Any]:
        """Sleep for longer than timeout (should timeout but doesn't)."""
        time.sleep(self._sleep_duration)
        context.results[self.step_id] = "completed"
        return context


class TestCharacterizationStepTimeoutNotEnforced:
    """Characterization tests for step-level timeout behavior."""

    def test_characterization__step_timeout_property_exists(self):
        """CHARACTERIZATION: PipelineStep.timeout property exists."""
        # Arrange
        step = SlowStepWithTimeout("slow", 0.1, 0.05)

        # Act
        timeout_value = step.timeout

        # Assert - Property exists and returns the value
        assert timeout_value == 0.05

    def test_characterization__step_timeout_not_enforced_in_serial_execution(
        self, pipeline_context
    ):
        """CHARACTERIZATION: Step timeout is NOT enforced in serial execution.

        Current behavior: Step sleeps for 0.2s with timeout=0.1s, but
        execution completes successfully without timing out.

        Expected behavior (if implemented): Should raise TimeoutError.
        """
        # Arrange
        step = SlowStepWithTimeout(
            step_id="slow_step",
            sleep_duration=0.2,  # Sleep for 200ms
            timeout_value=0.1,  # Timeout set to 100ms
        )
        pipeline = Pipeline(steps=[step])

        # Act - Should timeout but doesn't (current behavior)
        start_time = time.time()
        result = pipeline.run(pipeline_context)
        elapsed_time = time.time() - start_time

        # Assert - Step completes successfully despite exceeding timeout
        assert "slow_step" in result.results
        assert result.results["slow_step"] == "completed"
        assert elapsed_time >= 0.2  # Actually took the full sleep time
        # If timeout were enforced, this would raise TimeoutError

    def test_characterization__multiple_steps_with_timeout_not_enforced(
        self, pipeline_context
    ):
        """CHARACTERIZATION: Multiple steps with timeout all complete.

        Current behavior: All steps complete regardless of timeout values.
        """
        # Arrange
        steps = [
            SlowStepWithTimeout("step1", 0.1, 0.05),  # Exceeds timeout
            SlowStepWithTimeout("step2", 0.1, 0.05),  # Exceeds timeout
            SlowStepWithTimeout("step3", 0.1, 0.05),  # Exceeds timeout
        ]
        pipeline = Pipeline(steps=steps)

        # Act
        result = pipeline.run(pipeline_context)

        # Assert - All steps complete despite exceeding timeout
        assert "step1" in result.results
        assert "step2" in result.results
        assert "step3" in result.results
        assert result.results["step1"] == "completed"
        assert result.results["step2"] == "completed"
        assert result.results["step3"] == "completed"

    def test_characterization__step_timeout_none_works_as_expected(
        self, pipeline_context
    ):
        """CHARACTERIZATION: Step with timeout=None completes normally."""
        # Arrange
        from tests.conftest import SimpleStep

        step = SimpleStep("normal_step", "key", "value")

        # Act
        timeout_value = step.timeout
        result = step.run(pipeline_context)

        # Assert
        assert timeout_value is None  # Default timeout is None
        assert "key" in result.results

