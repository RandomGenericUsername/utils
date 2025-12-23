"""Shared test fixtures for all test suites.

This module provides reusable fixtures for contract, integration, unit, and
characterization tests.
"""

import logging as stdlib_logging
from typing import Generator
from unittest.mock import Mock, MagicMock

import pytest

from rich_logging import (
    Log,
    LogConfig,
    LogLevels,
    ConsoleHandlers,
    LogFormatters,
    LogFormatterStyleChoices,
    RichFeatureSettings,
    RichHandlerSettings,
)


@pytest.fixture(autouse=True)
def reset_loggers():
    """Reset logger state before each test.
    
    This ensures tests don't interfere with each other by:
    - Clearing Log._configurators registry
    - Removing all handlers from root logger
    """
    # Clear the configurators registry
    Log._configurators.clear()
    
    # Clear root logger handlers
    root_logger = stdlib_logging.getLogger()
    root_logger.handlers.clear()
    
    yield
    
    # Cleanup after test
    Log._configurators.clear()
    root_logger.handlers.clear()


@pytest.fixture
def mock_console():
    """Provide a mock Rich Console for testing.
    
    Returns:
        Mock: Mock console with print, log, and other Rich methods
    """
    console = Mock()
    console.print = Mock()
    console.log = Mock()
    console.file = Mock()
    return console


@pytest.fixture
def basic_log_config() -> LogConfig:
    """Provide a basic LogConfig for testing.

    Returns:
        LogConfig: Basic configuration with INFO level and default handler
    """
    return LogConfig(
        name="test_logger",
        log_level=LogLevels.INFO,
        console_handler=ConsoleHandlers.DEFAULT,
        formatter_type=LogFormatters.DEFAULT,
        formatter_style=LogFormatterStyleChoices.PERCENT,
    )


@pytest.fixture
def rich_log_config() -> LogConfig:
    """Provide a Rich-enabled LogConfig for testing.
    
    Returns:
        LogConfig: Configuration with Rich handler and features enabled
    """
    return LogConfig(
        name="test_rich_logger",
        log_level=LogLevels.DEBUG,
        console_handler=ConsoleHandlers.RICH,
        formatter_type=LogFormatters.RICH,
        handler_config=RichHandlerSettings(
            show_time=True,
            show_path=False,
            markup=True,
        ),
        rich_features=RichFeatureSettings(
            enabled=True,
            table_show_lines=True,
            panel_border_style="blue",
        ),
    )


@pytest.fixture
def mock_stdlib_logger() -> Mock:
    """Provide a mock stdlib Logger for testing.
    
    Returns:
        Mock: Mock logger with standard logging methods
    """
    logger = Mock(spec=stdlib_logging.Logger)
    logger.name = "test_logger"
    logger.level = stdlib_logging.INFO
    logger.handlers = []
    logger.setLevel = Mock()
    logger.addHandler = Mock()
    logger.removeHandler = Mock()
    logger.info = Mock()
    logger.debug = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    logger.critical = Mock()
    return logger


@pytest.fixture
def capture_log_output(caplog):
    """Capture log output for assertions.
    
    Args:
        caplog: pytest's built-in log capture fixture
        
    Yields:
        caplog: Configured log capture
    """
    caplog.set_level(stdlib_logging.DEBUG)
    yield caplog


@pytest.fixture
def temp_log_file(tmp_path):
    """Provide a temporary file path for file logging tests.
    
    Args:
        tmp_path: pytest's built-in temporary directory fixture
        
    Returns:
        Path: Path to temporary log file
    """
    return tmp_path / "test.log"

