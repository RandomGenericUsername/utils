"""Tests for PipelineContext."""

import copy

from pipeline import PipelineContext, PipelineStep
from task_pipeline.core.types import ProgressTracker


class TestPipelineContext:
    """Test suite for PipelineContext."""

    def test_context_creation_with_app_config(
        self, mock_app_config, mock_logger
    ):
        """Test creating context with app_config."""
        # Arrange & Act
        context = PipelineContext(
            app_config=mock_app_config,
            logger_instance=mock_logger,
        )

        # Assert
        assert context.app_config == mock_app_config
        assert context.app_config.name == "test_app"
        assert context.app_config.version == "1.0.0"

    def test_context_creation_with_logger(self, mock_app_config, mock_logger):
        """Test creating context with logger instance."""
        # Arrange & Act
        context = PipelineContext(
            app_config=mock_app_config,
            logger_instance=mock_logger,
        )

        # Assert
        assert context.logger_instance == mock_logger
        assert hasattr(context.logger_instance, "info")
        assert hasattr(context.logger_instance, "error")

    def test_context_results_dict_default(self, mock_app_config, mock_logger):
        """Test that results dict is initialized as empty."""
        # Arrange & Act
        context = PipelineContext(
            app_config=mock_app_config,
            logger_instance=mock_logger,
        )

        # Assert
        assert isinstance(context.results, dict)
        assert len(context.results) == 0

    def test_context_errors_list_default(self, mock_app_config, mock_logger):
        """Test that errors list is initialized as empty."""
        # Arrange & Act
        context = PipelineContext(
            app_config=mock_app_config,
            logger_instance=mock_logger,
        )

        # Assert
        assert isinstance(context.errors, list)
        assert len(context.errors) == 0

    def test_context_results_can_be_modified(self, pipeline_context):
        """Test that results dict can be modified."""
        # Arrange
        context = pipeline_context

        # Act
        context.results["key1"] = "value1"
        context.results["key2"] = 42
        context.results["key3"] = {"nested": "dict"}

        # Assert
        assert context.results["key1"] == "value1"
        assert context.results["key2"] == 42
        assert context.results["key3"] == {"nested": "dict"}
        assert len(context.results) == 3

    def test_context_errors_can_be_appended(self, pipeline_context):
        """Test that errors list can be appended to."""
        # Arrange
        context = pipeline_context
        error1 = RuntimeError("Error 1")
        error2 = ValueError("Error 2")

        # Act
        context.errors.append(error1)
        context.errors.append(error2)

        # Assert
        assert len(context.errors) == 2
        assert context.errors[0] == error1
        assert context.errors[1] == error2
        assert isinstance(context.errors[0], RuntimeError)
        assert isinstance(context.errors[1], ValueError)

    def test_context_with_custom_app_config(self, mock_logger):
        """Test context with custom app config type."""
        # Arrange
        from dataclasses import dataclass

        @dataclass
        class CustomConfig:
            setting1: str
            setting2: int

        custom_config = CustomConfig(setting1="test", setting2=100)

        # Act
        context = PipelineContext(
            app_config=custom_config,
            logger_instance=mock_logger,
        )

        # Assert
        assert context.app_config.setting1 == "test"
        assert context.app_config.setting2 == 100

    def test_context_results_dict_operations(self, pipeline_context):
        """Test various dict operations on results."""
        # Arrange
        context = pipeline_context

        # Act & Assert - Add items
        context.results["a"] = 1
        assert "a" in context.results

        # Update items
        context.results["a"] = 2
        assert context.results["a"] == 2

        # Delete items
        del context.results["a"]
        assert "a" not in context.results

        # Get with default
        value = context.results.get("nonexistent", "default")
        assert value == "default"

    def test_context_errors_list_operations(self, pipeline_context):
        """Test various list operations on errors."""
        # Arrange
        context = pipeline_context
        errors = [RuntimeError("E1"), ValueError("E2"), TypeError("E3")]

        # Act & Assert - Extend
        context.errors.extend(errors)
        assert len(context.errors) == 3

        # Index access
        assert context.errors[0].args[0] == "E1"
        assert context.errors[1].args[0] == "E2"

        # Slicing
        first_two = context.errors[:2]
        assert len(first_two) == 2

        # Clear
        context.errors.clear()
        assert len(context.errors) == 0

    def test_context_is_mutable(self, pipeline_context):
        """Test that context can be modified and changes persist."""
        # Arrange
        context = pipeline_context
        original_results_id = id(context.results)
        original_errors_id = id(context.errors)

        # Act
        context.results["test"] = "value"
        context.errors.append(RuntimeError("test"))

        # Assert - Same objects, modified in place
        assert id(context.results) == original_results_id
        assert id(context.errors) == original_errors_id
        assert len(context.results) == 1
        assert len(context.errors) == 1

    def test_context_with_prepopulated_results(
        self, mock_app_config, mock_logger
    ):
        """Test creating context with prepopulated results."""
        # Arrange
        initial_results = {"key1": "value1", "key2": 42}

        # Act
        context = PipelineContext(
            app_config=mock_app_config,
            logger_instance=mock_logger,
            results=initial_results,
        )

        # Assert
        assert context.results == initial_results
        assert context.results["key1"] == "value1"
        assert context.results["key2"] == 42

    def test_context_with_prepopulated_errors(
        self, mock_app_config, mock_logger
    ):
        """Test creating context with prepopulated errors."""
        # Arrange
        initial_errors = [RuntimeError("Error 1"), ValueError("Error 2")]

        # Act
        context = PipelineContext(
            app_config=mock_app_config,
            logger_instance=mock_logger,
            errors=initial_errors,
        )

        # Assert
        assert len(context.errors) == 2
        assert context.errors[0].args[0] == "Error 1"
        assert context.errors[1].args[0] == "Error 2"

    def test_context_generic_type_parameter(self, mock_logger):
        """Test that context works with generic type parameter."""
        # Arrange
        from dataclasses import dataclass

        @dataclass
        class SpecificConfig:
            value: str

        config = SpecificConfig(value="test")

        # Act
        context: PipelineContext[SpecificConfig] = PipelineContext(
            app_config=config,
            logger_instance=mock_logger,
        )

        # Assert
        assert context.app_config.value == "test"
        assert isinstance(context.app_config, SpecificConfig)


class TestPipelineContextDeepCopy:
    """Test PipelineContext deep copy functionality."""

    def test_deepcopy_basic_context(self, mock_app_config, mock_logger):
        """Test that context can be deep copied."""
        # Arrange
        context = PipelineContext(
            app_config=mock_app_config,
            logger_instance=mock_logger,
        )
        context.results["key1"] = "value1"
        context.errors.append(RuntimeError("test"))

        # Act
        context_copy = copy.deepcopy(context)

        # Assert
        assert context_copy is not context
        assert context_copy.results is not context.results
        assert context_copy.errors is not context.errors
        assert context_copy.results == context.results
        assert len(context_copy.errors) == len(context.errors)

    def test_deepcopy_with_progress_tracker(
        self, mock_app_config, mock_logger
    ):
        """Test progress tracker is shared (not copied) during deepcopy."""

        class DummyStep(PipelineStep):
            @property
            def step_id(self) -> str:
                return "dummy"

            @property
            def description(self) -> str:
                return "Dummy step"

            def run(self, context):
                return context

        # Arrange
        steps = [DummyStep()]
        tracker = ProgressTracker(steps)

        context = PipelineContext(
            app_config=mock_app_config,
            logger_instance=mock_logger,
        )
        context._progress_tracker = tracker
        context._current_step_id = "dummy"

        # Act
        context_copy = copy.deepcopy(context)

        # Assert - progress tracker should be the SAME instance (shared)
        assert context_copy._progress_tracker is context._progress_tracker
        assert context_copy._current_step_id == context._current_step_id

    def test_deepcopy_progress_tracker_updates_shared(
        self, mock_app_config, mock_logger
    ):
        """Test updates to progress tracker are visible in both contexts."""

        class DummyStep(PipelineStep):
            @property
            def step_id(self) -> str:
                return "dummy"

            @property
            def description(self) -> str:
                return "Dummy step"

            def run(self, context):
                return context

        # Arrange
        steps = [DummyStep()]
        tracker = ProgressTracker(steps)

        context = PipelineContext(
            app_config=mock_app_config,
            logger_instance=mock_logger,
        )
        context._progress_tracker = tracker
        context._current_step_id = "dummy"

        # Act
        context_copy = copy.deepcopy(context)

        # Update progress via original context
        context._progress_tracker.update_step_progress("dummy", 50.0)

        # Assert - change should be visible in both
        assert context._progress_tracker.get_overall_progress() == 50.0
        assert context_copy._progress_tracker.get_overall_progress() == 50.0

    def test_deepcopy_results_isolation(self, mock_app_config, mock_logger):
        """Test that results are isolated after deepcopy."""
        # Arrange
        context = PipelineContext(
            app_config=mock_app_config,
            logger_instance=mock_logger,
        )
        context.results["key1"] = "value1"

        # Act
        context_copy = copy.deepcopy(context)
        context_copy.results["key2"] = "value2"

        # Assert - changes to copy don't affect original
        assert "key2" in context_copy.results
        assert "key2" not in context.results
        assert context.results == {"key1": "value1"}
        assert context_copy.results == {"key1": "value1", "key2": "value2"}

    def test_deepcopy_errors_isolation(self, mock_app_config, mock_logger):
        """Test that errors are isolated after deepcopy."""
        # Arrange
        context = PipelineContext(
            app_config=mock_app_config,
            logger_instance=mock_logger,
        )
        context.errors.append(RuntimeError("error1"))

        # Act
        context_copy = copy.deepcopy(context)
        context_copy.errors.append(ValueError("error2"))

        # Assert - changes to copy don't affect original
        assert len(context.errors) == 1
        assert len(context_copy.errors) == 2
        assert isinstance(context.errors[0], RuntimeError)
        assert isinstance(context_copy.errors[1], ValueError)
