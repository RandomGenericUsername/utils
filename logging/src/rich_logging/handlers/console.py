"""Console handler implementations."""

import logging as stdlib_logging
import rich_logging

from ..core.log_types import ConsoleHandlers
from ..rich.rich_console_manager import console_manager
from .base import BaseHandlerConfig, HandlerFactory
from .rich_settings import RichHandlerSettings

try:
    from rich.logging import RichHandler

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class StreamHandlerConfig(BaseHandlerConfig):
    """Configuration for standard stream handler."""

    def create(self) -> stdlib_logging.StreamHandler:
        """Create a StreamHandler instance."""
        handler = stdlib_logging.StreamHandler()
        handler.setFormatter(self.formatter)
        return handler


class RichHandlerConfig(BaseHandlerConfig):
    """Configuration for Rich handler."""

    def __init__(
        self,
        formatter: stdlib_logging.Formatter,
        settings: RichHandlerSettings | None = None,
        logger_name: str = None,
    ):
        """
        Initialize Rich handler configuration.

        Args:
            formatter: Formatter to attach (may be ignored by Rich's
                native formatting)
            settings: RichHandlerSettings instance (None creates default
                settings)
            logger_name: Name of the logger (for console sharing)
        """
        super().__init__(formatter)
        self.logger_name = logger_name

        if isinstance(settings, RichHandlerSettings):
            self.settings = settings
        elif settings is None:
            # Create default settings
            self.settings = RichHandlerSettings()
        else:
            raise TypeError(
                f"settings must be RichHandlerSettings or None, got "
                f"{type(settings)}"
            )

    def create(self) -> stdlib_logging.Handler:
        """
        Create a RichHandler instance.

        Returns:
            RichHandler if available, otherwise StreamHandler as fallback

        Note:
            Falls back to StreamHandler if Rich is not installed
        """
        if RICH_AVAILABLE:
            # Convert settings to dict and pass to RichHandler
            handler_kwargs = self.settings.to_dict()
            handler = RichHandler(**handler_kwargs)

            # Register console with manager for sharing
            if self.logger_name and hasattr(handler, "console"):
                console_manager.register_console(
                    self.logger_name, handler.console
                )
        else:
            # Graceful fallback to standard handler
            handler = stdlib_logging.StreamHandler()

        # Note: RichHandler does its own formatting, so we create a
        # minimal formatter that just returns the message to avoid double
        # formatting
        if RICH_AVAILABLE:
            # Create a minimal formatter that just returns the message
            minimal_formatter = stdlib_logging.Formatter("%(message)s")
            handler.setFormatter(minimal_formatter)
        else:
            # For fallback StreamHandler, use the provided formatter
            handler.setFormatter(self.formatter)

        return handler


# Register handlers
HandlerFactory.register(ConsoleHandlers.DEFAULT, StreamHandlerConfig)
HandlerFactory.register(ConsoleHandlers.RICH, RichHandlerConfig)
