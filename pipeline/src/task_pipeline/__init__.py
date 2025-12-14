"""Pipeline module with clean architecture for task execution."""

# Core components
from .core import (
    LogicOperator,
    ParallelConfig,
    PipelineConfig,
    PipelineContext,
    PipelineStep,
    ProgressTracker,
    TaskStep,
)

# Decorators
from .decorators import with_progress_callback

# Executors for advanced usage
from .executors import (
    ParallelTaskExecutor,
    PipelineExecutor,
    TaskExecutor,
)

# Main pipeline interface
from .pipeline import Pipeline

__all__ = [
    # Core types and configuration
    "LogicOperator",
    "ParallelConfig",
    "PipelineConfig",
    "PipelineContext",
    "PipelineStep",
    "ProgressTracker",
    "TaskStep",
    # Decorators
    "with_progress_callback",
    # Main interface
    "Pipeline",
    # Executors
    "ParallelTaskExecutor",
    "PipelineExecutor",
    "TaskExecutor",
]
