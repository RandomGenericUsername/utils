"""Rich console management for shared console access across logging and
Rich features."""

import threading
from typing import Optional

try:
    from rich.console import Console

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    Console = None


class RichConsoleManager:
    """
    Manages shared Rich console instances for coordinated output.

    Ensures that logging output and Rich features use the same console
    to prevent conflicts and maintain consistent formatting.
    """

    _instance: Optional["RichConsoleManager"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "RichConsoleManager":
        """Singleton pattern to ensure single console manager."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize console manager."""
        if not hasattr(self, "_initialized"):
            self._consoles: dict[str, Console] = {}
            self._console_lock = threading.Lock()
            self._default_console: Console | None = None
            self._initialized = True

    def register_console(self, logger_name: str, console: Console) -> None:
        """
        Register a console for a specific logger.

        Args:
            logger_name: Name of the logger
            console: Rich Console instance to register
        """
        if not RICH_AVAILABLE:
            return

        with self._console_lock:
            self._consoles[logger_name] = console

    def get_console(self, logger_name: str) -> Console | None:
        """
        Get the console for a specific logger.

        Args:
            logger_name: Name of the logger

        Returns:
            Console instance if available, None otherwise
        """
        if not RICH_AVAILABLE:
            return None

        with self._console_lock:
            # Try to get logger-specific console first
            if logger_name in self._consoles:
                return self._consoles[logger_name]

            # Fall back to default console
            if self._default_console is None:
                self._default_console = Console()

            return self._default_console

    def remove_console(self, logger_name: str) -> None:
        """
        Remove console registration for a logger.

        Args:
            logger_name: Name of the logger
        """
        with self._console_lock:
            self._consoles.pop(logger_name, None)

    def has_console(self, logger_name: str) -> bool:
        """
        Check if a console is registered for a logger.

        Args:
            logger_name: Name of the logger

        Returns:
            True if console is registered, False otherwise
        """
        if not RICH_AVAILABLE:
            return False

        with self._console_lock:
            return logger_name in self._consoles

    def clear_all(self) -> None:
        """Clear all registered consoles."""
        with self._console_lock:
            self._consoles.clear()
            self._default_console = None


# Global console manager instance
console_manager = RichConsoleManager()
