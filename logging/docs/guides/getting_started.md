# Getting Started

## Installation

The logging module is a standalone uv project. To use it in your project:

### As a Dependency

Add to your `pyproject.toml`:

```toml
[project]
dependencies = [
    "logging @ file:///path/to/src/common/modules/logging"
]
```

### Development Installation

```bash
cd src/common/modules/logging
uv sync
```

## Requirements

- **Python**: 3.12 or higher
- **Dependencies**: `rich>=13.0.0`

The module gracefully degrades if Rich is not available, falling back to standard Python logging.

## Quick Start

### 1. Basic Logging

The simplest way to get started:

```python
from rich_logging import Log, LogLevels

# Create a logger
logger = Log.create_logger(name="my_app", log_level=LogLevels.INFO)

# Use it
logger.info("Application started")
logger.warning("This is a warning")
logger.error("An error occurred")
```

**Output**:
```
INFO:my_app:Application started
WARNING:my_app:This is a warning
ERROR:my_app:An error occurred
```

### 2. Colored Output

Add colors to your logs:

```python
from rich_logging import Log, LogLevels, LogFormatters

logger = Log.create_logger(
    name="my_app",
    log_level=LogLevels.INFO,
    formatter_type=LogFormatters.COLORED
)

logger.info("This will be green")
logger.warning("This will be yellow")
logger.error("This will be red")
```

### 3. Rich Handler

Use Rich for enhanced console output:

```python
from rich_logging import Log, LogLevels, ConsoleHandlers
from rich_logging.handlers import RichHandlerSettings

logger = Log.create_logger(
    name="my_app",
    log_level=LogLevels.INFO,
    console_handler_type=ConsoleHandlers.RICH,
    rich_handler_settings=RichHandlerSettings(
        show_time=True,
        show_path=True,
        markup=True
    )
)

logger.info("Rich formatted message")
logger.info("[bold blue]Styled message[/bold blue]")
```

### 4. File Logging

Log to a file:

```python
from rich_logging import Log, LogLevels, FileHandlerTypes
from rich_logging.handlers import FileHandlerSettings

logger = Log.create_logger(
    name="my_app",
    log_level=LogLevels.INFO,
    file_handler_type=FileHandlerTypes.FILE,
    file_handler_settings=FileHandlerSettings(
        filename="app.log"
    )
)

logger.info("This goes to app.log")
```

### 5. Rich Features

Use Rich features for visual output:

```python
from rich_logging import Log

logger = Log.create_logger(name="my_app")

# Display a table
logger.table(
    data=[
        ["Name", "Status"],
        ["Task 1", "Complete"],
        ["Task 2", "Pending"]
    ],
    title="Task Status"
)

# Display a panel
logger.panel(
    "Deployment successful!",
    title="Success",
    border_style="green"
)

# Show progress
with logger.progress() as progress:
    task = progress.add_task("Processing...", total=100)
    for i in range(100):
        # Do work
        progress.update(task, advance=1)
```

## Common Patterns

### Pattern 1: Application Logger

Create a logger for your application:

```python
from rich_logging import Log, LogLevels, LogFormatters

# Create logger once at application startup
logger = Log.create_logger(
    name="my_app",
    log_level=LogLevels.INFO,
    formatter_type=LogFormatters.COLORED
)

# Use throughout application
def main():
    logger.info("Application starting")

    try:
        run_application()
        logger.info("Application completed successfully")
    except Exception as e:
        logger.exception("Application failed")
        raise
```

### Pattern 2: Module Logger

Create a logger for each module:

```python
# In module1.py
from rich_logging import Log, LogLevels

logger = Log.create_logger(name=__name__, log_level=LogLevels.DEBUG)

def process_data():
    logger.debug("Starting data processing")
    # ... processing logic
    logger.info("Data processing complete")
```

```python
# In module2.py
from rich_logging import Log, LogLevels

logger = Log.create_logger(name=__name__, log_level=LogLevels.DEBUG)

def analyze_results():
    logger.debug("Starting analysis")
    # ... analysis logic
    logger.info("Analysis complete")
```

### Pattern 3: File + Console Logging

Log to both console and file:

```python
from rich_logging import (
    Log, LogConfig, LogLevels, LogFormatters,
    ConsoleHandlers, FileHandlerTypes
)
from rich_logging.handlers import (
    RichHandlerSettings,
    RotatingFileHandlerSettings
)

config = LogConfig(
    log_level=LogLevels.INFO,
    formatter_type=LogFormatters.RICH,
    console_handler_type=ConsoleHandlers.RICH,
    rich_handler_settings=RichHandlerSettings(
        show_time=True,
        show_path=True
    ),
    file_handler_type=FileHandlerTypes.ROTATING_FILE,
    file_handler_settings=RotatingFileHandlerSettings(
        filename="app.log",
        max_bytes=10_485_760,  # 10 MB
        backup_count=5
    )
)

logger = Log.create_logger(name="my_app", config=config)
```

### Pattern 4: Debug vs Production

Different configuration for debug and production:

```python
import os
from rich_logging import Log, LogLevels, LogFormatters

# Determine environment
is_debug = os.getenv("DEBUG", "false").lower() == "true"

# Configure based on environment
logger = Log.create_logger(
    name="my_app",
    log_level=LogLevels.DEBUG if is_debug else LogLevels.INFO,
    formatter_type=LogFormatters.COLORED if is_debug else LogFormatters.DEFAULT
)

logger.debug("This only shows in debug mode")
logger.info("This shows in both modes")
```

### Pattern 5: Progress Tracking

Track long-running operations:

```python
from rich_logging import Log

logger = Log.create_logger(name="my_app")

def process_items(items):
    logger.info(f"Processing {len(items)} items")

    with logger.progress() as progress:
        task = progress.add_task("Processing", total=len(items))

        for item in items:
            # Process item
            result = process_item(item)

            # Update progress
            progress.update(task, advance=1)

    logger.info("Processing complete")
```

## Configuration Options

### Log Levels

```python
from rich_logging import LogLevels

LogLevels.DEBUG     # Detailed information for debugging
LogLevels.INFO      # General informational messages
LogLevels.WARNING   # Warning messages
LogLevels.ERROR     # Error messages
LogLevels.CRITICAL  # Critical error messages
```

### Formatter Types

```python
from rich_logging import LogFormatters

LogFormatters.DEFAULT  # Standard Python logging formatter
LogFormatters.COLORED  # ANSI colored formatter
LogFormatters.RICH     # Rich markup formatter
```

### Console Handler Types

```python
from rich_logging import ConsoleHandlers

ConsoleHandlers.DEFAULT  # Standard StreamHandler
ConsoleHandlers.RICH     # Rich RichHandler
```

### File Handler Types

```python
from rich_logging import FileHandlerTypes

FileHandlerTypes.FILE                # Basic file handler
FileHandlerTypes.ROTATING_FILE       # Size-based rotation
FileHandlerTypes.TIMED_ROTATING_FILE # Time-based rotation
```

## Next Steps

- **Configuration**: See [configuration.md](configuration.md) for detailed configuration options
- **Rich Features**: See [rich_features.md](rich_features.md) for comprehensive Rich features guide
- **File Logging**: See [file_logging.md](file_logging.md) for file handler details
- **Advanced Usage**: See [advanced_usage.md](advanced_usage.md) for advanced patterns
- **API Reference**: See [../api/logger.md](../api/logger.md) for complete API documentation
- **Examples**: See [../reference/examples.md](../reference/examples.md) for more examples

## Troubleshooting

### Rich Not Available

If Rich is not installed, the module falls back to standard logging:

```python
# This works even without Rich
logger = Log.create_logger(name="my_app", log_level=LogLevels.INFO)
logger.info("Standard logging works")

# Rich features become no-ops
logger.table(data)  # Does nothing if Rich unavailable
```

To install Rich:
```bash
pip install rich
# or
uv add rich
```

### Import Errors

If you get import errors, ensure the module is installed:

```bash
cd src/common/modules/logging
uv sync
```

### Logger Not Logging

Check the log level:

```python
# If log level is INFO, debug messages won't show
logger = Log.create_logger(name="my_app", log_level=LogLevels.INFO)
logger.debug("This won't show")  # Too low level
logger.info("This will show")    # Correct level
```

### File Permission Errors

Ensure the log file directory exists and is writable:

```python
import os
from pathlib import Path

log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logger = Log.create_logger(
    name="my_app",
    file_handler_type=FileHandlerTypes.FILE,
    file_handler_settings=FileHandlerSettings(
        filename=str(log_dir / "app.log")
    )
)
```

## Best Practices

1. **Create loggers once**: Create loggers at module or application startup, not in functions
2. **Use appropriate levels**: DEBUG for development, INFO for production
3. **Name loggers**: Use `__name__` for module loggers, descriptive names for application loggers
4. **Configure early**: Configure logging before other imports
5. **Use Rich features wisely**: Rich features are for visual output, not for log files
6. **Handle exceptions**: Use `logger.exception()` in except blocks
7. **Rotate log files**: Use rotating file handlers for long-running applications

## Summary

The logging module provides:

- **Simple API**: Single `Log.create_logger()` call
- **Type Safety**: Enums and dataclasses for configuration
- **Rich Integration**: 20+ Rich features
- **Graceful Degradation**: Works without Rich
- **Flexible Configuration**: Multiple handlers, formatters, and options

Start with basic logging and add features as needed!
