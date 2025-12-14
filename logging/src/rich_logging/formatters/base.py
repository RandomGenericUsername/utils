"""Base formatter configuration and factory."""

import logging as stdlib_logging
from abc import ABC, abstractmethod

from ..core.log_types import (
    LogFormatters,
    LogFormatterStyleChoices,
)


class BaseFormatterConfig(ABC):
    """Base class for formatter configurations."""

    def __init__(self, format_str: str, style: LogFormatterStyleChoices):
        """
        Initialize formatter configuration.

        Args:
            format_str: Format string for log messages
            style: Format style (%, {, $)
        """
        self.format_str = format_str
        self.style = style

    @abstractmethod
    def create(self) -> stdlib_logging.Formatter:
        """
        Create the formatter instance.

        Returns:
            Configured stdlib_logging.Formatter instance
        """
        pass


class FormatterFactory:
    """Factory for creating formatters based on type."""

    # Registry mapping formatter types to config classes
    _registry: dict[LogFormatters, type[BaseFormatterConfig]] = {}

    @classmethod
    def register(
        cls,
        formatter_type: LogFormatters,
        config_class: type[BaseFormatterConfig],
    ):
        """
        Register a formatter config class.

        Args:
            formatter_type: Formatter type enum
            config_class: Config class to register
        """
        cls._registry[formatter_type] = config_class

    @classmethod
    def create(
        cls,
        formatter_type: LogFormatters,
        format_str: str,
        style: LogFormatterStyleChoices,
        **kwargs,
    ) -> stdlib_logging.Formatter:
        """
        Create a formatter instance.

        Args:
            formatter_type: Type of formatter to create
            format_str: Format string for log messages
            style: Format style (%, {, $)
            **kwargs: Additional arguments for specific formatter types

        Returns:
            Configured stdlib_logging.Formatter instance

        Raises:
            ValueError: If formatter type is not registered
        """
        if formatter_type not in cls._registry:
            raise ValueError(f"Unknown formatter type: {formatter_type}")

        config_class = cls._registry[formatter_type]
        config = config_class(format_str, style, **kwargs)
        return config.create()
