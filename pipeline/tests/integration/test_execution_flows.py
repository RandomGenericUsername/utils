"""Integration tests for basic pipeline execution flows.

Tests serial execution, parallel AND logic, and parallel OR logic.

Evidence Anchors:
- Serial execution: pipeline/src/task_pipeline/executors/pipeline_executor.py:17-48
- Parallel AND: pipeline/src/task_pipeline/executors/parallel_executor.py:117-123
- Parallel OR: pipeline/src/task_pipeline/executors/parallel_executor.py:117-123
- LogicOperator: pipeline/src/task_pipeline/core/types.py:78-83
"""

import pytest

from task_pipeline import (
    Pipeline,
    PipelineConfig,
    ParallelConfig,
    LogicOperator,
)


class TestSerialExecution:
    """Integration tests for serial pipeline execution."""

    def test_serial_execution_runs_steps_in_order(self, pipeline_context):
        """INTEGRATION: Serial steps execute in order, context flows through."""
        # Arrange
        from tests.conftest import SimpleStep

        steps = [
            SimpleStep("step1", "key1", "value1"),
            SimpleStep("step2", "key2", "value2"),
            SimpleStep("step3", "key3", "value3"),
        ]
        pipeline = Pipeline(steps=steps)

        # Act
        result = pipeline.run(pipeline_context)

        # Assert - All steps executed and results accumulated
        assert "key1" in result.results
        assert "key2" in result.results
        assert "key3" in result.results
        assert result.results["key1"] == "value1"
        assert result.results["key2"] == "value2"
        assert result.results["key3"] == "value3"
        assert len(result.errors) == 0

    def test_serial_execution_context_flows_between_steps(self, pipeline_context):
        """INTEGRATION: Context modifications flow from step to step."""
        # Arrange
        from tests.conftest import CounterStep

        steps = [
            CounterStep("step1", "counter"),  # counter = 1
            CounterStep("step2", "counter"),  # counter = 2
            CounterStep("step3", "counter"),  # counter = 3
        ]
        pipeline = Pipeline(steps=steps)

        # Act
        result = pipeline.run(pipeline_context)

        # Assert - Counter incremented by each step
        assert result.results["counter"] == 3
        assert len(result.errors) == 0

    def test_empty_pipeline_returns_unmodified_context(self, pipeline_context):
        """INTEGRATION: Empty pipeline returns context unchanged."""
        # Arrange
        pipeline = Pipeline(steps=[])

        # Act
        result = pipeline.run(pipeline_context)

        # Assert - Context unchanged
        assert result.results == {}
        assert result.errors == []
        assert result.app_config == pipeline_context.app_config


class TestParallelAndLogic:
    """Integration tests for parallel execution with AND logic."""

    def test_parallel_and_all_steps_succeed(self, pipeline_context):
        """INTEGRATION: Parallel AND succeeds when all steps succeed."""
        # Arrange
        from tests.conftest import SimpleStep

        parallel_steps = [
            SimpleStep("parallel1", "key1", "value1"),
            SimpleStep("parallel2", "key2", "value2"),
            SimpleStep("parallel3", "key3", "value3"),
        ]
        config = ParallelConfig(operator=LogicOperator.AND)
        pipeline_config = PipelineConfig(parallel_config=config)
        pipeline = Pipeline(steps=[parallel_steps], config=pipeline_config)

        # Act
        result = pipeline.run(pipeline_context)

        # Assert - All parallel steps succeeded
        assert "key1" in result.results
        assert "key2" in result.results
        assert "key3" in result.results
        assert len(result.errors) == 0

    def test_parallel_and_fails_when_one_step_fails(self, pipeline_context):
        """INTEGRATION: Parallel AND fails when any step fails."""
        # Arrange
        from tests.conftest import SimpleStep, FailingStep

        parallel_steps = [
            SimpleStep("parallel1", "key1", "value1"),
            FailingStep("failing", "Test failure", critical=True),
            SimpleStep("parallel3", "key3", "value3"),
        ]
        config = ParallelConfig(operator=LogicOperator.AND)
        pipeline_config = PipelineConfig(parallel_config=config)
        pipeline = Pipeline(steps=[parallel_steps], config=pipeline_config)

        # Act & Assert - Parallel group fails
        with pytest.raises(RuntimeError, match="Parallel group failed"):
            pipeline.run(pipeline_context)


class TestParallelOrLogic:
    """Integration tests for parallel execution with OR logic."""

    def test_parallel_or_succeeds_when_all_steps_succeed(
        self, pipeline_context
    ):
        """INTEGRATION: Parallel OR succeeds when all steps succeed."""
        # Arrange
        from tests.conftest import SimpleStep

        parallel_steps = [
            SimpleStep("parallel1", "key1", "value1"),
            SimpleStep("parallel2", "key2", "value2"),
        ]
        config = ParallelConfig(operator=LogicOperator.OR)
        pipeline_config = PipelineConfig(parallel_config=config)
        pipeline = Pipeline(steps=[parallel_steps], config=pipeline_config)

        # Act
        result = pipeline.run(pipeline_context)

        # Assert - All steps succeeded
        assert "key1" in result.results
        assert "key2" in result.results
        assert len(result.errors) == 0

    def test_parallel_or_succeeds_when_one_step_succeeds(
        self, pipeline_context
    ):
        """INTEGRATION: Parallel OR succeeds when one step succeeds."""
        # Arrange
        from tests.conftest import SimpleStep, FailingStep

        parallel_steps = [
            FailingStep("failing1", "Failure 1", critical=False),
            SimpleStep("success", "key", "value"),
            FailingStep("failing2", "Failure 2", critical=False),
        ]
        config = ParallelConfig(operator=LogicOperator.OR)
        pipeline_config = PipelineConfig(parallel_config=config)
        pipeline = Pipeline(steps=[parallel_steps], config=pipeline_config)

        # Act
        result = pipeline.run(pipeline_context)

        # Assert - At least one succeeded, so OR passes
        assert "key" in result.results
        assert result.results["key"] == "value"
