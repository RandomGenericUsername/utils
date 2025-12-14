"""Core logging functionality.

This module contains the core components of the logging system:
- LogConfigurator: Main configuration orchestrator
- Type definitions: Enums and dataclasses for type safety
- Utility functions: Helper functions for logging operations
"""

from .configurator import LoggerConfigurator
from .log_types import (  # Color classes; Configuration classes; Enums
    ColoredFormatterColors,
    ConsoleHandlers,
    FileHandlerSpec,
    FileHandlerTypes,
    LogConfig,
    LogFormatters,
    LogFormatterStyleChoices,
    LogLevels,
)
from .utils import (
    get_log_level_from_verbosity,
    parse_log_level,
    validate_log_level_string,
)

__all__ = [
    # Core orchestrator
    "LoggerConfigurator",
    # Enums
    "LogLevels",
    "LogFormatters",
    "LogFormatterStyleChoices",
    "ConsoleHandlers",
    "FileHandlerTypes",
    # Configuration
    "LogConfig",
    "FileHandlerSpec",
    # Colors
    "ColoredFormatterColors",
    # Utilities
    "get_log_level_from_verbosity",
    "validate_log_level_string",
    "parse_log_level",
]
