"""
Minimal logging types for Pydantic models.
"""

import logging as stdlib_logging
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..handlers.file_settings import (
        BaseFileHandlerSettings,
    )
    from ..handlers.rich_settings import RichHandlerSettings
    from ..rich.rich_feature_settings import RichFeatureSettings
    from ..rich.rich_logger import RichLogger

    # Type alias for enhanced logger (only available during type checking)
    EnhancedLogger = stdlib_logging.Logger | RichLogger


class LogLevelOptions:
    """Log level options."""

    debug: list[str] = ["debug", "d", "D"]
    info: list[str] = ["info", "i", "I"]
    warning: list[str] = ["warning", "w", "W"]
    error: list[str] = ["error", "e", "E"]
    critical: list[str] = ["critical", "c", "C"]


class LogLevels(Enum):
    """Log level enumeration."""

    DEBUG = stdlib_logging.DEBUG
    INFO = stdlib_logging.INFO
    WARNING = stdlib_logging.WARNING
    ERROR = stdlib_logging.ERROR
    CRITICAL = stdlib_logging.CRITICAL


class VerbosityToLogLevel:
    """Map verbosity level to log level."""

    mapping = {
        1: LogLevels.WARNING,
        2: LogLevels.INFO,
        3: LogLevels.DEBUG,
    }


class LogFormatterStyleChoices(Enum):
    """Basic logger formatter styles."""

    PERCENT = "%"
    BRACE = "{"
    DOLLAR = "$"


class LogFormatters(Enum):
    DEFAULT = "default"
    COLORED = "colored"
    RICH = "rich"


class ConsoleHandlers(Enum):
    DEFAULT = "default"
    RICH = "rich"


class FileHandlerTypes(Enum):
    """File handler types."""

    FILE = "file"
    ROTATING_FILE = "rotating_file"
    TIMED_ROTATING_FILE = "timed_rotating_file"


@dataclass
class FileHandlerSpec:
    """Specification for a file handler."""

    handler_type: FileHandlerTypes
    config: "BaseFileHandlerSettings"
    formatter_override: LogFormatters | None = None
    format_override: str | None = None


@dataclass
class ColoredFormatterColors:
    DEBUG: str = "\033[36m"  # Cyan
    INFO: str = "\033[32m"  # Green
    WARNING: str = "\033[33m"  # Yellow
    ERROR: str = "\033[31m"  # Red
    CRITICAL: str = "\033[35m"  # Magenta
    RESET: str = "\033[0m"  # Reset color


@dataclass
class LogConfig:
    log_level: LogLevels
    formatter_style: LogFormatterStyleChoices | None = None
    format: str | None = None
    formatter_type: LogFormatters | None = None
    name: str | None = None
    colors: ColoredFormatterColors | None = None
    console_handler: ConsoleHandlers = ConsoleHandlers.DEFAULT
    handler_config: "RichHandlerSettings | None" = (
        None  # Console handler configuration
    )
    file_handlers: list[FileHandlerSpec] | None = (
        None  # File handler specifications
    )
    rich_features: "RichFeatureSettings | None" = (
        None  # Rich features configuration
    )
