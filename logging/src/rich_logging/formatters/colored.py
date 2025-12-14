"""Colored formatter implementation."""

import logging as stdlib_logging
import rich_logging

from ..core.log_types import (
    ColoredFormatterColors,
    LogFormatters,
    LogFormatterStyleChoices,
)
from .base import (
    BaseFormatterConfig,
    FormatterFactory,
)


class ColoredFormatter(stdlib_logging.Formatter):
    """Formatter that adds ANSI colors based on log level."""

    def __init__(
        self,
        fmt: str | None = None,
        datefmt: str | None = None,
        style: str = "%",
        colors: type[ColoredFormatterColors] | None = None,
    ):
        """
        Initialize colored formatter.

        Args:
            fmt: Format string
            datefmt: Date format string
            style: Format style (%, {, $)
            colors: Colors class to use (defaults to ColoredFormatterColors)
        """
        super().__init__(fmt, datefmt, style)
        self.colors = colors or ColoredFormatterColors

    def format(self, record):
        """Format the log record with colors."""
        # Get the original formatted message
        log_message = super().format(record)

        # Add color based on log level
        color = getattr(self.colors, record.levelname, "")
        reset = getattr(self.colors, "RESET", "")
        return f"{color}{log_message}{reset}"


class ColoredFormatterConfig(BaseFormatterConfig):
    """Configuration for colored formatter."""

    def __init__(
        self,
        format_str: str,
        style: LogFormatterStyleChoices,
        colors: type[ColoredFormatterColors] | None = None,
    ):
        """
        Initialize colored formatter configuration.

        Args:
            format_str: Format string for log messages
            style: Format style (%, {, $)
            colors: Colors class to use (defaults to ColoredFormatterColors)
        """
        super().__init__(format_str, style)
        self.colors = colors or ColoredFormatterColors

    def create(self) -> stdlib_logging.Formatter:
        """Create a ColoredFormatter instance."""
        return ColoredFormatter(
            fmt=self.format_str,
            style=self.style.value,
            colors=self.colors,
        )


class DefaultFormatterConfig(BaseFormatterConfig):
    """Configuration for default (standard) formatter."""

    def __init__(
        self,
        format_str: str,
        style: LogFormatterStyleChoices,
        **_kwargs,  # Accept but ignore extra kwargs like 'colors'
    ):
        """
        Initialize default formatter configuration.

        Args:
            format_str: Format string for log messages
            style: Format style (%, {, $)
            **kwargs: Extra arguments (ignored for default formatter)
        """
        super().__init__(format_str, style)

    def create(self) -> stdlib_logging.Formatter:
        """Create a standard stdlib_logging.Formatter instance."""
        return stdlib_logging.Formatter(
            fmt=self.format_str,
            style=self.style.value,
        )


# Register formatters
FormatterFactory.register(LogFormatters.COLORED, ColoredFormatterConfig)
FormatterFactory.register(LogFormatters.DEFAULT, DefaultFormatterConfig)
