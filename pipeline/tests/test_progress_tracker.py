"""Test ProgressTracker class functionality."""

import threading
from typing import Any

from pipeline import PipelineStep
from task_pipeline.core.types import ProgressTracker


class DummyStep(PipelineStep):
    """Dummy step for testing."""

    def __init__(self, step_id_val: str):
        self._step_id = step_id_val

    @property
    def step_id(self) -> str:
        return self._step_id

    @property
    def description(self) -> str:
        return f"Dummy {self._step_id}"

    def run(self, context: Any) -> Any:
        return context


class TestProgressTrackerBasics:
    """Test basic ProgressTracker functionality."""

    def test_tracker_initialization(self):
        """Test ProgressTracker can be initialized with steps."""
        steps = [DummyStep("step1"), DummyStep("step2")]
        tracker = ProgressTracker(steps)

        assert tracker is not None
        assert tracker.get_overall_progress() == 0.0

    def test_tracker_with_empty_steps(self):
        """Test ProgressTracker with empty steps list."""
        tracker = ProgressTracker([])

        assert tracker.get_overall_progress() == 0.0
        assert tracker.get_step_details() == {}

    def test_tracker_with_single_step(self):
        """Test ProgressTracker with single step."""
        steps = [DummyStep("step1")]
        tracker = ProgressTracker(steps)

        details = tracker.get_step_details()
        assert len(details) == 1
        assert details["step1"]["max_weight"] == 100.0
        assert details["step1"]["internal_progress"] == 0.0


class TestProgressTrackerWeightCalculation:
    """Test weight calculation for different step configurations."""

    def test_equal_weights_for_serial_steps(self):
        """Test that serial steps get equal weights."""
        steps = [DummyStep("step1"), DummyStep("step2"), DummyStep("step3")]
        tracker = ProgressTracker(steps)

        details = tracker.get_step_details()

        # Each step should get 100/3 = 33.33%
        assert abs(details["step1"]["max_weight"] - 33.333333) < 0.01
        assert abs(details["step2"]["max_weight"] - 33.333333) < 0.01
        assert abs(details["step3"]["max_weight"] - 33.333333) < 0.01

    def test_parallel_group_weight_distribution(self):
        """Test that parallel groups divide their weight equally."""
        steps = [
            DummyStep("step1"),
            [
                DummyStep("parallel1"),
                DummyStep("parallel2"),
                DummyStep("parallel3"),
            ],
            DummyStep("step2"),
        ]
        tracker = ProgressTracker(steps)

        details = tracker.get_step_details()

        # 3 top-level steps, each gets 33.33%
        assert abs(details["step1"]["max_weight"] - 33.333333) < 0.01
        assert abs(details["step2"]["max_weight"] - 33.333333) < 0.01

        # Parallel group divides 33.33% among 3 steps = 11.11% each
        assert abs(details["parallel1"]["max_weight"] - 11.111111) < 0.01
        assert abs(details["parallel2"]["max_weight"] - 11.111111) < 0.01
        assert abs(details["parallel3"]["max_weight"] - 11.111111) < 0.01

    def test_nested_parallel_groups(self):
        """Test weight calculation with nested parallel groups."""
        steps = [
            [DummyStep("p1"), DummyStep("p2")],
            [DummyStep("p3"), DummyStep("p4")],
        ]
        tracker = ProgressTracker(steps)

        details = tracker.get_step_details()

        # 2 top-level groups, each gets 50%
        # Each group divides 50% among 2 steps = 25% each
        assert abs(details["p1"]["max_weight"] - 25.0) < 0.01
        assert abs(details["p2"]["max_weight"] - 25.0) < 0.01
        assert abs(details["p3"]["max_weight"] - 25.0) < 0.01
        assert abs(details["p4"]["max_weight"] - 25.0) < 0.01


class TestProgressTrackerUpdates:
    """Test progress update functionality."""

    def test_update_single_step_progress(self):
        """Test updating progress for a single step."""
        steps = [DummyStep("step1")]
        tracker = ProgressTracker(steps)

        tracker.update_step_progress("step1", 50.0)

        assert tracker.get_overall_progress() == 50.0
        details = tracker.get_step_details()
        assert details["step1"]["internal_progress"] == 50.0
        assert details["step1"]["contribution"] == 50.0

    def test_update_multiple_steps_progress(self):
        """Test updating progress for multiple steps."""
        steps = [DummyStep("step1"), DummyStep("step2")]
        tracker = ProgressTracker(steps)

        tracker.update_step_progress("step1", 100.0)
        tracker.update_step_progress("step2", 50.0)

        # step1: 50% weight * 100% progress = 50%
        # step2: 50% weight * 50% progress = 25%
        # Total: 75%
        assert tracker.get_overall_progress() == 75.0

    def test_update_progress_beyond_100(self):
        """Test that progress is clamped to 100%."""
        steps = [DummyStep("step1")]
        tracker = ProgressTracker(steps)

        tracker.update_step_progress("step1", 150.0)

        # Should be clamped to 100%
        assert tracker.get_overall_progress() == 100.0
        details = tracker.get_step_details()
        assert details["step1"]["internal_progress"] == 100.0

    def test_update_progress_negative(self):
        """Test that negative progress is clamped to 0%."""
        steps = [DummyStep("step1")]
        tracker = ProgressTracker(steps)

        tracker.update_step_progress("step1", -10.0)

        # Should be clamped to 0%
        assert tracker.get_overall_progress() == 0.0

    def test_update_nonexistent_step(self):
        """Test updating progress for a step that doesn't exist."""
        steps = [DummyStep("step1")]
        tracker = ProgressTracker(steps)

        # Should not raise an error, just ignore
        tracker.update_step_progress("nonexistent", 50.0)

        assert tracker.get_overall_progress() == 0.0


class TestProgressTrackerThreadSafety:
    """Test thread safety of ProgressTracker."""

    def test_concurrent_updates(self):
        """Test that concurrent updates are thread-safe."""
        steps = [DummyStep(f"step{i}") for i in range(10)]
        tracker = ProgressTracker(steps)

        def update_progress(step_id: str):
            for i in range(10):
                tracker.update_step_progress(step_id, i * 10.0)

        threads = []
        for i in range(10):
            thread = threading.Thread(
                target=update_progress, args=(f"step{i}",)
            )
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # All steps should be at 90% (last update was 9 * 10 = 90)
        details = tracker.get_step_details()
        for i in range(10):
            assert details[f"step{i}"]["internal_progress"] == 90.0

    def test_concurrent_reads_and_writes(self):
        """Test that concurrent reads and writes don't cause issues."""
        steps = [DummyStep("step1"), DummyStep("step2")]
        tracker = ProgressTracker(steps)

        results = []

        def writer():
            for i in range(50):
                tracker.update_step_progress("step1", i * 2.0)

        def reader():
            for _ in range(50):
                progress = tracker.get_overall_progress()
                results.append(progress)

        writer_thread = threading.Thread(target=writer)
        reader_thread = threading.Thread(target=reader)

        writer_thread.start()
        reader_thread.start()

        writer_thread.join()
        reader_thread.join()

        # Should have 50 readings
        assert len(results) == 50
        # All readings should be valid (0-100)
        assert all(0 <= r <= 100 for r in results)


class TestProgressTrackerStepDetails:
    """Test step details functionality."""

    def test_step_details_structure(self):
        """Test that step details have correct structure."""
        steps = [DummyStep("step1")]
        tracker = ProgressTracker(steps)

        details = tracker.get_step_details()

        assert "step1" in details
        assert "internal_progress" in details["step1"]
        assert "max_weight" in details["step1"]
        assert "contribution" in details["step1"]

    def test_contribution_calculation(self):
        """Test that contribution is calculated correctly."""
        steps = [DummyStep("step1"), DummyStep("step2")]
        tracker = ProgressTracker(steps)

        tracker.update_step_progress("step1", 50.0)

        details = tracker.get_step_details()

        # step1: 50% weight * 50% progress = 25% contribution
        assert details["step1"]["contribution"] == 25.0
        # step2: 50% weight * 0% progress = 0% contribution
        assert details["step2"]["contribution"] == 0.0

    def test_step_details_with_parallel_groups(self):
        """Test step details with parallel execution."""
        steps = [
            DummyStep("serial1"),
            [DummyStep("parallel1"), DummyStep("parallel2")],
            DummyStep("serial2"),
        ]
        tracker = ProgressTracker(steps)

        details = tracker.get_step_details()

        # Should have 4 steps total
        assert len(details) == 4
        assert "serial1" in details
        assert "parallel1" in details
        assert "parallel2" in details
        assert "serial2" in details
