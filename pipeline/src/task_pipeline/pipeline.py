"""Main pipeline interface following the Log class pattern."""

from collections.abc import Callable
from typing import Any

from .core.types import (
    PipelineConfig,
    PipelineContext,
    ProgressTracker,
    TaskStep,
)
from .executors.pipeline_executor import PipelineExecutor


class Pipeline:
    """
    Main pipeline interface for step execution.

    Provides a clean, high-level API for executing steps in serial and
    parallel, similar to the Log class pattern used in the logging module.
    """

    def __init__(
        self,
        steps: list[TaskStep],
        config: PipelineConfig | None = None,
        progress_callback: (
            "Callable[[int, int, str, float], None] | None"
        ) = None,
    ):
        """
        Initialize pipeline with steps and configuration.

        Args:
            steps: List of pipeline steps (steps or parallel groups)
            config: Pipeline configuration (optional)
            progress_callback: Optional callback for progress updates.
                Signature: (step_index, total_steps, step_name,
                progress_percent)

        Examples:
            # Serial execution
            pipeline = Pipeline([step1, step2, step3])

            # Parallel groups
            pipeline = Pipeline([
                [step1, step2, step3],  # parallel group
                [step4, step5, step6],  # parallel group
            ])

            # Mixed serial and parallel
            pipeline = Pipeline([
                step1,          # serial
                [step2, step3], # parallel
                step4,          # serial
            ])

            # With progress callback
            def on_progress(step_idx, total, name, percent):
                print(f"Progress: {percent:.1f}% - {name}")

            pipeline = Pipeline([step1, step2], progress_callback=on_progress)
        """
        self.steps = steps
        self.config = config or PipelineConfig()
        self._executor = PipelineExecutor()
        self._progress_callback = progress_callback
        self._current_step: int | None = None
        self._total_steps = len(steps)
        self._is_running = False
        self._progress_tracker = ProgressTracker(steps)

    def run(self, context: PipelineContext) -> PipelineContext:
        """
        Execute the pipeline and return final context.

        Args:
            context: Pipeline context containing shared data

        Returns:
            PipelineContext: Final context after all steps have executed

        Examples:
            final_context = pipeline.run(context)
            if final_context.errors:
                print("Pipeline had errors")
        """
        self._is_running = True

        # Inject progress tracker into context
        context._progress_tracker = self._progress_tracker

        try:
            current_context = context

            for step_index, step in enumerate(self.steps):
                self._current_step = step_index

                try:
                    if isinstance(step, list):
                        # Parallel group
                        for sub_step in step:
                            # Set step_id for each parallel step
                            current_context._current_step_id = sub_step.step_id

                        current_context = (
                            self._executor.parallel_executor.execute(
                                step,
                                current_context,
                                self.config.parallel_config,
                                self._progress_tracker,
                            )
                        )

                        # Auto-complete all parallel steps to 100%
                        for sub_step in step:
                            self._progress_tracker.update_step_progress(
                                sub_step.step_id, 100.0
                            )
                    else:
                        # Serial step
                        current_context._current_step_id = step.step_id

                        current_context = self._executor.task_executor.execute(
                            step, current_context
                        )

                        # Auto-complete step to 100%
                        self._progress_tracker.update_step_progress(
                            step.step_id, 100.0
                        )

                    # Call progress callback if provided
                    if self._progress_callback:
                        overall_progress = (
                            self._progress_tracker.get_overall_progress()
                        )
                        step_name = (
                            f"parallel_group_{step_index}"
                            if isinstance(step, list)
                            else step.step_id
                        )
                        self._progress_callback(
                            step_index,
                            self._total_steps,
                            step_name,
                            overall_progress,
                        )

                except Exception as e:
                    if self.config.fail_fast:
                        raise
                    # If not fail_fast, continue with current context
                    if hasattr(current_context, "errors"):
                        current_context.errors.append(e)

            return current_context
        finally:
            self._is_running = False
            self._current_step = None

    def get_status(self) -> dict[str, Any]:
        """
        Get current progress status with granular progress tracking.

        Returns:
            dict with keys:
            - progress: float (0-100) - overall progress with granularity
            - current_step: str | None - name of current step
            - is_running: bool - whether pipeline is executing
            - step_details: dict[str, dict] - detailed progress for each step
        """
        current_step_name = None
        if self._current_step is not None and self._current_step < len(
            self.steps
        ):
            step = self.steps[self._current_step]
            if isinstance(step, list):
                # For parallel groups, use a generic name
                current_step_name = f"parallel_group_{self._current_step}"
            else:
                current_step_name = step.step_id

        return {
            "progress": self._progress_tracker.get_overall_progress(),
            "current_step": current_step_name,
            "is_running": self._is_running,
            "step_details": self._progress_tracker.get_step_details(),
        }

    def is_running(self) -> bool:
        """Return True if pipeline is currently executing."""
        return self._is_running

    def get_current_step(self) -> str | None:
        """Return name of current step or None."""
        if self._current_step is not None and self._current_step < len(
            self.steps
        ):
            step = self.steps[self._current_step]
            if isinstance(step, list):
                # For parallel groups, use a generic name
                return f"parallel_group_{self._current_step}"
            return step.step_id
        return None

    @staticmethod
    def create(
        steps: list[TaskStep], config: PipelineConfig | None = None
    ) -> "Pipeline":
        """
        Create a new pipeline (factory method following Log.create_logger
        pattern).

        Args:
            steps: List of pipeline steps
            config: Pipeline configuration (optional)

        Returns:
            Pipeline: Configured pipeline instance
        """
        return Pipeline(steps, config)
