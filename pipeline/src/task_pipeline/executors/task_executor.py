"""Individual task executor with error handling."""

from ..core.types import PipelineContext, PipelineStep


class TaskExecutor:
    """Executes individual pipeline steps with proper error handling."""

    def execute(
        self, step: PipelineStep, context: PipelineContext
    ) -> PipelineContext:
        """
        Execute a single pipeline step.

        Args:
            step: The pipeline step to execute
            context: Pipeline context

        Returns:
            PipelineContext: The modified context object

        Raises:
            Exception: If step fails and is critical
        """
        try:
            return step.run(context)
        except Exception as e:
            # Store error in context if it has an errors attribute
            if hasattr(context, "errors"):
                context.errors.append(e)

            # Re-raise if step is critical
            if step.critical:
                raise

            # Return original context if step is not critical
            return context
