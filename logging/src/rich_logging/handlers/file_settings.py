"""File handler settings models."""

from dataclasses import dataclass


@dataclass
class FileHandlerSettings:
    """Settings for basic file handler."""

    filename: str
    """Path to the log file."""

    mode: str = "a"
    """File open mode ('a' for append, 'w' for write)."""

    encoding: str = "utf-8"
    """File encoding."""

    delay: bool = False
    """Whether to delay file opening until first log message."""


@dataclass
class RotatingFileHandlerSettings:
    """Settings for rotating file handler."""

    filename: str
    """Path to the log file."""

    max_bytes: int = 10_485_760  # 10MB
    """Maximum file size in bytes before rotation."""

    backup_count: int = 5
    """Number of backup files to keep."""

    mode: str = "a"
    """File open mode ('a' for append, 'w' for write)."""

    encoding: str = "utf-8"
    """File encoding."""

    delay: bool = False
    """Whether to delay file opening until first log message."""


@dataclass
class TimedRotatingFileHandlerSettings:
    """Settings for timed rotating file handler."""

    filename: str
    """Path to the log file."""

    when: str = "midnight"
    """When to rotate: 'S', 'M', 'H', 'D', 'midnight', 'W0'-'W6'."""

    interval: int = 1
    """Interval between rotations."""

    backup_count: int = 7
    """Number of backup files to keep."""

    encoding: str = "utf-8"
    """File encoding."""

    delay: bool = False
    """Whether to delay file opening until first log message."""

    utc: bool = False
    """Whether to use UTC time for rotation."""


# Union type for all file handler settings
BaseFileHandlerSettings = (
    FileHandlerSettings
    | RotatingFileHandlerSettings
    | TimedRotatingFileHandlerSettings
)
