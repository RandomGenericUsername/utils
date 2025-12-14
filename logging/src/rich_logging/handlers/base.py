"""Base handler configuration and factory."""

import logging as stdlib_logging
import rich_logging
from abc import ABC, abstractmethod

from ..core.log_types import ConsoleHandlers


class BaseHandlerConfig(ABC):
    """Base class for handler configurations."""

    def __init__(self, formatter: stdlib_logging.Formatter):
        """
        Initialize handler configuration.

        Args:
            formatter: Formatter to attach to the handler
        """
        self.formatter = formatter

    @abstractmethod
    def create(self) -> stdlib_logging.Handler:
        """
        Create and configure the handler instance.

        Returns:
            Configured stdlib_logging.Handler instance
        """
        pass


class HandlerFactory:
    """Factory for creating handlers based on type."""

    # Registry mapping handler types to config classes
    _registry: dict[ConsoleHandlers, type[BaseHandlerConfig]] = {}

    @classmethod
    def register(
        cls,
        handler_type: ConsoleHandlers,
        config_class: type[BaseHandlerConfig],
    ):
        """
        Register a handler config class.

        Args:
            handler_type: Handler type enum
            config_class: Config class to register
        """
        cls._registry[handler_type] = config_class

    @classmethod
    def create(
        cls,
        handler_type: ConsoleHandlers,
        formatter: stdlib_logging.Formatter,
        **kwargs,
    ) -> stdlib_logging.Handler:
        """
        Create a handler instance.

        Args:
            handler_type: Type of handler to create
            formatter: Formatter to attach to the handler
            **kwargs: Additional arguments for specific handler types
                     For RichHandler: settings=RichHandlerSettings instance

        Returns:
            Configured stdlib_logging.Handler instance

        Raises:
            ValueError: If handler type is not registered
        """
        if handler_type not in cls._registry:
            raise ValueError(f"Unknown handler type: {handler_type}")

        config_class = cls._registry[handler_type]

        # Special handling for RichHandlerConfig
        if handler_type == ConsoleHandlers.RICH:
            # Expect 'settings' key for RichHandlerSettings
            settings = kwargs.get("settings")
            config = config_class(formatter, settings=settings)
        else:
            config = config_class(formatter, **kwargs)

        return config.create()
