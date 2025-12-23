"""
Unit tests for FormatterFactory.

Tests formatter creation in isolation.
"""

import logging as stdlib_logging
import pytest

from rich_logging.formatters import FormatterFactory
from rich_logging.core.log_types import (
    LogFormatters,
    LogFormatterStyleChoices,
)


class TestFormatterFactory:
    """Unit tests for FormatterFactory."""

    def test_create_default_formatter(self):
        """Unit: Create default formatter."""
        formatter = FormatterFactory.create(
            LogFormatters.DEFAULT,
            format_str="%(levelname)s - %(message)s",
            style=LogFormatterStyleChoices.PERCENT
        )

        assert isinstance(formatter, stdlib_logging.Formatter)
        # Default formatter should have a format string
        assert formatter._fmt is not None

    def test_create_colored_formatter(self):
        """Unit: Create colored formatter."""
        formatter = FormatterFactory.create(
            LogFormatters.COLORED,
            format_str="%(levelname)s - %(message)s",
            style=LogFormatterStyleChoices.PERCENT
        )

        assert isinstance(formatter, stdlib_logging.Formatter)

    def test_create_rich_formatter(self):
        """Unit: Create Rich formatter."""
        formatter = FormatterFactory.create(
            LogFormatters.RICH,
            format_str="%(message)s",
            style=LogFormatterStyleChoices.PERCENT
        )

        # Rich formatter is a RichFormatter instance
        assert isinstance(formatter, stdlib_logging.Formatter)

    def test_create_formatter_with_brace_style(self):
        """Unit: Create formatter with brace style."""
        formatter = FormatterFactory.create(
            LogFormatters.DEFAULT,
            format_str="{levelname} - {message}",
            style=LogFormatterStyleChoices.BRACE
        )

        assert isinstance(formatter, stdlib_logging.Formatter)
        assert formatter._style._fmt  # Brace style uses _style

    def test_create_formatter_with_dollar_style(self):
        """Unit: Create formatter with dollar style."""
        formatter = FormatterFactory.create(
            LogFormatters.DEFAULT,
            format_str="$levelname - $message",
            style=LogFormatterStyleChoices.DOLLAR
        )

        assert isinstance(formatter, stdlib_logging.Formatter)


class TestFormatterFactoryEdgeCases:
    """Unit tests for FormatterFactory edge cases."""

    def test_create_formatter_invalid_type_raises_error(self):
        """Unit: Invalid formatter type raises error."""
        with pytest.raises((ValueError, AttributeError, KeyError)):
            FormatterFactory.create(
                "INVALID",  # type: ignore
                format_str="%(message)s",
                style=LogFormatterStyleChoices.PERCENT
            )

