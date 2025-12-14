"""Core pipeline types and configuration classes."""

import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from rich_logging.rich.rich_logger import RichLogger


@dataclass
class PipelineContext[AppConfig]:
    """Centralized pipeline context for any application using the pipeline.

    The app_config field accepts any application-specific configuration object.
    For the dotfiles installer, this would be src.config.config.AppConfig.
    """

    app_config: AppConfig
    logger_instance: RichLogger
    # Runtime state
    results: dict[str, Any] = field(default_factory=dict)
    errors: list[Exception] = field(default_factory=list)

    # Internal progress tracking (set by Pipeline)
    _progress_tracker: "ProgressTracker | None" = field(
        default=None, repr=False
    )
    _current_step_id: str | None = field(default=None, repr=False)

    def update_step_progress(self, progress: float) -> None:
        """
        Update progress for the current step (0-100).

        Call this from within your step's run() method to report progress.

        Args:
            progress: Progress percentage (0-100) for current step

        Example:
            def run(self, context):
                for i, item in enumerate(items):
                    process(item)
                    context.update_step_progress((i + 1) / len(items) * 100)
                return context
        """
        if self._progress_tracker and self._current_step_id:
            self._progress_tracker.update_step_progress(
                self._current_step_id, progress
            )

    def __deepcopy__(
        self, memo: dict[int, Any]
    ) -> "PipelineContext[AppConfig]":
        """
        Custom deep copy that handles non-picklable progress tracker.

        The progress tracker is shared across all context copies (not deep
        copied) since it needs to be the same instance for thread-safe
        progress updates.
        """
        import copy

        # Create new instance with deep copied fields except progress tracker
        return PipelineContext(
            app_config=copy.deepcopy(self.app_config, memo),
            logger_instance=copy.deepcopy(self.logger_instance, memo),
            results=copy.deepcopy(self.results, memo),
            errors=copy.deepcopy(self.errors, memo),
            _progress_tracker=self._progress_tracker,  # Share, don't copy
            _current_step_id=self._current_step_id,
        )


class LogicOperator(Enum):
    """Logic operators for parallel task execution."""

    AND = "and"
    OR = "or"


class PipelineStep(ABC):
    """Abstract base class for pipeline steps."""

    @property
    @abstractmethod
    def step_id(self) -> str:
        """Unique identifier for this step."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of what this step does."""
        pass

    @abstractmethod
    def run(self, context: PipelineContext[Any]) -> PipelineContext[Any]:
        """
        Execute the step logic.

        Args:
            context: Pipeline context object

        Returns:
            PipelineContext: The context object (potentially modified)
        """
        pass

    # Optional overridable properties
    @property
    def timeout(self) -> float | None:
        """Step timeout in seconds."""
        return None

    @property
    def retries(self) -> int:
        """Number of retries on failure."""
        return 0

    @property
    def critical(self) -> bool:
        """Whether step failure should stop the pipeline."""
        return True


@dataclass
class ParallelConfig:
    """Configuration for parallel task execution."""

    operator: LogicOperator = LogicOperator.AND
    max_workers: int | None = None
    timeout: float | None = None


@dataclass
class PipelineConfig:
    """Configuration for pipeline execution."""

    fail_fast: bool = True
    parallel_config: ParallelConfig = field(default_factory=ParallelConfig)


# Type alias for pipeline steps
TaskStep = PipelineStep | list[PipelineStep]


class ProgressTracker:
    """Thread-safe progress tracker for granular pipeline progress."""

    def __init__(self, steps: list[TaskStep]):
        """
        Initialize progress tracker with pipeline steps.

        Args:
            steps: List of pipeline steps (steps or parallel groups)
        """
        self._lock = threading.Lock()
        self._step_weights = self._calculate_weights(steps)
        self._step_progress: dict[str, float] = {}

    def _calculate_weights(self, steps: list[TaskStep]) -> dict[str, float]:
        """
        Calculate weight (% of total) for each step.

        Each top-level step gets equal weight (100 / total_steps).
        For parallel groups, the group's weight is divided equally among
        sub-steps.

        Args:
            steps: List of pipeline steps

        Returns:
            dict mapping step_id to its maximum weight percentage
        """
        total_steps = len(steps)

        # Handle empty steps list
        if total_steps == 0:
            return {}

        step_weight = 100.0 / total_steps

        weights = {}
        for step in steps:
            if isinstance(step, list):
                # Parallel group - divide group weight among sub-steps
                if len(step) > 0:
                    sub_weight = step_weight / len(step)
                    for sub_step in step:
                        weights[sub_step.step_id] = sub_weight
            else:
                weights[step.step_id] = step_weight

        return weights

    def update_step_progress(self, step_id: str, progress: float) -> None:
        """
        Update progress for a specific step.

        Args:
            step_id: ID of the step to update
            progress: Progress percentage within the step (0-100)
        """
        with self._lock:
            # Clamp to 0-100
            self._step_progress[step_id] = max(0.0, min(100.0, progress))

    def get_overall_progress(self) -> float:
        """
        Calculate overall pipeline progress (0-100).

        Returns:
            Overall progress percentage
        """
        with self._lock:
            total = 0.0
            for step_id, max_weight in self._step_weights.items():
                step_internal_progress = self._step_progress.get(step_id, 0.0)
                # Contribution = max_weight * (internal_progress / 100)
                contribution = max_weight * (step_internal_progress / 100.0)
                total += contribution
            return total

    def get_step_details(self) -> dict[str, dict[str, float]]:
        """
        Get detailed progress information for all steps.

        Returns:
            dict mapping step_id to progress details:
            - internal_progress: Progress within the step (0-100)
            - max_weight: Maximum weight of this step in overall progress
            - contribution: Current contribution to overall progress
        """
        with self._lock:
            return {
                step_id: {
                    "internal_progress": self._step_progress.get(step_id, 0.0),
                    "max_weight": max_weight,
                    "contribution": max_weight
                    * (self._step_progress.get(step_id, 0.0) / 100.0),
                }
                for step_id, max_weight in self._step_weights.items()
            }
