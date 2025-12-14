"""Test progress tracking functionality."""

import time
from typing import Any

from pipeline import Pipeline, PipelineContext, PipelineStep


class SimpleStep(PipelineStep):
    """Simple test step."""

    def __init__(self, step_id: str, result_value: str):
        """Initialize simple step."""
        self._step_id = step_id
        self._result_value = result_value

    @property
    def step_id(self) -> str:
        """Return step ID."""
        return self._step_id

    @property
    def description(self) -> str:
        """Return step description."""
        return f"Simple step: {self._step_id}"

    def run(self, context: PipelineContext[Any]) -> PipelineContext[Any]:
        """Add result to context."""
        context.results[self._step_id] = self._result_value
        return context


def test_progress_callback():
    """Test progress callback is called correctly with granular progress."""
    progress_updates = []

    def callback(step_index, total_steps, step_name, progress):
        progress_updates.append(
            {
                "step_index": step_index,
                "total_steps": total_steps,
                "step_name": step_name,
                "progress": progress,
            }
        )

    steps = [
        SimpleStep("step1", "done1"),
        SimpleStep("step2", "done2"),
        SimpleStep("step3", "done3"),
    ]

    # Create a minimal context
    class MockLogger:
        def info(self, msg):
            pass

        def error(self, msg):
            pass

    class MockConfig:
        pass

    context = PipelineContext(
        app_config=MockConfig(), logger_instance=MockLogger()
    )

    pipeline = Pipeline(steps=steps, progress_callback=callback)
    result = pipeline.run(context)

    # Verify callback was called 3 times (once per step completion)
    assert len(progress_updates) == 3

    # Verify first update - step1 completed (auto-completed to 100%)
    assert progress_updates[0]["step_index"] == 0
    assert progress_updates[0]["total_steps"] == 3
    assert progress_updates[0]["step_name"] == "step1"
    assert abs(progress_updates[0]["progress"] - 33.333333333333336) < 0.01

    # Verify second update - step2 completed
    assert progress_updates[1]["step_index"] == 1
    assert progress_updates[1]["total_steps"] == 3
    assert progress_updates[1]["step_name"] == "step2"
    assert abs(progress_updates[1]["progress"] - 66.666666666666671) < 0.01

    # Verify third update - step3 completed
    assert progress_updates[2]["step_index"] == 2
    assert progress_updates[2]["total_steps"] == 3
    assert progress_updates[2]["step_name"] == "step3"
    assert progress_updates[2]["progress"] == 100.0

    # Verify results were added to context
    assert result.results["step1"] == "done1"
    assert result.results["step2"] == "done2"
    assert result.results["step3"] == "done3"

    print("✓ Progress callback test passed")


def test_status_methods():
    """Test status query methods with granular progress."""
    steps = [
        SimpleStep("step1", "done1"),
        SimpleStep("step2", "done2"),
    ]

    class MockLogger:
        def info(self, msg):
            pass

        def error(self, msg):
            pass

    class MockConfig:
        pass

    context = PipelineContext(
        app_config=MockConfig(), logger_instance=MockLogger()
    )

    pipeline = Pipeline(steps=steps)

    # Before execution
    assert pipeline.is_running() is False
    assert pipeline.get_current_step() is None
    status = pipeline.get_status()
    assert status["progress"] == 0.0
    assert status["current_step"] is None
    assert status["is_running"] is False
    assert "step_details" in status
    assert len(status["step_details"]) == 2

    # Execute
    pipeline.run(context)

    # After execution
    assert pipeline.is_running() is False
    assert pipeline.get_current_step() is None

    # Check final status
    final_status = pipeline.get_status()
    assert final_status["progress"] == 100.0
    assert final_status["is_running"] is False

    print("✓ Status methods test passed")


def test_granular_progress_within_step():
    """Test granular progress updates within a single step."""

    class GranularStep(PipelineStep):
        """Step that reports granular progress."""

        def __init__(self, step_id_val: str):
            self._step_id = step_id_val

        @property
        def step_id(self) -> str:
            return self._step_id

        @property
        def description(self) -> str:
            return f"Granular step {self._step_id}"

        def run(self, context: PipelineContext) -> PipelineContext:
            # Simulate multi-phase work with progress updates
            context.update_step_progress(25.0)
            time.sleep(0.01)  # Simulate work

            context.update_step_progress(50.0)
            time.sleep(0.01)

            context.update_step_progress(75.0)
            time.sleep(0.01)

            context.update_step_progress(100.0)
            context.results[self.step_id] = "completed"
            return context

    steps = [
        GranularStep("step1"),
        GranularStep("step2"),
    ]

    class MockLogger:
        def info(self, msg):
            pass

        def error(self, msg):
            pass

    class MockConfig:
        pass

    context = PipelineContext(
        app_config=MockConfig(), logger_instance=MockLogger()
    )

    pipeline = Pipeline(steps=steps)
    result = pipeline.run(context)

    # Verify final progress is 100%
    status = pipeline.get_status()
    assert status["progress"] == 100.0

    # Verify step details show 100% for each step
    step_details = status["step_details"]
    assert step_details["step1"]["internal_progress"] == 100.0
    assert step_details["step2"]["internal_progress"] == 100.0

    # Verify results
    assert result.results["step1"] == "completed"
    assert result.results["step2"] == "completed"

    print("✓ Granular progress within step test passed")


def test_auto_completion_without_progress_updates():
    """Test that steps auto-complete to 100% even without progress updates."""

    class NoProgressStep(PipelineStep):
        """Step that never calls update_step_progress."""

        def __init__(self, step_id_val: str, result_value: str):
            self._step_id = step_id_val
            self.result_value = result_value

        @property
        def step_id(self) -> str:
            return self._step_id

        @property
        def description(self) -> str:
            return f"No progress step {self._step_id}"

        def run(self, context: PipelineContext) -> PipelineContext:
            # Do work but never call update_step_progress
            context.results[self.step_id] = self.result_value
            return context

    steps = [
        NoProgressStep("step1", "done1"),
        NoProgressStep("step2", "done2"),
    ]

    class MockLogger:
        def info(self, msg):
            pass

        def error(self, msg):
            pass

    class MockConfig:
        pass

    context = PipelineContext(
        app_config=MockConfig(), logger_instance=MockLogger()
    )

    pipeline = Pipeline(steps=steps)
    pipeline.run(context)

    # Verify final progress is 100% (auto-completed)
    status = pipeline.get_status()
    assert status["progress"] == 100.0

    # Verify each step was auto-completed to 100%
    step_details = status["step_details"]
    assert step_details["step1"]["internal_progress"] == 100.0
    assert step_details["step2"]["internal_progress"] == 100.0

    print("✓ Auto-completion test passed")


if __name__ == "__main__":
    test_progress_callback()
    test_status_methods()
    test_granular_progress_within_step()
    test_auto_completion_without_progress_updates()
    print("\n✅ All tests passed!")
