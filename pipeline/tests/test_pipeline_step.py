"""Tests for PipelineStep abstract base class."""

from typing import Any

import pytest

from pipeline import PipelineContext, PipelineStep


class TestPipelineStepInterface:
    """Test suite for PipelineStep abstract interface."""

    def test_cannot_instantiate_abstract_class(self):
        """Test that PipelineStep cannot be instantiated directly."""
        # Act & Assert
        with pytest.raises(TypeError):
            PipelineStep()  # type: ignore

    def test_concrete_step_must_implement_step_id(self, pipeline_context):
        """Test that concrete step must implement step_id property."""

        # Arrange
        class IncompleteStep(PipelineStep):
            @property
            def description(self) -> str:
                return "Test"

            def run(
                self, context: PipelineContext[Any]
            ) -> PipelineContext[Any]:
                return context

        # Act & Assert
        with pytest.raises(TypeError):
            IncompleteStep()  # type: ignore

    def test_concrete_step_must_implement_description(self, pipeline_context):
        """Test that concrete step must implement description property."""

        # Arrange
        class IncompleteStep(PipelineStep):
            @property
            def step_id(self) -> str:
                return "test"

            def run(
                self, context: PipelineContext[Any]
            ) -> PipelineContext[Any]:
                return context

        # Act & Assert
        with pytest.raises(TypeError):
            IncompleteStep()  # type: ignore

    def test_concrete_step_must_implement_run(self):
        """Test that concrete step must implement run method."""

        # Arrange
        class IncompleteStep(PipelineStep):
            @property
            def step_id(self) -> str:
                return "test"

            @property
            def description(self) -> str:
                return "Test"

        # Act & Assert
        with pytest.raises(TypeError):
            IncompleteStep()  # type: ignore

    def test_complete_step_can_be_instantiated(self):
        """Test that complete step implementation can be instantiated."""

        # Arrange
        class CompleteStep(PipelineStep):
            @property
            def step_id(self) -> str:
                return "complete_step"

            @property
            def description(self) -> str:
                return "A complete step"

            def run(
                self, context: PipelineContext[Any]
            ) -> PipelineContext[Any]:
                return context

        # Act
        step = CompleteStep()

        # Assert
        assert step.step_id == "complete_step"
        assert step.description == "A complete step"


class TestPipelineStepProperties:
    """Test suite for PipelineStep properties."""

    def test_step_id_property(self, simple_step):
        """Test step_id property."""
        # Assert
        assert simple_step.step_id == "simple_step"
        assert isinstance(simple_step.step_id, str)

    def test_description_property(self, simple_step):
        """Test description property."""
        # Assert
        assert simple_step.description == "Simple step: simple_step"
        assert isinstance(simple_step.description, str)

    def test_timeout_property_default(self, simple_step):
        """Test timeout property default value."""
        # Assert
        assert simple_step.timeout is None

    def test_retries_property_default(self, simple_step):
        """Test retries property default value."""
        # Assert
        assert simple_step.retries == 0
        assert isinstance(simple_step.retries, int)

    def test_critical_property_default(self, simple_step):
        """Test critical property default value."""
        # Assert
        assert simple_step.critical is True
        assert isinstance(simple_step.critical, bool)

    def test_custom_timeout_property(self):
        """Test step with custom timeout."""

        # Arrange
        class TimeoutStep(PipelineStep):
            @property
            def step_id(self) -> str:
                return "timeout_step"

            @property
            def description(self) -> str:
                return "Step with timeout"

            @property
            def timeout(self) -> float | None:
                return 5.0

            def run(
                self, context: PipelineContext[Any]
            ) -> PipelineContext[Any]:
                return context

        # Act
        step = TimeoutStep()

        # Assert
        assert step.timeout == 5.0

    def test_custom_retries_property(self):
        """Test step with custom retries."""

        # Arrange
        class RetryStep(PipelineStep):
            @property
            def step_id(self) -> str:
                return "retry_step"

            @property
            def description(self) -> str:
                return "Step with retries"

            @property
            def retries(self) -> int:
                return 3

            def run(
                self, context: PipelineContext[Any]
            ) -> PipelineContext[Any]:
                return context

        # Act
        step = RetryStep()

        # Assert
        assert step.retries == 3

    def test_custom_critical_property(self, non_critical_failing_step):
        """Test step with custom critical property."""
        # Assert
        assert non_critical_failing_step.critical is False

    def test_all_custom_properties(self):
        """Test step with all custom properties."""

        # Arrange
        class CustomStep(PipelineStep):
            @property
            def step_id(self) -> str:
                return "custom_step"

            @property
            def description(self) -> str:
                return "Fully customized step"

            @property
            def timeout(self) -> float | None:
                return 10.0

            @property
            def retries(self) -> int:
                return 5

            @property
            def critical(self) -> bool:
                return False

            def run(
                self, context: PipelineContext[Any]
            ) -> PipelineContext[Any]:
                return context

        # Act
        step = CustomStep()

        # Assert
        assert step.step_id == "custom_step"
        assert step.description == "Fully customized step"
        assert step.timeout == 10.0
        assert step.retries == 5
        assert step.critical is False


class TestPipelineStepRun:
    """Test suite for PipelineStep run method."""

    def test_run_method_receives_context(self, simple_step, pipeline_context):
        """Test that run method receives context."""
        # Act
        result = simple_step.run(pipeline_context)

        # Assert
        assert result is not None
        assert isinstance(result, PipelineContext)

    def test_run_method_returns_context(self, simple_step, pipeline_context):
        """Test that run method returns context."""
        # Act
        result = simple_step.run(pipeline_context)

        # Assert
        assert result == pipeline_context

    def test_run_method_can_modify_context(
        self, simple_step, pipeline_context
    ):
        """Test that run method can modify context."""
        # Arrange
        assert "test_key" not in pipeline_context.results

        # Act
        result = simple_step.run(pipeline_context)

        # Assert
        assert "test_key" in result.results
        assert result.results["test_key"] == "test_value"

    def test_run_method_can_add_multiple_results(self, pipeline_context):
        """Test that run method can add multiple results."""

        # Arrange
        class MultiResultStep(PipelineStep):
            @property
            def step_id(self) -> str:
                return "multi_result"

            @property
            def description(self) -> str:
                return "Multi result step"

            def run(
                self, context: PipelineContext[Any]
            ) -> PipelineContext[Any]:
                context.results["key1"] = "value1"
                context.results["key2"] = "value2"
                context.results["key3"] = "value3"
                return context

        step = MultiResultStep()

        # Act
        result = step.run(pipeline_context)

        # Assert
        assert len(result.results) == 3
        assert result.results["key1"] == "value1"
        assert result.results["key2"] == "value2"
        assert result.results["key3"] == "value3"

    def test_run_method_can_access_app_config(self, pipeline_context):
        """Test that run method can access app_config."""

        # Arrange
        class ConfigAccessStep(PipelineStep):
            @property
            def step_id(self) -> str:
                return "config_access"

            @property
            def description(self) -> str:
                return "Config access step"

            def run(
                self, context: PipelineContext[Any]
            ) -> PipelineContext[Any]:
                context.results["app_name"] = context.app_config.name
                context.results["app_version"] = context.app_config.version
                return context

        step = ConfigAccessStep()

        # Act
        result = step.run(pipeline_context)

        # Assert
        assert result.results["app_name"] == "test_app"
        assert result.results["app_version"] == "1.0.0"

    def test_run_method_can_use_logger(self, pipeline_context):
        """Test that run method can use logger."""

        # Arrange
        class LoggingStep(PipelineStep):
            @property
            def step_id(self) -> str:
                return "logging_step"

            @property
            def description(self) -> str:
                return "Logging step"

            def run(
                self, context: PipelineContext[Any]
            ) -> PipelineContext[Any]:
                context.logger_instance.info("Test message")
                context.results["logged"] = True
                return context

        step = LoggingStep()

        # Act
        result = step.run(pipeline_context)

        # Assert
        assert result.results["logged"] is True
        pipeline_context.logger_instance.info.assert_called_once_with(
            "Test message"
        )

    def test_run_method_can_raise_exception(
        self, failing_step, pipeline_context
    ):
        """Test that run method can raise exceptions."""
        # Act & Assert
        with pytest.raises(RuntimeError) as exc_info:
            failing_step.run(pipeline_context)

        assert str(exc_info.value) == "Test error"
