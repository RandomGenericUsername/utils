"""Integration tests for advanced scenarios.

Tests parallel timeout, context isolation, and mixed execution patterns.

Evidence Anchors:
- Parallel timeout: executors/parallel_executor.py:108
- Context deep copy: parallel_executor.py:91
- Mixed execution: executors/pipeline_executor.py:17-48
"""

import pytest
from concurrent.futures import TimeoutError

from task_pipeline import (
    Pipeline,
    PipelineConfig,
    ParallelConfig,
    LogicOperator,
)


class TestParallelTimeout:
    """Integration tests for parallel group timeout."""

    def test_parallel_group_timeout_enforced(self, pipeline_context):
        """INTEGRATION: Parallel group timeout is enforced."""
        # Arrange
        from tests.conftest import SlowStep

        parallel_steps = [
            SlowStep("slow1", 0.5),  # Takes 500ms
            SlowStep("slow2", 0.5),  # Takes 500ms
        ]
        config = ParallelConfig(
            operator=LogicOperator.AND,
            timeout=0.2,  # Timeout after 200ms
        )
        pipeline_config = PipelineConfig(parallel_config=config)
        pipeline = Pipeline(steps=[parallel_steps], config=pipeline_config)

        # Act & Assert - Timeout occurs
        with pytest.raises(TimeoutError):
            pipeline.run(pipeline_context)

    def test_parallel_group_completes_within_timeout(self, pipeline_context):
        """INTEGRATION: Parallel group completes when within timeout."""
        # Arrange
        from tests.conftest import SlowStep

        parallel_steps = [
            SlowStep("slow1", 0.05),  # Takes 50ms
            SlowStep("slow2", 0.05),  # Takes 50ms
        ]
        config = ParallelConfig(
            operator=LogicOperator.AND,
            timeout=0.5,  # Timeout after 500ms (plenty of time)
        )
        pipeline_config = PipelineConfig(parallel_config=config)
        pipeline = Pipeline(steps=[parallel_steps], config=pipeline_config)

        # Act
        result = pipeline.run(pipeline_context)

        # Assert - Completed successfully
        assert "slow1_completed" in result.results
        assert "slow2_completed" in result.results


class TestContextIsolation:
    """Integration tests for context isolation in parallel execution."""

    def test_parallel_steps_have_isolated_contexts(self, pipeline_context):
        """INTEGRATION: Parallel steps operate on isolated context copies."""
        # Arrange
        from tests.conftest import CounterStep

        # Pre-populate context with a counter
        pipeline_context.results["counter"] = 0

        parallel_steps = [
            CounterStep("step1", "counter"),  # Each increments from 0
            CounterStep("step2", "counter"),  # Each increments from 0
            CounterStep("step3", "counter"),  # Each increments from 0
        ]
        config = ParallelConfig(operator=LogicOperator.AND)
        pipeline_config = PipelineConfig(parallel_config=config)
        pipeline = Pipeline(steps=[parallel_steps], config=pipeline_config)

        # Act
        result = pipeline.run(pipeline_context)

        # Assert - Each step saw initial value 0, incremented to 1
        # After merging, numeric values are summed: 1 + 1 + 1 = 3
        assert result.results["counter"] == 3


class TestMixedExecutionPatterns:
    """Integration tests for mixed serial and parallel execution."""

    def test_serial_then_parallel_then_serial(self, pipeline_context):
        """INTEGRATION: Serial -> Parallel -> Serial execution pattern."""
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
        pipeline = Pipeline(steps=steps)

        # Act
        result = pipeline.run(pipeline_context)

        # Assert - All steps executed
        assert "key1" in result.results
        assert "key2" in result.results
        assert "key3" in result.results
        assert "key4" in result.results

    def test_multiple_parallel_groups_in_sequence(self, pipeline_context):
        """INTEGRATION: Multiple parallel groups execute in sequence."""
        # Arrange
        from tests.conftest import SimpleStep

        steps = [
            [
                SimpleStep("group1_step1", "g1k1", "g1v1"),
                SimpleStep("group1_step2", "g1k2", "g1v2"),
            ],
            [
                SimpleStep("group2_step1", "g2k1", "g2v1"),
                SimpleStep("group2_step2", "g2k2", "g2v2"),
            ],
        ]
        pipeline = Pipeline(steps=steps)

        # Act
        result = pipeline.run(pipeline_context)

        # Assert - All parallel groups executed
        assert "g1k1" in result.results
        assert "g1k2" in result.results
        assert "g2k1" in result.results
        assert "g2k2" in result.results

    def test_nested_parallel_not_supported_but_sequential_works(
        self, pipeline_context
    ):
        """INTEGRATION: Parallel groups execute sequentially (no nesting)."""
        # Arrange
        from tests.conftest import SimpleStep, CounterStep

        # This creates two sequential parallel groups, not nested parallelism
        steps = [
            CounterStep("init", "counter"),  # counter = 1
            [
                SimpleStep("parallel1", "key1", "value1"),
                SimpleStep("parallel2", "key2", "value2"),
            ],
            CounterStep("final", "counter"),  # counter = 2
        ]
        pipeline = Pipeline(steps=steps)

        # Act
        result = pipeline.run(pipeline_context)

        # Assert - Sequential execution of parallel groups
        assert result.results["counter"] == 2
        assert "key1" in result.results
        assert "key2" in result.results


class TestThreadSafety:
    """Integration tests for thread-safe parallel execution."""

    def test_parallel_execution_is_thread_safe(self, pipeline_context):
        """INTEGRATION: Parallel execution handles updates safely."""
        # Arrange
        from tests.conftest import CounterStep

        # Create many parallel steps to stress test thread safety
        parallel_steps = [
            CounterStep(f"step{i}", "counter") for i in range(10)
        ]
        config = ParallelConfig(operator=LogicOperator.AND, max_workers=5)
        pipeline_config = PipelineConfig(parallel_config=config)
        pipeline = Pipeline(steps=[parallel_steps], config=pipeline_config)

        # Act
        result = pipeline.run(pipeline_context)

        # Assert - All increments counted (10 steps, each increments by 1)
        assert result.results["counter"] == 10
