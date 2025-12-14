"""Main logging API facade."""

import logging as stdlib_logging
import rich_logging

# Import for type hints
from typing import TYPE_CHECKING

from .core.configurator import LoggerConfigurator
from .core.log_types import (
    ColoredFormatterColors,
    ConsoleHandlers,
    FileHandlerSpec,
    LogConfig,
    LogFormatters,
    LogFormatterStyleChoices,
    LogLevels,
)
from .rich.rich_feature_settings import RichFeatureSettings
from .rich.rich_logger import RichLogger

if TYPE_CHECKING:
    from .handlers.rich_settings import RichHandlerSettings

# These are the officially documented LogRecord attributes
FORMATTER_PLACEHOLDERS = [
    "name",  # Logger name
    "levelno",  # Log level number
    "levelname",  # Log level name
    "pathname",  # Full pathname of source file
    "filename",  # Filename portion of pathname
    "module",  # Module name
    "lineno",  # Source line number
    "funcName",  # Function name
    "created",  # Time when LogRecord was created (timestamp)
    "asctime",  # Human-readable time (created by formatter)
    "msecs",  # Millisecond portion of creation time
    "relativeCreated",  # Time relative to module load
    "thread",  # Thread ID
    "threadName",  # Thread name
    "process",  # Process ID
    "processName",  # Process name
    "message",  # The logged message (formatted msg % args)
]


class Log:
    """Main logging API facade with simplified interface."""

    # Store configurators for each logger
    _configurators: dict[str, LoggerConfigurator] = {}

    @staticmethod
    def create_logger(
        name: str | None = None,
        config: LogConfig | None = None,
        log_level: LogLevels | None = None,
        formatter_style: LogFormatterStyleChoices = (
            LogFormatterStyleChoices.PERCENT
        ),
        format: str = "%(asctime)s | %(levelname)-8s | %(message)s",
        formatter_type: LogFormatters = LogFormatters.DEFAULT,
        colors: type[ColoredFormatterColors] | None = None,
        console_handler_type: ConsoleHandlers = ConsoleHandlers.DEFAULT,
        handler_config: "RichHandlerSettings | None" = None,
        file_handlers: list[FileHandlerSpec] | None = None,
        rich_features: RichFeatureSettings | None = None,
    ) -> RichLogger:
        """
        Create and configure a logger.

        Args:
            name: Logger name
            config: LogConfig object with all settings (if provided,
                individual parameters override config values)
            log_level: Log level (required if config is not provided)
            formatter_style: Format style (%, {, $)
            format: Format string for log messages
            formatter_type: Type of formatter to use
            colors: Color scheme for colored formatter
            console_handler_type: Type of console handler to use
            handler_config: RichHandlerSettings instance for Rich handler
                configuration
            file_handlers: List of file handler specifications

        Returns:
            Configured logger instance

        Examples:
            # Using individual parameters
            logger = Log.create_logger("app", log_level=LogLevels.DEBUG)

            # Using LogConfig object
            config = LogConfig(log_level=LogLevels.DEBUG, ...)
            logger = Log.create_logger("app", config=config)

            # Using config with parameter overrides
            logger = Log.create_logger(
                "app", config=config, log_level=LogLevels.INFO
            )  # overrides config.log_level
        """
        logger = stdlib_logging.getLogger(name)
        configurator = LoggerConfigurator(logger)

        # If config is provided, use it as base and allow individual
        # parameters to override
        if config is not None:
            final_config = LogConfig(
                name=name,  # Always use the provided name parameter
                log_level=(
                    log_level if log_level is not None else config.log_level
                ),
                formatter_style=(
                    formatter_style
                    if formatter_style != LogFormatterStyleChoices.PERCENT
                    else config.formatter_style
                ),
                format=(
                    format
                    if format != "%(asctime)s | %(levelname)-8s | %(message)s"
                    else config.format
                ),
                formatter_type=(
                    formatter_type
                    if formatter_type != LogFormatters.DEFAULT
                    else config.formatter_type
                ),
                colors=colors if colors is not None else config.colors,
                console_handler=(
                    console_handler_type
                    if console_handler_type != ConsoleHandlers.DEFAULT
                    else config.console_handler
                ),
                handler_config=(
                    handler_config
                    if handler_config is not None
                    else config.handler_config
                ),
                file_handlers=(
                    file_handlers
                    if file_handlers is not None
                    else config.file_handlers
                ),
                rich_features=(
                    rich_features
                    if rich_features is not None
                    else config.rich_features
                ),
            )
        else:
            # Create config from individual parameters - log_level is required
            if log_level is None:
                raise ValueError(
                    "log_level is required when config is not provided"
                )

            final_config = LogConfig(
                name=name,
                log_level=log_level,
                formatter_style=formatter_style,
                format=format,
                formatter_type=formatter_type,
                colors=colors,
                console_handler=console_handler_type,
                handler_config=handler_config,
                file_handlers=file_handlers,
                rich_features=rich_features,
            )

        configurator.configure(final_config)
        Log._configurators[name] = configurator

        # Create and return RichLogger wrapper
        rich_settings = final_config.rich_features or RichFeatureSettings()
        return RichLogger(logger, rich_settings)

    @staticmethod
    def update(
        name: str,
        config: LogConfig | None = None,
        log_level: LogLevels | None = None,
        formatter_style: LogFormatterStyleChoices | None = None,
        format: str | None = None,
        formatter_type: LogFormatters | None = None,
        colors: type[ColoredFormatterColors] | None = None,
        console_handler_type: ConsoleHandlers | None = None,
        handler_config: "RichHandlerSettings | None" = None,
        file_handlers: list[FileHandlerSpec] | None = None,
        rich_features: RichFeatureSettings | None = None,
    ) -> RichLogger:
        """
        Update an existing logger's configuration.

        Args:
            name: Logger name
            config: LogConfig object with new settings (if provided,
                individual parameters override config values)
            log_level: New log level (None to keep existing)
            formatter_style: New format style (None to keep existing)
            format: New format string (None to keep existing)
            formatter_type: New formatter type (None to keep existing)
            colors: New color scheme (None to keep existing)
            console_handler_type: New handler type (None to keep existing)
            handler_config: New RichHandlerSettings instance (None to keep
                existing)
            file_handlers: New file handler specifications (None to keep
                existing)

        Returns:
            Updated logger instance

        Raises:
            ValueError: If logger has not been created with create_logger

        Examples:
            # Using individual parameters
            logger = Log.update("app", log_level=LogLevels.DEBUG)

            # Using LogConfig object
            config = LogConfig(log_level=LogLevels.DEBUG, ...)
            logger = Log.update("app", config=config)

            # Using config with parameter overrides
            logger = Log.update(
                "app", config=config, log_level=LogLevels.INFO
            )  # overrides config.log_level
        """
        if name not in Log._configurators:
            raise ValueError(
                f"Logger '{name}' not found. Create it first with "
                f"create_logger()"
            )

        configurator = Log._configurators[name]

        # If config is provided, use it as base for updates
        if config is not None:
            # Start with config values and override with individual parameters
            update_kwargs = {
                "log_level": (
                    log_level if log_level is not None else config.log_level
                ),
                "formatter_style": (
                    formatter_style
                    if formatter_style is not None
                    else config.formatter_style
                ),
                "format": format if format is not None else config.format,
                "formatter_type": (
                    formatter_type
                    if formatter_type is not None
                    else config.formatter_type
                ),
                "colors": colors if colors is not None else config.colors,
                "console_handler_type": (
                    console_handler_type
                    if console_handler_type is not None
                    else config.console_handler
                ),
                "handler_config": (
                    handler_config
                    if handler_config is not None
                    else config.handler_config
                ),
                "file_handlers": (
                    file_handlers
                    if file_handlers is not None
                    else config.file_handlers
                ),
                "rich_features": (
                    rich_features
                    if rich_features is not None
                    else config.rich_features
                ),
            }
        else:
            # Build kwargs for update, excluding None values
            update_kwargs = {}
            if log_level is not None:
                update_kwargs["log_level"] = log_level

            if formatter_style is not None:
                update_kwargs["formatter_style"] = formatter_style
            if format is not None:
                update_kwargs["format"] = format
            if formatter_type is not None:
                update_kwargs["formatter_type"] = formatter_type
            if colors is not None:
                update_kwargs["colors"] = colors
            if console_handler_type is not None:
                update_kwargs["console_handler_type"] = console_handler_type
            if handler_config is not None:
                update_kwargs["handler_config"] = handler_config
            if file_handlers is not None:
                update_kwargs["file_handlers"] = file_handlers
            if rich_features is not None:
                update_kwargs["rich_features"] = rich_features

        # Update configuration
        new_config = configurator.update(**update_kwargs)
        configurator.configure(new_config)

        # Create and return RichLogger wrapper
        rich_settings = new_config.rich_features or RichFeatureSettings()
        return RichLogger(configurator.logger, rich_settings)
