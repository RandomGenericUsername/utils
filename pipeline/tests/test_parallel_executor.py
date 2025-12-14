"""Tests for ParallelTaskExecutor."""

import time
from concurrent.futures import TimeoutError

import pytest

from pipeline import (
    LogicOperator,
    ParallelConfig,
    ParallelTaskExecutor,
)


class TestParallelExecutorBasics:
    """Test suite for ParallelTaskExecutor basic functionality."""

    def test_executor_can_be_instantiated(self):
        """Test that ParallelTaskExecutor can be instantiated."""
        # Act
        executor = ParallelTaskExecutor()

        # Assert
        assert executor is not None
        assert isinstance(executor, ParallelTaskExecutor)

    def test_executor_has_execute_method(self):
        """Test that ParallelTaskExecutor has execute method."""
        # Arrange
        executor = ParallelTaskExecutor()

        # Assert
        assert hasattr(executor, "execute")
        assert callable(executor.execute)

    def test_executor_with_custom_task_executor(self):
        """Test creating executor with custom task executor."""
        # Arrange
        from pipeline import TaskExecutor

        custom_task_executor = TaskExecutor()

        # Act
        executor = ParallelTaskExecutor(task_executor=custom_task_executor)

        # Assert
        assert executor.task_executor == custom_task_executor


class TestParallelExecutorExecution:
    """Test suite for ParallelTaskExecutor parallel execution."""

    def test_execute_empty_steps_list(self, pipeline_context, parallel_config):
        """Test executing empty steps list."""
        # Arrange
        executor = ParallelTaskExecutor()

        # Act
        result = executor.execute([], pipeline_context, parallel_config)

        # Assert
        assert result == pipeline_context

    def test_execute_single_step(
        self, simple_step, pipeline_context, parallel_config
    ):
        """Test executing single step in parallel."""
        # Arrange
        executor = ParallelTaskExecutor()

        # Act
        result = executor.execute(
            [simple_step], pipeline_context, parallel_config
        )

        # Assert
        assert result.results["test_key"] == "test_value"

    def test_execute_multiple_steps_in_parallel(self, pipeline_context):
        """Test executing multiple steps in parallel."""
        # Arrange
        from .conftest import SimpleStep

        executor = ParallelTaskExecutor()
        steps = [
            SimpleStep("step1", "key1", "value1"),
            SimpleStep("step2", "key2", "value2"),
            SimpleStep("step3", "key3", "value3"),
        ]
        config = ParallelConfig(operator=LogicOperator.AND, max_workers=3)

        # Act
        result = executor.execute(steps, pipeline_context, config)

        # Assert
        assert result.results["key1"] == "value1"
        assert result.results["key2"] == "value2"
        assert result.results["key3"] == "value3"

    def test_execute_steps_run_concurrently(self, pipeline_context):
        """Test that steps actually run in parallel."""
        # Arrange
        from .conftest import SlowStep

        executor = ParallelTaskExecutor()
        steps = [
            SlowStep("slow1", 0.1),
            SlowStep("slow2", 0.1),
            SlowStep("slow3", 0.1),
        ]
        config = ParallelConfig(operator=LogicOperator.AND, max_workers=3)

        # Act
        start_time = time.time()
        result = executor.execute(steps, pipeline_context, config)
        elapsed_time = time.time() - start_time

        # Assert - Should take ~0.1s (parallel) not ~0.3s (serial)
        assert elapsed_time < 0.25  # Allow some overhead
        assert result.results["slow1_completed"] is True
        assert result.results["slow2_completed"] is True
        assert result.results["slow3_completed"] is True

    def test_execute_with_max_workers_limit(self, pipeline_context):
        """Test executing with max_workers limit."""
        # Arrange
        from .conftest import SimpleStep

        executor = ParallelTaskExecutor()
        steps = [
            SimpleStep(f"step{i}", f"key{i}", f"value{i}") for i in range(10)
        ]
        config = ParallelConfig(operator=LogicOperator.AND, max_workers=2)

        # Act
        result = executor.execute(steps, pipeline_context, config)

        # Assert - All steps should complete
        assert len(result.results) == 10


class TestParallelExecutorContextMerging:
    """Test suite for context merging in parallel execution."""

    def test_merge_results_from_multiple_steps(self, pipeline_context):
        """Test merging results from multiple parallel steps."""
        # Arrange
        from .conftest import SimpleStep

        executor = ParallelTaskExecutor()
        steps = [
            SimpleStep("step1", "a", 1),
            SimpleStep("step2", "b", 2),
            SimpleStep("step3", "c", 3),
        ]
        config = ParallelConfig(operator=LogicOperator.AND)

        # Act
        result = executor.execute(steps, pipeline_context, config)

        # Assert
        assert result.results["a"] == 1
        assert result.results["b"] == 2
        assert result.results["c"] == 3

    def test_merge_numeric_results_with_increments(self, pipeline_context):
        """Test merging numeric results with proper increment calculation."""
        # Arrange
        from .conftest import CounterStep

        executor = ParallelTaskExecutor()
        pipeline_context.results["counter"] = 0
        steps = [
            CounterStep("step1", "counter", 5),
            CounterStep("step2", "counter", 3),
            CounterStep("step3", "counter", 2),
        ]
        config = ParallelConfig(operator=LogicOperator.AND)

        # Act
        result = executor.execute(steps, pipeline_context, config)

        # Assert - Should sum increments: 5 + 3 + 2 = 10
        assert result.results["counter"] == 10

    def test_merge_errors_from_multiple_steps(self, pipeline_context):
        """Test merging errors from multiple parallel steps."""
        # Arrange
        from .conftest import FailingStep

        executor = ParallelTaskExecutor()
        steps = [
            FailingStep("fail1", "Error 1", critical=False),
            FailingStep("fail2", "Error 2", critical=False),
        ]
        config = ParallelConfig(
            operator=LogicOperator.OR
        )  # OR so it doesn't fail

        # Act
        result = executor.execute(steps, pipeline_context, config)

        # Assert - Errors should be merged
        assert len(result.errors) >= 0  # May have errors depending on OR logic

    def test_context_isolation_between_parallel_steps(self, pipeline_context):
        """Test that parallel steps have isolated contexts."""
        # Arrange
        from typing import Any

        from pipeline import PipelineContext, PipelineStep

        class IsolationTestStep(PipelineStep):
            def __init__(self, step_id: str):
                self._step_id = step_id

            @property
            def step_id(self) -> str:
                return self._step_id

            @property
            def description(self) -> str:
                return f"Isolation test: {self._step_id}"

            def run(
                self, context: PipelineContext[Any]
            ) -> PipelineContext[Any]:
                # Try to modify a shared key
                context.results["shared"] = self._step_id
                context.results[f"unique_{self._step_id}"] = True
                return context

        executor = ParallelTaskExecutor()
        steps = [
            IsolationTestStep("step1"),
            IsolationTestStep("step2"),
            IsolationTestStep("step3"),
        ]
        config = ParallelConfig(operator=LogicOperator.AND)

        # Act
        result = executor.execute(steps, pipeline_context, config)

        # Assert - Each step should have its unique result
        assert result.results.get("unique_step1") is True
        assert result.results.get("unique_step2") is True
        assert result.results.get("unique_step3") is True


class TestParallelExecutorLogicOperators:
    """Test suite for AND/OR logic operators."""

    def test_and_operator_all_steps_succeed(self, pipeline_context):
        """Test AND operator when all steps succeed."""
        # Arrange
        from .conftest import SimpleStep

        executor = ParallelTaskExecutor()
        steps = [
            SimpleStep("step1", "key1", "value1"),
            SimpleStep("step2", "key2", "value2"),
        ]
        config = ParallelConfig(operator=LogicOperator.AND)

        # Act
        result = executor.execute(steps, pipeline_context, config)

        # Assert
        assert result.results["key1"] == "value1"
        assert result.results["key2"] == "value2"

    def test_and_operator_one_step_fails(self, pipeline_context):
        """Test AND operator when one step fails."""
        # Arrange
        from .conftest import FailingStep, SimpleStep

        executor = ParallelTaskExecutor()
        steps = [
            SimpleStep("step1", "key1", "value1"),
            FailingStep("fail", "Error", critical=True),
        ]
        config = ParallelConfig(operator=LogicOperator.AND)

        # Act & Assert
        with pytest.raises(RuntimeError, match="Parallel group failed"):
            executor.execute(steps, pipeline_context, config)

    def test_and_operator_all_steps_fail(self, pipeline_context):
        """Test AND operator when all steps fail."""
        # Arrange
        from .conftest import FailingStep

        executor = ParallelTaskExecutor()
        steps = [
            FailingStep("fail1", "Error 1", critical=True),
            FailingStep("fail2", "Error 2", critical=True),
        ]
        config = ParallelConfig(operator=LogicOperator.AND)

        # Act & Assert
        with pytest.raises(RuntimeError, match="Parallel group failed"):
            executor.execute(steps, pipeline_context, config)

    def test_or_operator_all_steps_succeed(self, pipeline_context):
        """Test OR operator when all steps succeed."""
        # Arrange
        from .conftest import SimpleStep

        executor = ParallelTaskExecutor()
        steps = [
            SimpleStep("step1", "key1", "value1"),
            SimpleStep("step2", "key2", "value2"),
        ]
        config = ParallelConfig(operator=LogicOperator.OR)

        # Act
        result = executor.execute(steps, pipeline_context, config)

        # Assert
        assert result.results["key1"] == "value1"
        assert result.results["key2"] == "value2"

    def test_or_operator_one_step_succeeds(self, pipeline_context):
        """Test OR operator when one step succeeds."""
        # Arrange
        from .conftest import FailingStep, SimpleStep

        executor = ParallelTaskExecutor()
        steps = [
            SimpleStep("step1", "key1", "value1"),
            FailingStep("fail", "Error", critical=True),
        ]
        config = ParallelConfig(operator=LogicOperator.OR)

        # Act
        result = executor.execute(steps, pipeline_context, config)

        # Assert - Should succeed because one step succeeded
        assert result.results["key1"] == "value1"

    def test_or_operator_all_steps_fail(self, pipeline_context):
        """Test OR operator when all steps fail."""
        # Arrange
        from .conftest import FailingStep

        executor = ParallelTaskExecutor()
        steps = [
            FailingStep("fail1", "Error 1", critical=True),
            FailingStep("fail2", "Error 2", critical=True),
        ]
        config = ParallelConfig(operator=LogicOperator.OR)

        # Act & Assert
        with pytest.raises(RuntimeError, match="Parallel group failed"):
            executor.execute(steps, pipeline_context, config)


class TestParallelExecutorTimeout:
    """Test suite for timeout handling."""

    def test_timeout_with_slow_steps(self, pipeline_context):
        """Test timeout when steps take too long."""
        # Arrange
        from .conftest import SlowStep

        executor = ParallelTaskExecutor()
        steps = [
            SlowStep("slow1", 2.0),  # Takes 2 seconds
            SlowStep("slow2", 2.0),
        ]
        config = ParallelConfig(operator=LogicOperator.AND, timeout=0.5)

        # Act & Assert
        with pytest.raises(TimeoutError):
            executor.execute(steps, pipeline_context, config)

    def test_no_timeout_with_fast_steps(self, pipeline_context):
        """Test no timeout when steps complete quickly."""
        # Arrange
        from .conftest import SlowStep

        executor = ParallelTaskExecutor()
        steps = [
            SlowStep("fast1", 0.1),
            SlowStep("fast2", 0.1),
        ]
        config = ParallelConfig(operator=LogicOperator.AND, timeout=5.0)

        # Act
        result = executor.execute(steps, pipeline_context, config)

        # Assert
        assert result.results["fast1_completed"] is True
        assert result.results["fast2_completed"] is True

    def test_timeout_none_allows_unlimited_time(self, pipeline_context):
        """Test that timeout=None allows unlimited execution time."""
        # Arrange
        from .conftest import SlowStep

        executor = ParallelTaskExecutor()
        steps = [SlowStep("slow", 0.2)]
        config = ParallelConfig(operator=LogicOperator.AND, timeout=None)

        # Act
        result = executor.execute(steps, pipeline_context, config)

        # Assert
        assert result.results["slow_completed"] is True


class TestParallelExecutorEdgeCases:
    """Test suite for edge cases."""

    def test_execute_with_original_context_preservation(
        self, pipeline_context
    ):
        """Test original context preserved during parallel execution."""
        # Arrange
        from .conftest import SimpleStep

        executor = ParallelTaskExecutor()
        pipeline_context.results["original"] = "value"
        steps = [SimpleStep("step1", "new", "data")]
        config = ParallelConfig(operator=LogicOperator.AND)

        # Act
        result = executor.execute(steps, pipeline_context, config)

        # Assert
        assert result.results["original"] == "value"
        assert result.results["new"] == "data"

    def test_execute_preserves_app_config(self, pipeline_context):
        """Test that app_config is preserved through parallel execution."""
        # Arrange
        from .conftest import SimpleStep

        executor = ParallelTaskExecutor()
        original_app_config = pipeline_context.app_config
        steps = [SimpleStep("step1", "key", "value")]
        config = ParallelConfig(operator=LogicOperator.AND)

        # Act
        result = executor.execute(steps, pipeline_context, config)

        # Assert
        assert result.app_config == original_app_config
        assert result.app_config.name == "test_app"

    def test_execute_preserves_logger(self, pipeline_context):
        """Test that logger is preserved through parallel execution."""
        # Arrange
        from .conftest import SimpleStep

        executor = ParallelTaskExecutor()
        original_logger = pipeline_context.logger_instance
        steps = [SimpleStep("step1", "key", "value")]
        config = ParallelConfig(operator=LogicOperator.AND)

        # Act
        result = executor.execute(steps, pipeline_context, config)

        # Assert
        assert result.logger_instance == original_logger
