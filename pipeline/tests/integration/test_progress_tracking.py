"""Integration tests for progress tracking with callbacks.

Tests progress callback invocation and weighted progress calculation.

Evidence Anchors:
- Progress tracking: pipeline/src/task_pipeline/core/types.py:154-252
- Callback invocation: pipeline/src/task_pipeline/pipeline.py:97-105
- Weight calculation: types.py:189-210
"""

from unittest.mock import MagicMock

from task_pipeline import Pipeline, PipelineConfig


class TestProgressCallbacks:
    """Integration tests for progress callback functionality."""

    def test_progress_callback_invoked_for_each_step(self, pipeline_context):
        """INTEGRATION: Progress callback invoked after each step completes."""
        # Arrange
        from tests.conftest import SimpleStep

        steps = [
            SimpleStep("step1", "key1", "value1"),
            SimpleStep("step2", "key2", "value2"),
            SimpleStep("step3", "key3", "value3"),
        ]
        callback = MagicMock()
        pipeline = Pipeline(steps=steps, progress_callback=callback)

        # Act
        pipeline.run(pipeline_context)

        # Assert - Callback invoked for each step
        assert callback.call_count >= 3  # At least once per step

    def test_progress_callback_receives_increasing_progress(
        self, pipeline_context
    ):
        """INTEGRATION: Progress callback receives increasing progress values."""
        # Arrange
        from tests.conftest import SimpleStep

        steps = [
            SimpleStep("step1", "key1", "value1"),
            SimpleStep("step2", "key2", "value2"),
            SimpleStep("step3", "key3", "value3"),
        ]
        progress_values = []

        def track_progress(step_idx, total, name, progress):
            progress_values.append(progress)

        pipeline = Pipeline(steps=steps, progress_callback=track_progress)

        # Act
        pipeline.run(pipeline_context)

        # Assert - Progress increases monotonically
        assert len(progress_values) > 0
        for i in range(1, len(progress_values)):
            assert progress_values[i] >= progress_values[i - 1]

    def test_progress_callback_reaches_100_percent(self, pipeline_context):
        """INTEGRATION: Progress callback reaches 100% at completion."""
        # Arrange
        from tests.conftest import SimpleStep

        steps = [
            SimpleStep("step1", "key1", "value1"),
            SimpleStep("step2", "key2", "value2"),
        ]
        progress_values = []

        def track_progress(step_idx, total, name, progress):
            progress_values.append(progress)

        pipeline = Pipeline(steps=steps, progress_callback=track_progress)

        # Act
        pipeline.run(pipeline_context)

        # Assert - Final progress is 100%
        assert len(progress_values) > 0
        assert progress_values[-1] == 100.0

    def test_progress_callback_with_parallel_steps(self, pipeline_context):
        """INTEGRATION: Progress tracking works with parallel steps."""
        # Arrange
        from tests.conftest import SimpleStep

        parallel_steps = [
            SimpleStep("parallel1", "key1", "value1"),
            SimpleStep("parallel2", "key2", "value2"),
            SimpleStep("parallel3", "key3", "value3"),
        ]
        progress_values = []

        def track_progress(step_idx, total, name, progress):
            progress_values.append(progress)

        pipeline = Pipeline(steps=[parallel_steps], progress_callback=track_progress)

        # Act
        pipeline.run(pipeline_context)

        # Assert - Progress tracked for parallel group
        assert len(progress_values) > 0
        assert progress_values[-1] == 100.0


class TestProgressWithoutCallback:
    """Integration tests for progress tracking without callback."""

    def test_pipeline_works_without_progress_callback(self, pipeline_context):
        """INTEGRATION: Pipeline works normally without progress callback."""
        # Arrange
        from tests.conftest import SimpleStep

        steps = [
            SimpleStep("step1", "key1", "value1"),
            SimpleStep("step2", "key2", "value2"),
        ]
        pipeline = Pipeline(steps=steps, progress_callback=None)

        # Act
        result = pipeline.run(pipeline_context)

        # Assert - Pipeline completes successfully
        assert "key1" in result.results
        assert "key2" in result.results

    def test_pipeline_with_none_callback_explicit(self, pipeline_context):
        """INTEGRATION: Explicitly passing None for callback works."""
        # Arrange
        from tests.conftest import SimpleStep

        steps = [SimpleStep("step1", "key1", "value1")]
        config = PipelineConfig(fail_fast=True)
        pipeline = Pipeline(steps=steps, config=config, progress_callback=None)

        # Act
        result = pipeline.run(pipeline_context)

        # Assert - Works without callback
        assert "key1" in result.results


class TestProgressWithMixedSteps:
    """Integration tests for progress with mixed serial and parallel steps."""

    def test_progress_with_mixed_serial_and_parallel(self, pipeline_context):
        """INTEGRATION: Progress tracking with mixed serial and parallel steps."""
        # Arrange
        from tests.conftest import SimpleStep

        steps = [
            SimpleStep("serial1", "key1", "value1"),
            [
                SimpleStep("parallel1", "key2", "value2"),
                SimpleStep("parallel2", "key3", "value3"),
            ],
            SimpleStep("serial2", "key4", "value4"),
        ]
        progress_values = []

        def track_progress(step_idx, total, name, progress):
            progress_values.append(progress)

        pipeline = Pipeline(steps=steps, progress_callback=track_progress)

        # Act
        pipeline.run(pipeline_context)

        # Assert - Progress tracked through mixed execution
        assert len(progress_values) > 0
        assert progress_values[-1] == 100.0
        # Progress should increase monotonically
        for i in range(1, len(progress_values)):
            assert progress_values[i] >= progress_values[i - 1]
