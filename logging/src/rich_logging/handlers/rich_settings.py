"""Rich handler settings model."""

from collections.abc import Callable, Iterable
from dataclasses import dataclass

try:
    from rich.console import Console
    from rich.highlighter import Highlighter
    from rich.text import Text

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    # Type stubs for when Rich is not available
    Text = object
    Highlighter = object
    Console = object


@dataclass
class RichHandlerSettings:
    """
    Configuration settings for RichHandler.

    This dataclass provides type-safe configuration for all RichHandler options
    with proper defaults and validation.
    """

    # Core display options
    show_time: bool = True
    """Whether to show timestamp in log output."""

    show_level: bool = True
    """Whether to show log level (INFO, WARNING, etc.)."""

    show_path: bool = True
    """Whether to show file path and line number."""

    markup: bool = False
    """Whether to enable Rich markup processing in log messages."""

    # Time formatting
    omit_repeated_times: bool = True
    """Whether to omit timestamp if it's the same as the previous log entry."""

    log_time_format: str | Callable = "[%x %X]"
    """Time format string or callable for timestamp display."""

    # Path options
    enable_link_path: bool = True
    """Whether to make file paths clickable (if terminal supports it)."""

    # Highlighting
    highlighter: Highlighter | None = None
    """Custom highlighter instance for log messages."""

    keywords: list[str] | None = None
    """List of keywords to highlight in log messages."""

    # Traceback configuration
    rich_tracebacks: bool = False
    """Whether to use Rich for beautiful traceback formatting."""

    tracebacks_width: int | None = None
    """Width for traceback display (None for auto-width)."""

    tracebacks_code_width: int = 88
    """Width for code snippets in tracebacks."""

    tracebacks_extra_lines: int = 3
    """Number of extra lines of context around error in tracebacks."""

    tracebacks_theme: str | None = None
    """Syntax highlighting theme for tracebacks (e.g., 'monokai',
    'github-dark')."""

    tracebacks_word_wrap: bool = True
    """Whether to word wrap long lines in tracebacks."""

    tracebacks_show_locals: bool = False
    """Whether to show local variables in tracebacks."""

    tracebacks_suppress: Iterable[str | object] = ()
    """Modules or paths to suppress from tracebacks."""

    tracebacks_max_frames: int = 100
    """Maximum number of frames to show in tracebacks."""

    # Local variable display (when tracebacks_show_locals=True)
    locals_max_length: int = 10
    """Maximum number of items to show in collections."""

    locals_max_string: int = 80
    """Maximum string length for local variables."""

    # Console instance (for sharing)
    console: Console | None = None
    """Optional console instance to use (None creates default console)."""

    def to_dict(self) -> dict:
        """
        Convert settings to dictionary for RichHandler constructor.

        Returns:
            Dictionary of settings compatible with RichHandler
        """
        # Convert dataclass to dict, excluding None values for optional
        # parameters
        result = {}

        for field_name, field_value in self.__dict__.items():
            if field_value is not None:
                result[field_name] = field_value

        return result

    def __post_init__(self):
        """Validate settings after initialization."""
        if self.keywords is not None and not isinstance(self.keywords, list):
            raise TypeError("keywords must be a list of strings or None")

        if self.keywords is not None:
            for keyword in self.keywords:
                if not isinstance(keyword, str):
                    raise TypeError("All keywords must be strings")

        if self.tracebacks_code_width <= 0:
            raise ValueError("tracebacks_code_width must be positive")

        if self.tracebacks_extra_lines < 0:
            raise ValueError("tracebacks_extra_lines must be non-negative")

        if self.tracebacks_max_frames <= 0:
            raise ValueError("tracebacks_max_frames must be positive")

        if self.locals_max_length <= 0:
            raise ValueError("locals_max_length must be positive")

        if self.locals_max_string <= 0:
            raise ValueError("locals_max_string must be positive")
