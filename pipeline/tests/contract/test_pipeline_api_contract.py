"""Contract tests for Pipeline class public API.

Evidence Anchors:
- Pipeline class: pipeline/src/task_pipeline/pipeline.py:17-224
- Pipeline.__init__: pipeline/src/task_pipeline/pipeline.py:25-73
- Pipeline.run: pipeline/src/task_pipeline/pipeline.py:75-106
- Pipeline.create: pipeline/src/task_pipeline/pipeline.py:210-224

Contract Guarantees:
1. Pipeline accepts list of TaskStep (PipelineStep or list[PipelineStep])
2. Pipeline accepts optional PipelineConfig (defaults if None)
3. Pipeline accepts optional progress_callback (Callable[[float], None])
4. Pipeline.run() accepts PipelineContext and returns PipelineContext
5. Pipeline.create() factory method works identically to __init__
"""

import pytest
from typing import Any
from unittest.mock import MagicMock

from task_pipeline import Pipeline, PipelineStep, PipelineContext, PipelineConfig
from task_pipeline.core.types import TaskStep


class TestPipelineInitializationContract:
    """Test Pipeline.__init__() contract guarantees."""

    def test_pipeline_accepts_empty_steps_list(
        self, pipeline_context, mock_logger
    ):
        """CONTRACT: Pipeline accepts empty list of steps."""
        # Arrange & Act
        pipeline = Pipeline(steps=[])

        # Assert - Should not raise
        assert pipeline is not None
        assert isinstance(pipeline, Pipeline)

    def test_pipeline_accepts_single_step(self, pipeline_context):
        """CONTRACT: Pipeline accepts single PipelineStep in list."""
        # Arrange
        from tests.conftest import SimpleStep

        step = SimpleStep("step1", "key", "value")

        # Act
        pipeline = Pipeline(steps=[step])

        # Assert
        assert pipeline is not None
        assert isinstance(pipeline, Pipeline)

    def test_pipeline_accepts_multiple_serial_steps(self, pipeline_context):
        """CONTRACT: Pipeline accepts multiple serial steps."""
        # Arrange
        from tests.conftest import SimpleStep

        steps = [
            SimpleStep("step1", "key1", "value1"),
            SimpleStep("step2", "key2", "value2"),
            SimpleStep("step3", "key3", "value3"),
        ]

        # Act
        pipeline = Pipeline(steps=steps)

        # Assert
        assert pipeline is not None

    def test_pipeline_accepts_parallel_step_group(self, pipeline_context):
        """CONTRACT: Pipeline accepts list[PipelineStep] for parallel execution."""
        # Arrange
        from tests.conftest import SimpleStep

        parallel_group = [
            SimpleStep("parallel1", "key1", "value1"),
            SimpleStep("parallel2", "key2", "value2"),
        ]
        steps: list[TaskStep] = [parallel_group]

        # Act
        pipeline = Pipeline(steps=steps)

        # Assert
        assert pipeline is not None

    def test_pipeline_accepts_mixed_serial_and_parallel_steps(
        self, pipeline_context
    ):
        """CONTRACT: Pipeline accepts mix of serial steps and parallel groups."""
        # Arrange
        from tests.conftest import SimpleStep

        steps: list[TaskStep] = [
            SimpleStep("serial1", "key1", "value1"),
            [
                SimpleStep("parallel1", "key2", "value2"),
                SimpleStep("parallel2", "key3", "value3"),
            ],
            SimpleStep("serial2", "key4", "value4"),
        ]

        # Act
        pipeline = Pipeline(steps=steps)

        # Assert
        assert pipeline is not None

    def test_pipeline_accepts_none_config_uses_defaults(self):
        """CONTRACT: Pipeline accepts None for config, uses defaults."""
        # Arrange
        from tests.conftest import SimpleStep

        steps = [SimpleStep("step1", "key", "value")]

        # Act
        pipeline = Pipeline(steps=steps, config=None)

        # Assert
        assert pipeline is not None
        # Default config should be created internally

    def test_pipeline_accepts_custom_config(self):
        """CONTRACT: Pipeline accepts custom PipelineConfig."""
        # Arrange
        from tests.conftest import SimpleStep

        steps = [SimpleStep("step1", "key", "value")]
        config = PipelineConfig(fail_fast=False)

        # Act
        pipeline = Pipeline(steps=steps, config=config)

        # Assert
        assert pipeline is not None

    def test_pipeline_accepts_none_progress_callback(self):
        """CONTRACT: Pipeline accepts None for progress_callback."""
        # Arrange
        from tests.conftest import SimpleStep

        steps = [SimpleStep("step1", "key", "value")]

        # Act
        pipeline = Pipeline(steps=steps, progress_callback=None)

        # Assert
        assert pipeline is not None

    def test_pipeline_accepts_progress_callback_function(self):
        """CONTRACT: Pipeline accepts Callable[[float], None] for progress_callback."""
        # Arrange
        from tests.conftest import SimpleStep

        steps = [SimpleStep("step1", "key", "value")]
        callback = MagicMock()

        # Act
        pipeline = Pipeline(steps=steps, progress_callback=callback)

        # Assert
        assert pipeline is not None


class TestPipelineRunContract:
    """Test Pipeline.run() contract guarantees."""

    def test_run_accepts_pipeline_context(self, pipeline_context):
        """CONTRACT: Pipeline.run() accepts PipelineContext."""
        # Arrange
        from tests.conftest import SimpleStep

        pipeline = Pipeline(steps=[SimpleStep("step1", "key", "value")])

        # Act
        result = pipeline.run(pipeline_context)

        # Assert - Should not raise
        assert result is not None

    def test_run_returns_pipeline_context(self, pipeline_context):
        """CONTRACT: Pipeline.run() returns PipelineContext."""
        # Arrange
        from tests.conftest import SimpleStep

        pipeline = Pipeline(steps=[SimpleStep("step1", "key", "value")])

        # Act
        result = pipeline.run(pipeline_context)

        # Assert
        assert isinstance(result, PipelineContext)

    def test_run_returns_modified_context_with_results(self, pipeline_context):
        """CONTRACT: Pipeline.run() returns context with step results."""
        # Arrange
        from tests.conftest import SimpleStep

        step = SimpleStep("step1", "test_key", "test_value")
        pipeline = Pipeline(steps=[step])

        # Act
        result = pipeline.run(pipeline_context)

        # Assert
        assert "test_key" in result.results
        assert result.results["test_key"] == "test_value"

    def test_run_preserves_original_context_fields(self, pipeline_context):
        """CONTRACT: Pipeline.run() preserves context fields."""
        # Arrange
        from tests.conftest import SimpleStep

        pipeline = Pipeline(steps=[SimpleStep("step1", "key", "value")])
        original_app_config = pipeline_context.app_config
        original_logger = pipeline_context.logger_instance

        # Act
        result = pipeline.run(pipeline_context)

        # Assert
        assert result.app_config is original_app_config
        assert result.logger_instance is original_logger


class TestPipelineCreateFactoryContract:
    """Test Pipeline.create() factory method contract."""

    def test_create_factory_method_exists(self):
        """CONTRACT: Pipeline.create() factory method exists."""
        # Assert
        assert hasattr(Pipeline, "create")
        assert callable(Pipeline.create)

    def test_create_accepts_steps_and_config(self, pipeline_context):
        """CONTRACT: Pipeline.create() accepts steps and config parameters."""
        # Arrange
        from tests.conftest import SimpleStep

        steps = [SimpleStep("step1", "key", "value")]
        config = PipelineConfig(fail_fast=True)

        # Act
        pipeline = Pipeline.create(steps=steps, config=config)

        # Assert
        assert pipeline is not None
        assert isinstance(pipeline, Pipeline)

    def test_create_returns_pipeline_instance(self):
        """CONTRACT: Pipeline.create() returns Pipeline instance."""
        # Arrange
        from tests.conftest import SimpleStep

        steps = [SimpleStep("step1", "key", "value")]

        # Act
        pipeline = Pipeline.create(steps=steps)

        # Assert
        assert isinstance(pipeline, Pipeline)

    def test_create_pipeline_is_functional(self, pipeline_context):
        """CONTRACT: Pipeline created with .create() is fully functional."""
        # Arrange
        from tests.conftest import SimpleStep

        pipeline = Pipeline.create(steps=[SimpleStep("step1", "key", "value")])

        # Act
        result = pipeline.run(pipeline_context)

        # Assert
        assert isinstance(result, PipelineContext)
        assert "key" in result.results
