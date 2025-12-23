"""Contract tests for PipelineStep interface.

Evidence Anchors:
- PipelineStep ABC: pipeline/src/task_pipeline/core/types.py:85-128
- Required properties: step_id (L88-92), description (L94-98)
- Required method: run() (L100-111)
- Optional properties: timeout (L114-117), retries (L119-122), critical (L124-127)

Contract Guarantees:
1. PipelineStep is an abstract base class (cannot instantiate directly)
2. Subclasses must implement: step_id, description, run()
3. Optional properties have defaults: timeout=None, retries=0, critical=True
4. run() receives PipelineContext and returns PipelineContext
5. step_id returns str
6. description returns str
"""

import pytest
from abc import ABC
from typing import Any

from task_pipeline import PipelineStep, PipelineContext


class TestPipelineStepAbstractContract:
    """Test PipelineStep abstract base class contract."""

    def test_pipelinestep_is_abstract_base_class(self):
        """CONTRACT: PipelineStep is an ABC and cannot be instantiated."""
        # Assert
        assert issubclass(PipelineStep, ABC)

    def test_pipelinestep_cannot_be_instantiated_directly(self):
        """CONTRACT: Cannot instantiate PipelineStep without implementing abstract methods."""
        # Act & Assert
        with pytest.raises(TypeError):
            # This should raise TypeError because abstract methods not implemented
            PipelineStep()  # type: ignore

    def test_pipelinestep_requires_step_id_implementation(self):
        """CONTRACT: Subclass must implement step_id property."""

        # Arrange - Missing step_id
        class IncompleteStep(PipelineStep):
            @property
            def description(self) -> str:
                return "test"

            def run(self, context: PipelineContext[Any]) -> PipelineContext[Any]:
                return context

        # Act & Assert
        with pytest.raises(TypeError):
            IncompleteStep()  # type: ignore

    def test_pipelinestep_requires_description_implementation(self):
        """CONTRACT: Subclass must implement description property."""

        # Arrange - Missing description
        class IncompleteStep(PipelineStep):
            @property
            def step_id(self) -> str:
                return "test"

            def run(self, context: PipelineContext[Any]) -> PipelineContext[Any]:
                return context

        # Act & Assert
        with pytest.raises(TypeError):
            IncompleteStep()  # type: ignore

    def test_pipelinestep_requires_run_implementation(self):
        """CONTRACT: Subclass must implement run() method."""

        # Arrange - Missing run()
        class IncompleteStep(PipelineStep):
            @property
            def step_id(self) -> str:
                return "test"

            @property
            def description(self) -> str:
                return "test"

        # Act & Assert
        with pytest.raises(TypeError):
            IncompleteStep()  # type: ignore


class TestPipelineStepRequiredPropertiesContract:
    """Test required property contracts."""

    def test_step_id_returns_string(self):
        """CONTRACT: step_id property returns str."""
        # Arrange
        from tests.conftest import SimpleStep

        step = SimpleStep("test_id", "key", "value")

        # Act
        result = step.step_id

        # Assert
        assert isinstance(result, str)
        assert result == "test_id"

    def test_description_returns_string(self):
        """CONTRACT: description property returns str."""
        # Arrange
        from tests.conftest import SimpleStep

        step = SimpleStep("test_id", "key", "value")

        # Act
        result = step.description

        # Assert
        assert isinstance(result, str)
        assert len(result) > 0  # Should be non-empty

    def test_run_accepts_pipeline_context(self, pipeline_context):
        """CONTRACT: run() method accepts PipelineContext."""
        # Arrange
        from tests.conftest import SimpleStep

        step = SimpleStep("test_id", "key", "value")

        # Act - Should not raise
        result = step.run(pipeline_context)

        # Assert
        assert result is not None

    def test_run_returns_pipeline_context(self, pipeline_context):
        """CONTRACT: run() method returns PipelineContext."""
        # Arrange
        from tests.conftest import SimpleStep

        step = SimpleStep("test_id", "key", "value")

        # Act
        result = step.run(pipeline_context)

        # Assert
        assert isinstance(result, PipelineContext)


class TestPipelineStepOptionalPropertiesContract:
    """Test optional property default values contract."""

    def test_timeout_default_is_none(self):
        """CONTRACT: timeout property defaults to None."""
        # Arrange
        from tests.conftest import SimpleStep

        step = SimpleStep("test_id", "key", "value")

        # Act
        result = step.timeout

        # Assert
        assert result is None

    def test_retries_default_is_zero(self):
        """CONTRACT: retries property defaults to 0."""
        # Arrange
        from tests.conftest import SimpleStep

        step = SimpleStep("test_id", "key", "value")

        # Act
        result = step.retries

        # Assert
        assert result == 0
        assert isinstance(result, int)

    def test_critical_default_is_true(self):
        """CONTRACT: critical property defaults to True."""
        # Arrange
        from tests.conftest import SimpleStep

        step = SimpleStep("test_id", "key", "value")

        # Act
        result = step.critical

        # Assert
        assert result is True
        assert isinstance(result, bool)


class TestPipelineStepOptionalPropertiesOverrideContract:
    """Test that optional properties can be overridden."""

    def test_timeout_can_be_overridden(self):
        """CONTRACT: timeout property can be overridden in subclass."""

        # Arrange
        class CustomTimeoutStep(PipelineStep):
            @property
            def step_id(self) -> str:
                return "custom"

            @property
            def description(self) -> str:
                return "Custom timeout step"

            @property
            def timeout(self) -> float | None:
                return 30.0

            def run(
                self, context: PipelineContext[Any]
            ) -> PipelineContext[Any]:
                return context

        step = CustomTimeoutStep()

        # Act
        result = step.timeout

        # Assert
        assert result == 30.0

    def test_retries_can_be_overridden(self):
        """CONTRACT: retries property can be overridden in subclass."""

        # Arrange
        class CustomRetriesStep(PipelineStep):
            @property
            def step_id(self) -> str:
                return "custom"

            @property
            def description(self) -> str:
                return "Custom retries step"

            @property
            def retries(self) -> int:
                return 3

            def run(
                self, context: PipelineContext[Any]
            ) -> PipelineContext[Any]:
                return context

        step = CustomRetriesStep()

        # Act
        result = step.retries

        # Assert
        assert result == 3

    def test_critical_can_be_overridden(self):
        """CONTRACT: critical property can be overridden in subclass."""

        # Arrange
        class NonCriticalStep(PipelineStep):
            @property
            def step_id(self) -> str:
                return "custom"

            @property
            def description(self) -> str:
                return "Non-critical step"

            @property
            def critical(self) -> bool:
                return False

            def run(
                self, context: PipelineContext[Any]
            ) -> PipelineContext[Any]:
                return context

        step = NonCriticalStep()

        # Act
        result = step.critical

        # Assert
        assert result is False


class TestPipelineStepCompleteImplementationContract:
    """Test that complete implementation works correctly."""

    def test_complete_implementation_can_be_instantiated(self):
        """CONTRACT: Complete implementation can be instantiated."""
        # Arrange
        from tests.conftest import SimpleStep

        # Act
        step = SimpleStep("test_id", "key", "value")

        # Assert
        assert step is not None
        assert isinstance(step, PipelineStep)

    def test_complete_implementation_is_functional(self, pipeline_context):
        """CONTRACT: Complete implementation is functional."""
        # Arrange
        from tests.conftest import SimpleStep

        step = SimpleStep("test_id", "test_key", "test_value")

        # Act
        result = step.run(pipeline_context)

        # Assert
        assert isinstance(result, PipelineContext)
        assert "test_key" in result.results
        assert result.results["test_key"] == "test_value"
