"""Main pipeline executor for orchestrating step execution."""

from ..core.types import (
    PipelineConfig,
    PipelineContext,
    TaskStep,
)
from .parallel_executor import (
    ParallelTaskExecutor,
)
from .task_executor import TaskExecutor


class PipelineExecutor:
    """Orchestrates pipeline execution with serial and parallel steps."""

    def __init__(
        self,
        task_executor: TaskExecutor | None = None,
        parallel_executor: ParallelTaskExecutor | None = None,
    ):
        """
        Initialize pipeline executor.

        Args:
            task_executor: Executor for individual steps (optional)
            parallel_executor: Executor for parallel groups (optional)
        """
        self.task_executor = task_executor or TaskExecutor()
        self.parallel_executor = parallel_executor or ParallelTaskExecutor(
            self.task_executor
        )

    def execute(
        self,
        steps: list[TaskStep],
        context: PipelineContext,
        config: PipelineConfig,
    ) -> PipelineContext:
        """
        Execute pipeline steps and return final context.

        Args:
            steps: List of pipeline steps (steps or parallel groups)
            context: Pipeline context
            config: Pipeline configuration

        Returns:
            PipelineContext: Final context after all steps
        """
        current_context = context

        for step in steps:
            try:
                if isinstance(step, list):
                    # Parallel group
                    current_context = self.parallel_executor.execute(
                        step, current_context, config.parallel_config
                    )
                else:
                    # Serial step
                    current_context = self.task_executor.execute(
                        step, current_context
                    )
            except Exception as e:
                if config.fail_fast:
                    raise
                # If not fail_fast, continue with current context
                if hasattr(current_context, "errors"):
                    current_context.errors.append(e)

        return current_context
