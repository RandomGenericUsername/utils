"""Rich formatter implementation."""

import logging as stdlib_logging
import rich_logging

from ..core.log_types import (
    LogFormatters,
    LogFormatterStyleChoices,
)
from .base import (
    BaseFormatterConfig,
    FormatterFactory,
)

try:
    from rich.console import Console

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class RichFormatter(stdlib_logging.Formatter):
    """Formatter that outputs Rich markup for use with regular handlers."""

    def __init__(
        self,
        fmt: str | None = None,
        datefmt: str | None = None,
        style: str = "%",
        level_colors: dict[str, str] | None = None,
    ):
        """
        Initialize Rich formatter.

        Args:
            fmt: Format string (can include Rich markup)
            datefmt: Date format string
            style: Format style (%, {, $)
            level_colors: Custom color mapping for log levels
        """
        super().__init__(fmt, datefmt, style)
        self.level_colors = level_colors or {
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "magenta",
        }

    def format(self, record):
        """Format the log record with Rich markup, then render to plain
        text."""
        if not RICH_AVAILABLE:
            # Fallback to standard formatting if Rich not available
            return super().format(record)

        # Get the original formatted message
        log_message = super().format(record)

        # If the format string doesn't contain Rich markup for level,
        # we can auto-add colors to the level name
        if (
            "[" not in log_message
            or f"[{self.level_colors.get(record.levelname, '')}]"
            not in log_message
        ):
            # Auto-colorize level name if not already colored in format string
            level_color = self.level_colors.get(record.levelname, "white")
            log_message = log_message.replace(
                record.levelname,
                f"[{level_color}]{record.levelname}[/{level_color}]",
                1,  # Only replace first occurrence
            )

        # Render Rich markup to ANSI codes for regular handlers
        try:
            console = Console(file=None, force_terminal=True)
            with console.capture() as capture:
                console.print(log_message, end="")
            return capture.get()
        except Exception:
            # If Rich rendering fails, return the markup as-is
            return log_message


class RichFormatterConfig(BaseFormatterConfig):
    """Configuration for Rich formatter."""

    def __init__(
        self,
        format_str: str,
        style: LogFormatterStyleChoices,
        level_colors: dict[str, str] | None = None,
        **_kwargs,  # Accept but ignore extra kwargs
    ):
        """
        Initialize Rich formatter configuration.

        Args:
            format_str: Format string for log messages (can include Rich
                markup)
            style: Format style (%, {, $)
            level_colors: Custom color mapping for log levels
            **kwargs: Extra arguments (ignored)
        """
        super().__init__(format_str, style)
        self.level_colors = level_colors

    def create(self) -> stdlib_logging.Formatter:
        """Create a RichFormatter instance."""
        if not RICH_AVAILABLE:
            # Graceful fallback to standard formatter
            return stdlib_logging.Formatter(
                fmt=self.format_str,
                style=self.style.value,
            )

        return RichFormatter(
            fmt=self.format_str,
            style=self.style.value,
            level_colors=self.level_colors,
        )


# Register Rich formatter
FormatterFactory.register(LogFormatters.RICH, RichFormatterConfig)
