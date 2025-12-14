"""Parallel task executor using ThreadPoolExecutor."""

import copy
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..core.types import (
    LogicOperator,
    ParallelConfig,
    PipelineContext,
    PipelineStep,
    ProgressTracker,
)
from .task_executor import TaskExecutor


class ParallelTaskExecutor:
    """Executes parallel step groups with configurable logic and context
    merging."""

    def __init__(self, task_executor: TaskExecutor | None = None):
        """
        Initialize parallel executor.

        Args:
            task_executor: Task executor for individual steps (optional)
        """
        self.task_executor = task_executor or TaskExecutor()

    def execute(
        self,
        steps: list[PipelineStep],
        context: PipelineContext,
        config: ParallelConfig,
        progress_tracker: "ProgressTracker | None" = None,
    ) -> PipelineContext:
        """
        Execute a group of steps in parallel with context merging.

        Args:
            steps: List of pipeline steps to execute in parallel
            context: Pipeline context
            config: Parallel execution configuration
            progress_tracker: Optional progress tracker for granular progress

        Returns:
            PipelineContext: Merged context from all parallel executions
        """
        if not steps:
            return context

        # Keep original context for merging
        original_context = copy.deepcopy(context)

        with ThreadPoolExecutor(max_workers=config.max_workers) as executor:
            # Submit all steps with deep copies of context
            futures = []
            for step in steps:
                step_context = copy.deepcopy(original_context)
                # Set current step ID for this parallel branch
                step_context._current_step_id = step.step_id
                step_context._progress_tracker = progress_tracker

                futures.append(
                    executor.submit(
                        self.task_executor.execute,
                        step,
                        step_context,
                    )
                )

            # Collect results
            step_contexts = []
            step_success = []

            for future in as_completed(futures, timeout=config.timeout):
                try:
                    result_context = future.result()
                    step_contexts.append(result_context)
                    step_success.append(True)
                except Exception:
                    step_success.append(False)

            # Check if parallel group succeeded based on logic operator
            if config.operator == LogicOperator.AND:
                group_succeeded = all(step_success)
            else:  # OR
                group_succeeded = any(step_success)

            if not group_succeeded:
                raise RuntimeError("Parallel group failed")

            # Merge contexts from successful steps
            merged_context = self._merge_contexts(
                original_context, step_contexts
            )
            return merged_context

    def _merge_contexts(
        self,
        original_context: PipelineContext,
        step_contexts: list[PipelineContext],
    ) -> PipelineContext:
        """
        Merge contexts from parallel steps.

        Args:
            original_context: The original context before parallel execution
            step_contexts: List of contexts returned from parallel steps

        Returns:
            PipelineContext: Merged context
        """
        merged = copy.deepcopy(original_context)

        for step_context in step_contexts:
            # Merge results if both contexts have results attribute
            if (
                hasattr(merged, "results")
                and hasattr(step_context, "results")
                and isinstance(merged.results, dict)
                and isinstance(step_context.results, dict)
            ):
                # Dict-style results - merge with special handling
                # for numeric values and lists
                for key, value in step_context.results.items():
                    original_value = (
                        original_context.results.get(key, [])
                        if hasattr(original_context, "results")
                        and isinstance(value, list)
                        else (
                            original_context.results.get(key, 0)
                            if hasattr(original_context, "results")
                            else 0
                        )
                    )

                    # Check if value is a list - merge lists by extending
                    if isinstance(value, list):
                        # Only merge items that were added by this step
                        # (not present in original)
                        if isinstance(original_value, list):
                            original_len = len(original_value)
                            new_items = value[
                                original_len:
                            ]  # Only items added by this step
                            if new_items:  # Only extend if there are new items
                                if key in merged.results and isinstance(
                                    merged.results[key], list
                                ):
                                    merged.results[key].extend(new_items)
                                else:
                                    merged.results[key] = (
                                        original_value.copy() + new_items
                                    )
                            elif key not in merged.results:
                                # No new items, set original
                                merged.results[key] = original_value.copy()
                        else:
                            # Original wasn't a list, just set the value
                            merged.results[key] = value.copy()
                    # Check if value is numeric (but not boolean)
                    elif (
                        isinstance(value, (int, float))
                        and not isinstance(value, bool)
                        and isinstance(original_value, (int, float))
                        and not isinstance(original_value, bool)
                    ):
                        # For numeric values, calculate the increment
                        # from this step
                        step_increment = value - original_value
                        if step_increment > 0:  # Only add positive increments
                            merged.results[key] = (
                                merged.results.get(key, original_value)
                                + step_increment
                            )
                    elif isinstance(value, dict):
                        # For dict values, merge recursively
                        if key in merged.results and isinstance(
                            merged.results[key], dict
                        ):
                            # Merge the dicts
                            merged.results[key].update(value)
                        else:
                            # No existing dict, just set the value
                            merged.results[key] = value.copy()
                    else:
                        # For all other values (booleans, strings, etc.)
                        merged.results[key] = value

            # Merge errors if both contexts have errors attribute
            if hasattr(merged, "errors") and hasattr(step_context, "errors"):
                original_error_len = (
                    len(original_context.errors)
                    if hasattr(original_context, "errors")
                    else 0
                )
                new_errors = step_context.errors[
                    original_error_len:
                ]  # Only new errors
                merged.errors.extend(new_errors)

        return merged
