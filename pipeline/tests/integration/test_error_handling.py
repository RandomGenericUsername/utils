"""Integration tests for error handling (fail-fast and fail-slow modes).

Tests critical vs non-critical step failures and error accumulation.

Evidence Anchors:
- Fail-fast: pipeline/src/task_pipeline/pipeline.py:43-44
- Critical step handling: pipeline/src/task_pipeline/executors/task_executor.py:30-39
- Error accumulation: pipeline/src/task_pipeline/core/types.py:40-42
"""

import pytest

from task_pipeline import Pipeline, PipelineConfig


class TestFailFastMode:
    """Integration tests for fail-fast error handling."""

    def test_fail_fast_stops_on_first_critical_error(self, pipeline_context):
        """INTEGRATION: Fail-fast stops pipeline on first critical error."""
        # Arrange
        from tests.conftest import SimpleStep, FailingStep

        steps = [
            SimpleStep("step1", "key1", "value1"),
            FailingStep("failing", "Critical error", critical=True),
            SimpleStep("step3", "key3", "value3"),  # Should not execute
        ]
        config = PipelineConfig(fail_fast=True)
        pipeline = Pipeline(steps=steps, config=config)

        # Act & Assert - Pipeline stops at failing step
        with pytest.raises(RuntimeError, match="Critical error"):
            pipeline.run(pipeline_context)

    def test_fail_fast_continues_on_non_critical_error(self, pipeline_context):
        """INTEGRATION: Fail-fast continues when non-critical step fails."""
        # Arrange
        from tests.conftest import SimpleStep, FailingStep

        steps = [
            SimpleStep("step1", "key1", "value1"),
            FailingStep("failing", "Non-critical error", critical=False),
            SimpleStep("step3", "key3", "value3"),
        ]
        config = PipelineConfig(fail_fast=True)
        pipeline = Pipeline(steps=steps, config=config)

        # Act
        result = pipeline.run(pipeline_context)

        # Assert - Pipeline completed, error stored
        assert "key1" in result.results
        assert "key3" in result.results
        assert len(result.errors) == 1
        assert "Non-critical error" in str(result.errors[0])


class TestFailSlowMode:
    """Integration tests for fail-slow error handling."""

    def test_fail_slow_accumulates_all_errors(self, pipeline_context):
        """INTEGRATION: Fail-slow accumulates all errors from non-critical steps."""
        # Arrange
        from tests.conftest import SimpleStep, FailingStep

        steps = [
            SimpleStep("step1", "key1", "value1"),
            FailingStep("failing1", "Error 1", critical=False),
            SimpleStep("step3", "key3", "value3"),
            FailingStep("failing2", "Error 2", critical=False),
            SimpleStep("step5", "key5", "value5"),
        ]
        config = PipelineConfig(fail_fast=False)
        pipeline = Pipeline(steps=steps, config=config)

        # Act
        result = pipeline.run(pipeline_context)

        # Assert - All steps executed, all errors accumulated
        assert "key1" in result.results
        assert "key3" in result.results
        assert "key5" in result.results
        assert len(result.errors) == 2
        assert "Error 1" in str(result.errors[0])
        assert "Error 2" in str(result.errors[1])

    def test_fail_slow_continues_even_on_critical_error(
        self, pipeline_context
    ):
        """INTEGRATION: Fail-slow continues even on critical errors.

        CHARACTERIZATION: Current behavior is that fail_fast=False means
        ALL errors (including critical) are accumulated and execution
        continues. The 'critical' flag only affects whether the error
        is re-raised when fail_fast=True.
        """
        # Arrange
        from tests.conftest import SimpleStep, FailingStep

        steps = [
            SimpleStep("step1", "key1", "value1"),
            FailingStep("failing1", "Non-critical", critical=False),
            FailingStep("failing2", "Critical error", critical=True),
            SimpleStep("step4", "key4", "value4"),  # DOES execute
        ]
        config = PipelineConfig(fail_fast=False)
        pipeline = Pipeline(steps=steps, config=config)

        # Act
        result = pipeline.run(pipeline_context)

        # Assert - All steps executed despite critical error
        assert "key1" in result.results
        assert "key4" in result.results
        # Both errors accumulated
        assert len(result.errors) >= 2
        error_messages = [str(e) for e in result.errors]
        assert any("Non-critical" in msg for msg in error_messages)
        assert any("Critical error" in msg for msg in error_messages)


class TestMixedCriticalityScenarios:
    """Integration tests for mixed critical and non-critical steps."""

    def test_multiple_non_critical_failures_all_recorded(self, pipeline_context):
        """INTEGRATION: Multiple non-critical failures all recorded in context."""
        # Arrange
        from tests.conftest import FailingStep

        steps = [
            FailingStep("fail1", "Error 1", critical=False),
            FailingStep("fail2", "Error 2", critical=False),
            FailingStep("fail3", "Error 3", critical=False),
        ]
        config = PipelineConfig(fail_fast=False)
        pipeline = Pipeline(steps=steps, config=config)

        # Act
        result = pipeline.run(pipeline_context)

        # Assert - All errors recorded
        assert len(result.errors) == 3
        error_messages = [str(e) for e in result.errors]
        assert any("Error 1" in msg for msg in error_messages)
        assert any("Error 2" in msg for msg in error_messages)
        assert any("Error 3" in msg for msg in error_messages)

    def test_successful_steps_after_non_critical_failures(self, pipeline_context):
        """INTEGRATION: Successful steps execute after non-critical failures."""
        # Arrange
        from tests.conftest import SimpleStep, FailingStep

        steps = [
            FailingStep("fail1", "Error 1", critical=False),
            SimpleStep("success1", "key1", "value1"),
            FailingStep("fail2", "Error 2", critical=False),
            SimpleStep("success2", "key2", "value2"),
        ]
        config = PipelineConfig(fail_fast=False)
        pipeline = Pipeline(steps=steps, config=config)

        # Act
        result = pipeline.run(pipeline_context)

        # Assert - Successful steps completed
        assert "key1" in result.results
        assert "key2" in result.results
        assert result.results["key1"] == "value1"
        assert result.results["key2"] == "value2"
        assert len(result.errors) == 2

