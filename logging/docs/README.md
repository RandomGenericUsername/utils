# Dotfiles Logging Module Documentation

**Version:** 0.1.0
**Python:** 3.12+
**Dependencies:** `rich>=13.0.0`

## Overview

The `logging` module is a standalone Python logging library that provides a clean, type-safe interface for creating and managing loggers with enhanced Rich library integration. It offers a simplified facade over Python's standard logging while adding powerful visual features through the Rich library.

## Key Features

- **Simple API**: Single `Log.create_logger()` call for most use cases
- **Rich Integration**: 20+ Rich features (tables, panels, progress bars, syntax highlighting, etc.)
- **Type Safety**: Comprehensive type hints and enums for configuration
- **Graceful Degradation**: Falls back to standard logging when Rich is unavailable
- **Flexible Configuration**: Support for multiple handlers, formatters, and output destinations
- **Factory Pattern**: Extensible handler and formatter registration system
- **Thread-Safe**: Singleton console manager for coordinated Rich output

## Quick Start

```python
from rich_logging import Log, LogLevels

# Create a basic logger
logger = Log.create_logger(
    name="my_app",
    log_level=LogLevels.INFO
)

# Use standard logging methods
logger.info("Application started")
logger.warning("This is a warning")

# Use Rich features
logger.table(
    data=[["Name", "Age"], ["Alice", "30"], ["Bob", "25"]],
    title="User Data"
)

logger.panel("Important message", title="Alert", border_style="red")
```

## Architecture

The module follows a clean layered architecture:

### Core Layer
- **Types & Configuration**: Enums, dataclasses, and type definitions (`core/log_types.py`)
- **Configurator**: Logger setup and management (`core/configurator.py`)
- **Utilities**: Helper functions for formatting and validation (`core/utils.py`)

### Implementation Layer
- **Handlers**: Console and file handlers with factory pattern (`handlers/`)
- **Formatters**: Colored, Rich, and default formatters (`formatters/`)

### Integration Layer
- **Rich Features**: Enhanced logger wrapper with 20+ Rich methods (`rich/rich_logger.py`)
- **Console Manager**: Singleton for shared console access (`rich/rich_console_manager.py`)
- **Feature Settings**: Type-safe Rich configuration (`rich/rich_feature_settings.py`)

### API Layer
- **Facade**: Simplified `Log` class for easy access (`log.py`)
- **Public Exports**: Clean public API through `__init__.py`

## Design Patterns

1. **Facade Pattern**: `Log` class provides simplified interface to complex subsystems
2. **Factory Pattern**: `HandlerFactory`, `FormatterFactory`, `FileHandlerFactory` for extensibility
3. **Singleton Pattern**: `RichConsoleManager` ensures single console instance
4. **Wrapper Pattern**: `RichLogger` wraps standard logger with enhanced methods
5. **Registry Pattern**: Factories use registries for handler/formatter types

## Documentation Structure

```
docs/
├── README.md                          # This file - overview and quick start
├── architecture/
│   ├── overview.md                    # Detailed architecture explanation
│   ├── design_patterns.md             # Design patterns and rationale
│   └── components.md                  # Component breakdown and relationships
├── api/
│   ├── logger.md                      # Log facade and RichLogger API
│   ├── handlers.md                    # Handler types and configuration
│   ├── formatters.md                  # Formatter types and customization
│   ├── types.md                       # Type definitions and enums
│   └── utilities.md                   # Utility functions
├── guides/
│   ├── getting_started.md             # Installation and basic usage
│   ├── configuration.md               # Configuration options and patterns
│   ├── rich_features.md               # Using Rich features
│   ├── file_logging.md                # File handlers and rotation
│   └── advanced_usage.md              # Advanced patterns and customization
├── reference/
│   ├── examples.md                    # Comprehensive examples
│   └── troubleshooting.md             # Common issues and solutions
└── helpers/                           # Investigation helper documents
    ├── README.md
    ├── INTERACTIVE_PROMPT.md
    ├── REQUIREMENTS_CHECKLIST.md
    ├── INVESTIGATION_NOTES.md
    └── SESSION_SUMMARY.md
```

## Public API

### Main Entry Point

- `Log.create_logger()` - Create and configure a logger
- `Log.update()` - Update existing logger configuration

### Logger Classes

- `RichLogger` - Enhanced logger with Rich features
- `LoggerConfigurator` - Logger configuration manager

### Configuration Types

- `LogConfig` - Main logger configuration dataclass
- `LogLevels` - Log level enumeration
- `LogFormatters` - Formatter type enumeration
- `ConsoleHandlers` - Console handler type enumeration
- `FileHandlerTypes` - File handler type enumeration

### Handler Settings

- `RichHandlerSettings` - Rich handler configuration
- `FileHandlerSettings` - Basic file handler configuration
- `RotatingFileHandlerSettings` - Rotating file handler configuration
- `TimedRotatingFileHandlerSettings` - Timed rotating file handler configuration

### Rich Features

- `RichFeatureSettings` - Rich feature configuration
- `RichConsoleManager` - Console management singleton

### Formatters

- `ColoredFormatter` - ANSI color formatter
- `RichFormatter` - Rich markup formatter

## Usage Examples

### Basic Logging

```python
from rich_logging import Log, LogLevels

logger = Log.create_logger(name="app", log_level=LogLevels.DEBUG)
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")
```

### File Logging with Rotation

```python
from rich_logging import Log, LogConfig, FileHandlerTypes
from rich_logging.handlers import RotatingFileHandlerSettings

config = LogConfig(
    log_level=LogLevels.INFO,
    file_handler_type=FileHandlerTypes.ROTATING_FILE,
    file_handler_settings=RotatingFileHandlerSettings(
        filename="app.log",
        max_bytes=10_485_760,  # 10 MB
        backup_count=5
    )
)

logger = Log.create_logger(name="app", config=config)
```

### Rich Features

```python
from rich_logging import Log

logger = Log.create_logger(name="app")

# Display a table
logger.table(
    data=[["Name", "Status"], ["Task 1", "Complete"], ["Task 2", "Pending"]],
    title="Task Status"
)

# Show a panel
logger.panel("Deployment successful!", title="Success", border_style="green")

# Display progress
with logger.progress() as progress:
    task = progress.add_task("Processing...", total=100)
    for i in range(100):
        progress.update(task, advance=1)
```

### Custom Configuration

```python
from rich_logging import (
    Log, LogConfig, LogLevels, LogFormatters, ConsoleHandlers
)
from rich_logging.handlers import RichHandlerSettings
from rich_logging.rich import RichFeatureSettings

config = LogConfig(
    log_level=LogLevels.DEBUG,
    formatter_type=LogFormatters.RICH,
    console_handler_type=ConsoleHandlers.RICH,
    rich_handler_settings=RichHandlerSettings(
        show_time=True,
        show_level=True,
        show_path=True,
        markup=True
    ),
    rich_feature_settings=RichFeatureSettings(
        panel_border_style="cyan",
        table_show_lines=True,
        syntax_theme="dracula"
    )
)

logger = Log.create_logger(name="app", config=config)
```

## Next Steps

- **Getting Started**: See [guides/getting_started.md](guides/getting_started.md)
- **API Reference**: See [api/](api/) directory for detailed API documentation
- **Architecture**: See [architecture/](architecture/) directory for design details
- **Examples**: See [reference/examples.md](reference/examples.md) for comprehensive examples

## Contributing

This module follows strict design principles:

1. **Separation of Concerns**: Clean boundaries between layers
2. **Type Safety**: Comprehensive type hints throughout
3. **Graceful Degradation**: Always provide fallbacks
4. **Extensibility**: Use factory pattern for new handlers/formatters
5. **Documentation**: Document all public APIs and design decisions
