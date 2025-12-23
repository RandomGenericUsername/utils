"""Integration tests for context merging in parallel execution.

Tests type-specific merging logic for lists, numeric values, dicts, and other types.

Evidence Anchors:
- Context merging: pipeline/src/task_pipeline/executors/parallel_executor.py:131-235
- List merging: parallel_executor.py:171-193
- Numeric merging: parallel_executor.py:195-208
- Dict merging: parallel_executor.py:209-218
- Other types: parallel_executor.py:221
- Error merging: parallel_executor.py:224-233
"""

from typing import Any

from task_pipeline import (
    Pipeline,
    PipelineStep,
    PipelineContext,
    PipelineConfig,
    ParallelConfig,
    LogicOperator,
)


class ListAppendStep(PipelineStep):
    """Step that appends items to a list in results."""

    def __init__(self, step_id: str, key: str, items: list[Any]):
        self._step_id = step_id
        self._key = key
        self._items = items

    @property
    def step_id(self) -> str:
        return self._step_id

    @property
    def description(self) -> str:
        return f"Append {self._items} to {self._key}"

    def run(self, context: PipelineContext[Any]) -> PipelineContext[Any]:
        if self._key not in context.results:
            context.results[self._key] = []
        context.results[self._key].extend(self._items)
        return context


class NumericIncrementStep(PipelineStep):
    """Step that increments a numeric value."""

    def __init__(self, step_id: str, key: str, increment: int | float):
        self._step_id = step_id
        self._key = key
        self._increment = increment

    @property
    def step_id(self) -> str:
        return self._step_id

    @property
    def description(self) -> str:
        return f"Increment {self._key} by {self._increment}"

    def run(self, context: PipelineContext[Any]) -> PipelineContext[Any]:
        current = context.results.get(self._key, 0)
        context.results[self._key] = current + self._increment
        return context


class DictMergeStep(PipelineStep):
    """Step that merges a dict into results."""

    def __init__(self, step_id: str, key: str, data: dict[str, Any]):
        self._step_id = step_id
        self._key = key
        self._data = data

    @property
    def step_id(self) -> str:
        return self._step_id

    @property
    def description(self) -> str:
        return f"Merge dict into {self._key}"

    def run(self, context: PipelineContext[Any]) -> PipelineContext[Any]:
        if self._key not in context.results:
            context.results[self._key] = {}
        context.results[self._key].update(self._data)
        return context


class TestListMerging:
    """Integration tests for list merging in parallel execution."""

    def test_parallel_steps_merge_lists(self, pipeline_context):
        """INTEGRATION: Parallel steps extend lists with new items."""
        # Arrange
        parallel_steps = [
            ListAppendStep("step1", "items", ["a", "b"]),
            ListAppendStep("step2", "items", ["c", "d"]),
            ListAppendStep("step3", "items", ["e", "f"]),
        ]
        config = ParallelConfig(operator=LogicOperator.AND)
        pipeline_config = PipelineConfig(parallel_config=config)
        pipeline = Pipeline(steps=[parallel_steps], config=pipeline_config)

        # Act
        result = pipeline.run(pipeline_context)

        # Assert - All items merged into list
        assert "items" in result.results
        items = result.results["items"]
        assert len(items) == 6
        assert set(items) == {"a", "b", "c", "d", "e", "f"}


class TestNumericMerging:
    """Integration tests for numeric value merging in parallel execution."""

    def test_parallel_steps_sum_numeric_increments(self, pipeline_context):
        """INTEGRATION: Parallel steps sum numeric increments."""
        # Arrange
        parallel_steps = [
            NumericIncrementStep("step1", "counter", 10),
            NumericIncrementStep("step2", "counter", 20),
            NumericIncrementStep("step3", "counter", 30),
        ]
        config = ParallelConfig(operator=LogicOperator.AND)
        pipeline_config = PipelineConfig(parallel_config=config)
        pipeline = Pipeline(steps=[parallel_steps], config=pipeline_config)

        # Act
        result = pipeline.run(pipeline_context)

        # Assert - Increments summed
        assert result.results["counter"] == 60  # 10 + 20 + 30


class TestDictMerging:
    """Integration tests for dict merging in parallel execution."""

    def test_parallel_steps_merge_dicts_shallowly(self, pipeline_context):
        """INTEGRATION: Parallel steps merge dicts (shallow merge).

        Note: Current implementation uses dict.update() which is shallow.
        Nested dicts are overwritten, not recursively merged.
        Last writer wins for nested dict values.
        """
        # Arrange
        parallel_steps = [
            DictMergeStep("step1", "config", {"a": 1, "b": {"x": 10}}),
            DictMergeStep("step2", "config", {"c": 2, "b": {"y": 20}}),
            DictMergeStep("step3", "config", {"d": 3, "b": {"z": 30}}),
        ]
        config = ParallelConfig(operator=LogicOperator.AND)
        pipeline_config = PipelineConfig(parallel_config=config)
        pipeline = Pipeline(steps=[parallel_steps], config=pipeline_config)

        # Act
        result = pipeline.run(pipeline_context)

        # Assert - Dicts merged at top level
        assert "config" in result.results
        config_dict = result.results["config"]
        assert config_dict["a"] == 1
        assert config_dict["c"] == 2
        assert config_dict["d"] == 3
        # Nested dict "b" is overwritten by last step (shallow merge)
        assert "b" in config_dict
        assert isinstance(config_dict["b"], dict)
