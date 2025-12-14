"""Logging module with clean architecture."""

# Core components
from .core import (
    ColoredFormatterColors,
    ConsoleHandlers,
    FileHandlerSpec,
    FileHandlerTypes,
    LogConfig,
    LogFormatters,
    LogFormatterStyleChoices,
    LoggerConfigurator,
    LogLevels,
    get_log_level_from_verbosity,
    parse_log_level,
    validate_log_level_string,
)

# Legacy imports for backward compatibility
from .core.log_types import (
    LogLevelOptions,
    VerbosityToLogLevel,
)

# Re-export formatter and handler classes for advanced usage
from .formatters import (
    ColoredFormatter,
    FormatterFactory,
    RichFormatter,
)
from .handlers import (
    FileHandlerSettings,
    HandlerFactory,
    RichHandlerSettings,
    RotatingFileHandlerSettings,
    TimedRotatingFileHandlerSettings,
)

# Main API
from .log import FORMATTER_PLACEHOLDERS, Log

# Rich features
from .rich import (
    RichFeatureSettings,
    RichLogger,
)

__all__ = [
    # Main API
    "Log",
    "FORMATTER_PLACEHOLDERS",
    # Types
    "ColoredFormatterColors",
    "ConsoleHandlers",
    "LogConfig",
    "LogFormatters",
    "LogFormatterStyleChoices",
    "LogLevels",
    "LogLevelOptions",
    "VerbosityToLogLevel",
    # Utils
    "get_log_level_from_verbosity",
    "parse_log_level",
    "validate_log_level_string",
    # Advanced
    "ColoredFormatter",
    "FormatterFactory",
    "HandlerFactory",
    "LoggerConfigurator",
    "RichFormatter",
    "RichHandlerSettings",
    # Rich features
    "RichFeatureSettings",
    "RichLogger",
]
