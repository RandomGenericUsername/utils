"""Logger configurator for managing logger setup and updates."""

import logging as stdlib_logging

from ..formatters import FormatterFactory
from ..handlers import HandlerFactory
from ..handlers.file import FileHandlerFactory
from .log_types import (
    ConsoleHandlers,
    FileHandlerSpec,
    LogConfig,
)


class LoggerConfigurator:
    """Manages configuration of a logger instance."""

    def __init__(self, logger: stdlib_logging.Logger):
        """
        Initialize configurator for a logger.

        Args:
            logger: Logger instance to configure
        """
        self.logger = logger
        self.config: LogConfig | None = None

    def configure(self, config: LogConfig):
        """
        Configure the logger with the given configuration.

        Args:
            config: Logger configuration
        """
        # Remove existing handlers
        self._remove_handlers()

        # Set log level
        self.logger.setLevel(config.log_level.value)

        # Create formatter
        formatter = FormatterFactory.create(
            formatter_type=config.formatter_type,
            format_str=config.format,
            style=config.formatter_style,
            colors=config.colors,
        )

        # Create handler with formatter
        # Pass handler-specific configuration if available
        handler_kwargs = {}
        if hasattr(config, "handler_config") and config.handler_config:
            # Expect RichHandlerSettings object for RICH handler
            if config.console_handler == ConsoleHandlers.RICH:
                handler_kwargs["settings"] = config.handler_config
            else:
                # For other handlers, pass as kwargs (if they support it)
                if isinstance(config.handler_config, dict):
                    handler_kwargs.update(config.handler_config)

        # Add logger name for console sharing
        if config.console_handler == ConsoleHandlers.RICH:
            handler_kwargs["logger_name"] = config.name

        handler = HandlerFactory.create(
            handler_type=config.console_handler,
            formatter=formatter,
            **handler_kwargs,
        )

        # Add console handler to logger
        self.logger.addHandler(handler)

        # Create file handlers if specified
        if config.file_handlers:
            for file_spec in config.file_handlers:
                # Create formatter for this file handler
                file_formatter = self._create_file_formatter(file_spec, config)

                # Create file handler
                file_handler = FileHandlerFactory.create(
                    handler_type=file_spec.handler_type,
                    formatter=file_formatter,
                    config=file_spec.config,
                )
                self.logger.addHandler(file_handler)

        # Store configuration
        self.config = config

    def update(self, **kwargs) -> LogConfig:
        """
        Update configuration with new values.

        Args:
            **kwargs: Configuration values to update

        Returns:
            New LogConfig with updated values

        Raises:
            RuntimeError: If configurator has not been configured yet
        """
        if self.config is None:
            raise RuntimeError(
                "Configurator must be configured before updating"
            )

        # Merge with existing config
        config_dict = {
            "name": kwargs.get("name", self.config.name),
            "log_level": kwargs.get("log_level", self.config.log_level),
            "formatter_style": kwargs.get(
                "formatter_style", self.config.formatter_style
            ),
            "format": kwargs.get("format", self.config.format),
            "formatter_type": kwargs.get(
                "formatter_type", self.config.formatter_type
            ),
            "colors": kwargs.get("colors", self.config.colors),
            "console_handler": kwargs.get(
                "console_handler_type", self.config.console_handler
            ),
            "handler_config": kwargs.get(
                "handler_config", self.config.handler_config
            ),
            "file_handlers": kwargs.get(
                "file_handlers", self.config.file_handlers
            ),
            "rich_features": kwargs.get(
                "rich_features", self.config.rich_features
            ),
        }

        return LogConfig(**config_dict)

    def _create_file_formatter(
        self, file_spec: FileHandlerSpec, config: LogConfig
    ) -> stdlib_logging.Formatter:
        """
        Create formatter for a file handler, respecting overrides.

        Args:
            file_spec: File handler specification
            config: Global logger configuration

        Returns:
            Configured formatter for the file handler
        """
        # Use per-handler overrides or fall back to global config
        formatter_type = file_spec.formatter_override or config.formatter_type
        format_str = file_spec.format_override or config.format

        return FormatterFactory.create(
            formatter_type=formatter_type,
            format_str=format_str,
            style=config.formatter_style,
            colors=config.colors,
        )

    def _remove_handlers(self):
        """Remove all handlers from the logger."""
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
