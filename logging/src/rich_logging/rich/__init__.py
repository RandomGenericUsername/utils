"""Rich integration components.

This module contains all Rich-related functionality:
- RichLogger: Enhanced logger with Rich features
- RichConsoleManager: Singleton console manager for sharing consoles
- RichFeatureSettings: Type-safe configuration for Rich features
"""

from .rich_console_manager import RichConsoleManager
from .rich_feature_settings import RichFeatureSettings
from .rich_logger import RichLogger

__all__ = [
    "RichLogger",
    "RichConsoleManager",
    "RichFeatureSettings",
]
