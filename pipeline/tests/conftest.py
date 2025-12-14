"""Shared fixtures for pipeline tests."""

from dataclasses import dataclass
from typing import Any
from unittest.mock import MagicMock

import pytest

from pipeline import (
    LogicOperator,
    ParallelConfig,
    PipelineConfig,
    PipelineContext,
    PipelineStep,
)

# Export test step classes so they can be imported in test files
__all__ = [
    "SimpleStep",
    "FailingStep",
    "CounterStep",
    "SlowStep",
    "MockAppConfig",
]


@dataclass
class MockAppConfig:
    """Mock application configuration for testing."""

    name: str = "test_app"
    version: str = "1.0.0"
    debug: bool = False


@pytest.fixture
def mock_app_config():
    """Provide a mock application configuration."""
    return MockAppConfig()


@pytest.fixture
def mock_logger():
    """Provide a mock logger instance."""
    logger = MagicMock()
    logger.info = MagicMock()
    logger.error = MagicMock()
    logger.warning = MagicMock()
    logger.debug = MagicMock()
    return logger


@pytest.fixture
def pipeline_context(mock_app_config, mock_logger):
    """Provide a basic pipeline context."""
    return PipelineContext(
        app_config=mock_app_config,
        logger_instance=mock_logger,
    )


@pytest.fixture
def pipeline_config():
    """Provide a basic pipeline configuration."""
    return PipelineConfig(fail_fast=True)


@pytest.fixture
def parallel_config():
    """Provide a basic parallel configuration."""
    return ParallelConfig(
        operator=LogicOperator.AND,
        max_workers=2,
        timeout=5.0,
    )


class SimpleStep(PipelineStep):
    """Simple test step that adds a result."""

    def __init__(self, step_id: str, result_key: str, result_value: Any):
        """Initialize simple step."""
        self._step_id = step_id
        self._result_key = result_key
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
        context.results[self._result_key] = self._result_value
        return context


class FailingStep(PipelineStep):
    """Test step that always fails."""

    def __init__(
        self, step_id: str, error_message: str, critical: bool = True
    ):
        """Initialize failing step."""
        self._step_id = step_id
        self._error_message = error_message
        self._critical = critical

    @property
    def step_id(self) -> str:
        """Return step ID."""
        return self._step_id

    @property
    def description(self) -> str:
        """Return step description."""
        return f"Failing step: {self._step_id}"

    @property
    def critical(self) -> bool:
        """Return whether step is critical."""
        return self._critical

    def run(self, context: PipelineContext[Any]) -> PipelineContext[Any]:
        """Raise an exception."""
        raise RuntimeError(self._error_message)


class CounterStep(PipelineStep):
    """Test step that increments a counter."""

    def __init__(
        self, step_id: str, counter_key: str = "counter", increment: int = 1
    ):
        """Initialize counter step."""
        self._step_id = step_id
        self._counter_key = counter_key
        self._increment = increment

    @property
    def step_id(self) -> str:
        """Return step ID."""
        return self._step_id

    @property
    def description(self) -> str:
        """Return step description."""
        return f"Counter step: {self._step_id}"

    def run(self, context: PipelineContext[Any]) -> PipelineContext[Any]:
        """Increment counter in context."""
        current = context.results.get(self._counter_key, 0)
        context.results[self._counter_key] = current + self._increment
        return context


class SlowStep(PipelineStep):
    """Test step that takes time to execute."""

    def __init__(self, step_id: str, delay: float):
        """Initialize slow step."""
        self._step_id = step_id
        self._delay = delay

    @property
    def step_id(self) -> str:
        """Return step ID."""
        return self._step_id

    @property
    def description(self) -> str:
        """Return step description."""
        return f"Slow step: {self._step_id} ({self._delay}s)"

    def run(self, context: PipelineContext[Any]) -> PipelineContext[Any]:
        """Sleep for specified delay."""
        import time

        time.sleep(self._delay)
        context.results[f"{self._step_id}_completed"] = True
        return context


@pytest.fixture
def simple_step():
    """Provide a simple test step."""
    return SimpleStep("simple_step", "test_key", "test_value")


@pytest.fixture
def failing_step():
    """Provide a failing test step."""
    return FailingStep("failing_step", "Test error", critical=True)


@pytest.fixture
def non_critical_failing_step():
    """Provide a non-critical failing test step."""
    return FailingStep(
        "non_critical_step", "Non-critical error", critical=False
    )


@pytest.fixture
def counter_step():
    """Provide a counter test step."""
    return CounterStep("counter_step", "counter", 1)
