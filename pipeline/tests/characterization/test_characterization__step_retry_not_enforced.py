"""Characterization test: Step-level retries property exists but is NOT enforced.

Evidence Anchors:
- PipelineStep.retries property: pipeline/src/task_pipeline/core/types.py:119-122
- TaskExecutor.execute: pipeline/src/task_pipeline/executors/task_executor.py:27-28
- No retry logic in TaskExecutor

Current Behavior:
- PipelineStep has a `retries` property that defaults to 0
- Subclasses can override this property to return a retry count
- However, TaskExecutor.execute() does NOT implement retry logic
- If step.run() raises an exception, it's caught and stored in context.errors
- The step is NOT retried, regardless of the retries property value

TODO: Decide if step-level retry should be implemented or if the property
should be removed/deprecated.
"""

import pytest
from typing import Any

from task_pipeline import PipelineStep, PipelineContext, Pipeline, PipelineConfig


class FlakeyStepWithRetries(PipelineStep):
    """Test step that fails N times before succeeding."""

    def __init__(
        self, step_id: str, fail_count: int, retries_value: int, critical: bool = True
    ):
        """Initialize flakey step with retries.

        Args:
            step_id: Step identifier
            fail_count: Number of times to fail before succeeding
            retries_value: Declared retry count (NOT enforced)
            critical: Whether step is critical
        """
        self._step_id = step_id
        self._fail_count = fail_count
        self._retries_value = retries_value
        self._critical = critical
        self._attempt_count = 0

    @property
    def step_id(self) -> str:
        return self._step_id

    @property
    def description(self) -> str:
        return f"Flakey step with {self._retries_value} retries"

    @property
    def retries(self) -> int:
        """Return retry count (NOT enforced by executor)."""
        return self._retries_value

    @property
    def critical(self) -> bool:
        return self._critical

    def run(self, context: PipelineContext[Any]) -> PipelineContext[Any]:
        """Fail N times, then succeed (if retries were enforced)."""
        self._attempt_count += 1

        if self._attempt_count <= self._fail_count:
            raise RuntimeError(
                f"Attempt {self._attempt_count} failed (will succeed on attempt {self._fail_count + 1})"
            )

        context.results[self.step_id] = f"succeeded_on_attempt_{self._attempt_count}"
        return context


class TestCharacterizationStepRetryNotEnforced:
    """Characterization tests for step-level retry behavior."""

    def test_characterization__step_retries_property_exists(self):
        """CHARACTERIZATION: PipelineStep.retries property exists."""
        # Arrange
        step = FlakeyStepWithRetries("flakey", fail_count=2, retries_value=3)

        # Act
        retries_value = step.retries

        # Assert - Property exists and returns the value
        assert retries_value == 3

    def test_characterization__step_retries_not_enforced_critical_step(
        self, pipeline_context
    ):
        """CHARACTERIZATION: Retries NOT enforced for critical failing step.

        Current behavior: Step fails once and raises exception immediately,
        even though retries=3 is set.

        Expected behavior (if implemented): Should retry 3 times before failing.
        """
        # Arrange
        step = FlakeyStepWithRetries(
            step_id="flakey_step",
            fail_count=1,  # Will fail on first attempt, succeed on second
            retries_value=3,  # Should retry 3 times (but doesn't)
            critical=True,
        )
        pipeline = Pipeline(steps=[step])

        # Act & Assert - Fails immediately without retrying
        with pytest.raises(RuntimeError, match="Attempt 1 failed"):
            pipeline.run(pipeline_context)

        # If retries were enforced, this would succeed after 1 retry
        assert step._attempt_count == 1  # Only attempted once

    def test_characterization__step_retries_not_enforced_non_critical_step(
        self, pipeline_context
    ):
        """CHARACTERIZATION: Retries NOT enforced for non-critical failing step.

        Current behavior: Non-critical step fails once, error is stored,
        execution continues. No retries attempted.
        """
        # Arrange
        step = FlakeyStepWithRetries(
            step_id="flakey_step",
            fail_count=1,  # Will fail on first attempt
            retries_value=3,  # Should retry 3 times (but doesn't)
            critical=False,  # Non-critical
        )
        pipeline = Pipeline(steps=[step], config=PipelineConfig(fail_fast=False))

        # Act
        result = pipeline.run(pipeline_context)

        # Assert - Failed without retrying
        assert step._attempt_count == 1  # Only attempted once
        assert len(result.errors) == 1  # Error was stored
        assert "flakey_step" not in result.results  # Did not succeed
        # If retries were enforced, would have succeeded on attempt 2

    def test_characterization__step_retries_zero_default_works(
        self, pipeline_context
    ):
        """CHARACTERIZATION: Step with retries=0 (default) fails immediately."""
        # Arrange
        from tests.conftest import FailingStep

        step = FailingStep("failing", "Test error", critical=False)

        # Act
        retries_value = step.retries
        pipeline = Pipeline(steps=[step], config=PipelineConfig(fail_fast=False))
        result = pipeline.run(pipeline_context)

        # Assert
        assert retries_value == 0  # Default retries is 0
        assert len(result.errors) == 1  # Failed once, no retries

