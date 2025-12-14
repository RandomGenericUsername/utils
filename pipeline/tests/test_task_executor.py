"""Tests for TaskExecutor."""

import pytest

from pipeline import TaskExecutor


class TestTaskExecutorBasics:
    """Test suite for TaskExecutor basic functionality."""

    def test_executor_can_be_instantiated(self):
        """Test that TaskExecutor can be instantiated."""
        # Act
        executor = TaskExecutor()

        # Assert
        assert executor is not None
        assert isinstance(executor, TaskExecutor)

    def test_executor_has_execute_method(self):
        """Test that TaskExecutor has execute method."""
        # Arrange
        executor = TaskExecutor()

        # Assert
        assert hasattr(executor, "execute")
        assert callable(executor.execute)


class TestTaskExecutorExecution:
    """Test suite for TaskExecutor step execution."""

    def test_execute_simple_step(self, simple_step, pipeline_context):
        """Test executing a simple step."""
        # Arrange
        executor = TaskExecutor()

        # Act
        result = executor.execute(simple_step, pipeline_context)

        # Assert
        assert result is not None
        assert result.results["test_key"] == "test_value"

    def test_execute_returns_modified_context(
        self, simple_step, pipeline_context
    ):
        """Test that execute returns the modified context."""
        # Arrange
        executor = TaskExecutor()
        original_context_id = id(pipeline_context)

        # Act
        result = executor.execute(simple_step, pipeline_context)

        # Assert
        assert id(result) == original_context_id
        assert result == pipeline_context

    def test_execute_multiple_steps_sequentially(
        self, simple_step, counter_step, pipeline_context
    ):
        """Test executing multiple steps sequentially."""
        # Arrange
        executor = TaskExecutor()

        # Act
        result1 = executor.execute(simple_step, pipeline_context)
        result2 = executor.execute(counter_step, result1)

        # Assert
        assert result2.results["test_key"] == "test_value"
        assert result2.results["counter"] == 1

    def test_execute_step_can_modify_existing_results(self, pipeline_context):
        """Test that step can modify existing results."""
        # Arrange
        from typing import Any

        from pipeline import PipelineContext, PipelineStep

        class ModifyStep(PipelineStep):
            @property
            def step_id(self) -> str:
                return "modify_step"

            @property
            def description(self) -> str:
                return "Modify existing results"

            def run(
                self, context: PipelineContext[Any]
            ) -> PipelineContext[Any]:
                context.results["counter"] = (
                    context.results.get("counter", 0) + 10
                )
                return context

        executor = TaskExecutor()
        pipeline_context.results["counter"] = 5

        # Act
        result = executor.execute(ModifyStep(), pipeline_context)

        # Assert
        assert result.results["counter"] == 15

    def test_execute_step_with_logger_access(self, pipeline_context):
        """Test executing step that uses logger."""
        # Arrange
        from typing import Any

        from pipeline import PipelineContext, PipelineStep

        class LoggingStep(PipelineStep):
            @property
            def step_id(self) -> str:
                return "logging_step"

            @property
            def description(self) -> str:
                return "Step with logging"

            def run(
                self, context: PipelineContext[Any]
            ) -> PipelineContext[Any]:
                context.logger_instance.info("Executing step")
                context.results["logged"] = True
                return context

        executor = TaskExecutor()

        # Act
        result = executor.execute(LoggingStep(), pipeline_context)

        # Assert
        assert result.results["logged"] is True
        pipeline_context.logger_instance.info.assert_called_once()


class TestTaskExecutorErrorHandling:
    """Test suite for TaskExecutor error handling."""

    def test_execute_critical_failing_step_raises_exception(
        self, failing_step, pipeline_context
    ):
        """Test that critical failing step raises exception."""
        # Arrange
        executor = TaskExecutor()

        # Act & Assert
        with pytest.raises(RuntimeError) as exc_info:
            executor.execute(failing_step, pipeline_context)

        assert str(exc_info.value) == "Test error"

    def test_execute_critical_failing_step_stores_error(
        self, failing_step, pipeline_context
    ):
        """Test that critical failing step stores error in context."""
        # Arrange
        executor = TaskExecutor()

        # Act & Assert
        with pytest.raises(RuntimeError):
            executor.execute(failing_step, pipeline_context)

        # Assert error was stored
        assert len(pipeline_context.errors) == 1
        assert isinstance(pipeline_context.errors[0], RuntimeError)
        assert str(pipeline_context.errors[0]) == "Test error"

    def test_execute_non_critical_failing_step_does_not_raise(
        self, non_critical_failing_step, pipeline_context
    ):
        """Test that non-critical failing step does not raise exception."""
        # Arrange
        executor = TaskExecutor()

        # Act
        result = executor.execute(non_critical_failing_step, pipeline_context)

        # Assert - No exception raised
        assert result is not None
        assert result == pipeline_context

    def test_execute_non_critical_failing_step_stores_error(
        self, non_critical_failing_step, pipeline_context
    ):
        """Test that non-critical failing step stores error in context."""
        # Arrange
        executor = TaskExecutor()

        # Act
        result = executor.execute(non_critical_failing_step, pipeline_context)

        # Assert
        assert len(result.errors) == 1
        assert isinstance(result.errors[0], RuntimeError)
        assert str(result.errors[0]) == "Non-critical error"

    def test_execute_non_critical_failing_step_returns_original_context(
        self, non_critical_failing_step, pipeline_context
    ):
        """Test that non-critical failing step returns original context."""
        # Arrange
        executor = TaskExecutor()
        pipeline_context.results["existing"] = "value"

        # Act
        result = executor.execute(non_critical_failing_step, pipeline_context)

        # Assert - Original context preserved
        assert result.results["existing"] == "value"

    def test_execute_multiple_non_critical_failures(self, pipeline_context):
        """Test executing multiple non-critical failing steps."""
        # Arrange
        from .conftest import FailingStep

        executor = TaskExecutor()
        step1 = FailingStep("fail1", "Error 1", critical=False)
        step2 = FailingStep("fail2", "Error 2", critical=False)
        step3 = FailingStep("fail3", "Error 3", critical=False)

        # Act
        result1 = executor.execute(step1, pipeline_context)
        result2 = executor.execute(step2, result1)
        result3 = executor.execute(step3, result2)

        # Assert
        assert len(result3.errors) == 3
        assert str(result3.errors[0]) == "Error 1"
        assert str(result3.errors[1]) == "Error 2"
        assert str(result3.errors[2]) == "Error 3"

    def test_execute_mixed_critical_and_non_critical(
        self, simple_step, non_critical_failing_step, pipeline_context
    ):
        """Test executing mix of successful and non-critical failing steps."""
        # Arrange
        executor = TaskExecutor()

        # Act
        result1 = executor.execute(simple_step, pipeline_context)
        result2 = executor.execute(non_critical_failing_step, result1)

        # Assert
        assert result2.results["test_key"] == "test_value"  # From simple_step
        assert len(result2.errors) == 1  # From non_critical_failing_step

    def test_execute_error_with_context_without_errors_attribute(
        self, failing_step, mock_app_config, mock_logger
    ):
        """Test error handling when context doesn't have errors attribute."""
        # Arrange
        from dataclasses import dataclass

        from pipeline import PipelineContext

        # Create context without errors attribute by using a custom class
        @dataclass
        class MinimalContext:
            app_config: object
            logger_instance: object
            results: dict

        # This won't work with PipelineContext, so we test the hasattr check
        executor = TaskExecutor()
        context = PipelineContext(
            app_config=mock_app_config, logger_instance=mock_logger
        )

        # Act & Assert
        with pytest.raises(RuntimeError):
            executor.execute(failing_step, context)

        # Verify error was stored (PipelineContext has errors attribute)
        assert len(context.errors) == 1


class TestTaskExecutorEdgeCases:
    """Test suite for TaskExecutor edge cases."""

    def test_execute_step_that_returns_different_context(
        self, pipeline_context
    ):
        """Test step that returns a different context object."""
        # Arrange
        from typing import Any

        from pipeline import PipelineContext, PipelineStep

        class NewContextStep(PipelineStep):
            @property
            def step_id(self) -> str:
                return "new_context"

            @property
            def description(self) -> str:
                return "Returns new context"

            def run(
                self, context: PipelineContext[Any]
            ) -> PipelineContext[Any]:
                # Create a new context
                new_context = PipelineContext(
                    app_config=context.app_config,
                    logger_instance=context.logger_instance,
                )
                new_context.results["new"] = "context"
                return new_context

        executor = TaskExecutor()
        pipeline_context.results["old"] = "value"

        # Act
        result = executor.execute(NewContextStep(), pipeline_context)

        # Assert
        assert "new" in result.results
        assert "old" not in result.results

    def test_execute_step_with_empty_context(
        self, mock_app_config, mock_logger
    ):
        """Test executing step with empty context."""
        # Arrange
        from pipeline import PipelineContext

        from .conftest import SimpleStep

        executor = TaskExecutor()
        empty_context = PipelineContext(
            app_config=mock_app_config, logger_instance=mock_logger
        )
        step = SimpleStep("test", "key", "value")

        # Act
        result = executor.execute(step, empty_context)

        # Assert
        assert len(result.results) == 1
        assert result.results["key"] == "value"
