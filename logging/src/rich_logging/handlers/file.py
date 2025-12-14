"""File handler implementations."""

import logging as stdlib_logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

from ..core.log_types import FileHandlerTypes
from .base import BaseHandlerConfig
from .file_settings import (
    BaseFileHandlerSettings,
    FileHandlerSettings,
    RotatingFileHandlerSettings,
    TimedRotatingFileHandlerSettings,
)


class FileHandlerConfig(BaseHandlerConfig):
    """Configuration for basic file handler."""

    def __init__(
        self, formatter: stdlib_logging.Formatter, settings: FileHandlerSettings
    ):
        """
        Initialize file handler configuration.

        Args:
            formatter: Formatter to attach to the handler
            settings: FileHandlerSettings instance
        """
        super().__init__(formatter)
        self.settings = settings

    def create(self) -> stdlib_logging.FileHandler:
        """Create a FileHandler instance."""
        handler = stdlib_logging.FileHandler(
            filename=self.settings.filename,
            mode=self.settings.mode,
            encoding=self.settings.encoding,
            delay=self.settings.delay,
        )
        handler.setFormatter(self.formatter)
        return handler


class RotatingFileHandlerConfig(BaseHandlerConfig):
    """Configuration for rotating file handler."""

    def __init__(
        self,
        formatter: stdlib_logging.Formatter,
        settings: RotatingFileHandlerSettings,
    ):
        """
        Initialize rotating file handler configuration.

        Args:
            formatter: Formatter to attach to the handler
            settings: RotatingFileHandlerSettings instance
        """
        super().__init__(formatter)
        self.settings = settings

    def create(self) -> RotatingFileHandler:
        """Create a RotatingFileHandler instance."""
        handler = RotatingFileHandler(
            filename=self.settings.filename,
            maxBytes=self.settings.max_bytes,
            backupCount=self.settings.backup_count,
            mode=self.settings.mode,
            encoding=self.settings.encoding,
            delay=self.settings.delay,
        )
        handler.setFormatter(self.formatter)
        return handler


class TimedRotatingFileHandlerConfig(BaseHandlerConfig):
    """Configuration for timed rotating file handler."""

    def __init__(
        self,
        formatter: stdlib_logging.Formatter,
        settings: TimedRotatingFileHandlerSettings,
    ):
        """
        Initialize timed rotating file handler configuration.

        Args:
            formatter: Formatter to attach to the handler
            settings: TimedRotatingFileHandlerSettings instance
        """
        super().__init__(formatter)
        self.settings = settings

    def create(self) -> TimedRotatingFileHandler:
        """Create a TimedRotatingFileHandler instance."""
        handler = TimedRotatingFileHandler(
            filename=self.settings.filename,
            when=self.settings.when,
            interval=self.settings.interval,
            backupCount=self.settings.backup_count,
            encoding=self.settings.encoding,
            delay=self.settings.delay,
            utc=self.settings.utc,
        )
        handler.setFormatter(self.formatter)
        return handler


class FileHandlerFactory:
    """Factory for creating file handlers."""

    # Registry mapping file handler types to config classes
    _registry: dict[FileHandlerTypes, type[BaseHandlerConfig]] = {}

    @classmethod
    def register(
        cls,
        handler_type: FileHandlerTypes,
        config_class: type[BaseHandlerConfig],
    ):
        """
        Register a file handler config class.

        Args:
            handler_type: File handler type enum
            config_class: Config class to register
        """
        cls._registry[handler_type] = config_class

    @classmethod
    def create(
        cls,
        handler_type: FileHandlerTypes,
        formatter: stdlib_logging.Formatter,
        config: BaseFileHandlerSettings,
    ) -> stdlib_logging.Handler:
        """
        Create a file handler instance.

        Args:
            handler_type: Type of file handler to create
            formatter: Formatter to attach to the handler
            config: File handler settings

        Returns:
            Configured stdlib_logging.Handler instance

        Raises:
            ValueError: If handler type is not registered
        """
        if handler_type not in cls._registry:
            raise ValueError(f"Unknown file handler type: {handler_type}")

        config_class = cls._registry[handler_type]
        handler_config = config_class(formatter, config)
        return handler_config.create()


# Register file handlers
FileHandlerFactory.register(FileHandlerTypes.FILE, FileHandlerConfig)
FileHandlerFactory.register(
    FileHandlerTypes.ROTATING_FILE, RotatingFileHandlerConfig
)
FileHandlerFactory.register(
    FileHandlerTypes.TIMED_ROTATING_FILE, TimedRotatingFileHandlerConfig
)
