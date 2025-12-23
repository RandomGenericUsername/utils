# Usage Guide

Complete guide to using the `rich-logging` library. All examples are verified by integration tests.

---

## Table of Contents

- [Quick Start](#quick-start)
- [Basic Logging](#basic-logging)
- [Log Levels](#log-levels)
- [Configuration](#configuration)
- [Updating Logger Configuration](#updating-logger-configuration)
- [Multiple Loggers](#multiple-loggers)
- [Rich Features](#rich-features)
- [Task Context](#task-context)

---

## Quick Start

Create a logger and start logging:

```python
from rich_logging import Log, LogLevels

# Create a logger
logger = Log.create_logger("myapp", log_level=LogLevels.INFO)

# Log messages
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")
```

**Evidence**: `tests/integration/test_logger_lifecycle.py::TestLoggerCreationAndLogging::test_create_logger_and_log_messages`

---

## Basic Logging

### Creating a Logger

The simplest way to create a logger:

```python
from rich_logging import Log, LogLevels

logger = Log.create_logger("myapp", log_level=LogLevels.INFO)
```

This creates a logger named `"myapp"` with INFO level logging.

**Evidence**: `tests/integration/test_logger_lifecycle.py::TestLoggerCreationAndLogging::test_create_logger_and_log_messages`

### Logging Messages

Use standard logging methods:

```python
logger.debug("Detailed debugging information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred")
logger.critical("Critical error!")
logger.exception("Exception with traceback")
```

**Evidence**: `tests/integration/test_logger_lifecycle.py::TestLoggerCreationAndLogging::test_create_logger_and_log_messages`

---

## Log Levels

Log levels control which messages are displayed. Messages below the configured level are filtered out.

### Available Log Levels

From most to least verbose:

1. **DEBUG** - Detailed debugging information
2. **INFO** - General informational messages
3. **WARNING** - Warning messages
4. **ERROR** - Error messages
5. **CRITICAL** - Critical errors

### Log Level Filtering

```python
from rich_logging import Log, LogLevels

# Create logger with WARNING level
logger = Log.create_logger("myapp", log_level=LogLevels.WARNING)

# These will NOT be logged (below WARNING level)
logger.debug("Debug message")
logger.info("Info message")

# These WILL be logged (WARNING level and above)
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")
```

**Evidence**: `tests/integration/test_logger_lifecycle.py::TestLoggerCreationAndLogging::test_logger_respects_log_level`

---

## Configuration

### Using LogConfig

For more complex configurations, use the `LogConfig` dataclass:

```python
from rich_logging import Log, LogConfig, LogLevels, ConsoleHandlers

config = LogConfig(
    name="myapp",
    log_level=LogLevels.DEBUG,
    console_handler_type=ConsoleHandlers.RICH
)

logger = Log.create_logger(config=config)
```

### Console Handler Types

Choose between standard and Rich console handlers:

```python
from rich_logging import Log, LogLevels, ConsoleHandlers

# Standard console handler (default)
logger = Log.create_logger(
    "myapp",
    log_level=LogLevels.INFO,
    console_handler_type=ConsoleHandlers.DEFAULT
)

# Rich console handler (enhanced output)
logger = Log.create_logger(
    "myapp",
    log_level=LogLevels.INFO,
    console_handler_type=ConsoleHandlers.RICH
)
```

**Evidence**: `tests/integration/test_logger_lifecycle.py::TestMultipleLoggers::test_multiple_loggers_different_handlers`

### Enabling Rich Features

```python
from rich_logging import Log, LogLevels, ConsoleHandlers, RichFeatureSettings

logger = Log.create_logger(
    "myapp",
    log_level=LogLevels.INFO,
    console_handler_type=ConsoleHandlers.RICH,
    rich_features=RichFeatureSettings(enabled=True)
)
```

**Evidence**: `tests/integration/test_logger_lifecycle.py::TestLoggerCreationAndLogging::test_logger_with_rich_handler`

---

## Updating Logger Configuration

You can update an existing logger's configuration without recreating it:

```python
from rich_logging import Log, LogLevels

# Create logger with INFO level
logger = Log.create_logger("myapp", log_level=LogLevels.INFO)

# Debug messages are filtered out
logger.debug("Not logged")
logger.info("Logged")

# Update to DEBUG level
logger = Log.update("myapp", log_level=LogLevels.DEBUG)

# Now debug messages are logged
logger.debug("Now logged!")
logger.info("Still logged")
```

**Evidence**: `tests/integration/test_logger_lifecycle.py::TestLoggerUpdate::test_update_logger_level`

### Multiple Updates

You can update a logger multiple times:

```python
logger = Log.create_logger("myapp", log_level=LogLevels.INFO)

# First update
logger = Log.update("myapp", log_level=LogLevels.DEBUG)

# Second update
logger = Log.update("myapp", log_level=LogLevels.WARNING)

# Third update
logger = Log.update("myapp", log_level=LogLevels.ERROR)
```

**Evidence**: `tests/integration/test_logger_lifecycle.py::TestLoggerUpdate::test_update_logger_multiple_times`

---

## Multiple Loggers

You can create multiple independent loggers with different configurations:

```python
from rich_logging import Log, LogLevels

# Create first logger with DEBUG level
logger1 = Log.create_logger("app1", log_level=LogLevels.DEBUG)

# Create second logger with WARNING level
logger2 = Log.create_logger("app2", log_level=LogLevels.WARNING)

# Each logger operates independently
logger1.debug("App1 debug")    # Logged (app1 is DEBUG level)
logger1.info("App1 info")      # Logged

logger2.debug("App2 debug")    # NOT logged (app2 is WARNING level)
logger2.warning("App2 warning") # Logged
```

**Evidence**: `tests/integration/test_logger_lifecycle.py::TestMultipleLoggers::test_multiple_loggers_independent`

### Different Handler Types

Each logger can have its own handler type:

```python
from rich_logging import Log, LogLevels, ConsoleHandlers

# Logger with standard console handler
logger1 = Log.create_logger(
    "app1",
    log_level=LogLevels.INFO,
    console_handler_type=ConsoleHandlers.DEFAULT
)

# Logger with Rich console handler
logger2 = Log.create_logger(
    "app2",
    log_level=LogLevels.INFO,
    console_handler_type=ConsoleHandlers.RICH
)
```

**Evidence**: `tests/integration/test_logger_lifecycle.py::TestMultipleLoggers::test_multiple_loggers_different_handlers`

---

## Rich Features

Rich features provide enhanced console output with tables, panels, progress bars, and more.

### Prerequisites

Enable Rich features when creating the logger:

```python
from rich_logging import Log, LogLevels, ConsoleHandlers, RichFeatureSettings

logger = Log.create_logger(
    "myapp",
    log_level=LogLevels.INFO,
    console_handler_type=ConsoleHandlers.RICH,
    rich_features=RichFeatureSettings(enabled=True)
)
```

### Display Methods

#### Tables

Display data in a table format:

```python
logger.table(
    [["Name", "Age"], ["Alice", "30"], ["Bob", "25"]],
    show_header=True
)
```

**Evidence**: `tests/integration/test_rich_features.py::TestRichDisplayFeatures::test_table_displays_data`

#### Panels

Display messages in bordered panels:

```python
logger.panel("Important message", title="Alert")
```

**Evidence**: `tests/integration/test_rich_features.py::TestRichDisplayFeatures::test_panel_displays_message`

#### Rules

Display horizontal separators:

```python
logger.rule("Section Title")
```

**Evidence**: `tests/integration/test_rich_features.py::TestRichDisplayFeatures::test_rule_displays_separator`

#### Syntax Highlighting

Display syntax-highlighted code:

```python
logger.syntax("def hello(): pass", "python")
```

**Evidence**: `tests/integration/test_rich_features.py::TestRichDisplayFeatures::test_syntax_displays_code`

#### Markdown

Display formatted markdown:

```python
logger.markdown("# Title\n\nParagraph")
```

**Evidence**: `tests/integration/test_rich_features.py::TestRichDisplayFeatures::test_markdown_displays_formatted_text`

#### JSON

Display formatted JSON:

```python
logger.json({"key": "value", "number": 42})
```

**Evidence**: `tests/integration/test_rich_features.py::TestRichDisplayFeatures::test_json_displays_formatted_json`

### Context Managers

#### Progress Tracking

Track progress of long-running operations:

```python
with logger.progress("Processing", total=100) as progress:
    task = progress.add_task("Processing items", total=100)
    for i in range(100):
        # Do work
        progress.update(task, advance=1)
```

**Evidence**: `tests/integration/test_rich_features.py::TestRichContextManagers::test_progress_context_manager_workflow`

**Graceful Degradation**: When Rich is disabled, progress returns a dummy object that doesn't display anything but has the same interface.

**Evidence**: `tests/integration/test_rich_features.py::TestRichContextManagers::test_progress_fallback_when_disabled`

---

## Task Context

Task context is useful for parallel execution where multiple tasks run concurrently and need to be identified in logs.

### Setting Task Context

```python
from rich_logging import Log, LogLevels

logger = Log.create_logger("myapp", log_level=LogLevels.INFO)

# Set task context
logger.set_task_context("task1", "Task 1 Name")

# Log messages (will include task context)
logger.info("Processing item")

# Clear task context when done
logger.clear_task_context()
```

**Evidence**: `tests/integration/test_rich_features.py::TestTaskContext::test_task_context_workflow`

### Using Context Manager

For automatic cleanup:

```python
with logger.task_context("task1", "Task 1 Name"):
    logger.info("Processing item")
    # Context automatically cleared after block
```

This ensures task context is cleared even if an exception occurs.

---

## Best Practices

### 1. Use Appropriate Log Levels

- **DEBUG**: Detailed information for diagnosing problems
- **INFO**: Confirmation that things are working as expected
- **WARNING**: Something unexpected happened, but the application is still working
- **ERROR**: A serious problem occurred
- **CRITICAL**: A very serious error that may prevent the program from continuing

### 2. Create Named Loggers

Always provide a name when creating loggers:

```python
# Good
logger = Log.create_logger("myapp", log_level=LogLevels.INFO)

# Avoid (uses root logger)
logger = Log.create_logger(log_level=LogLevels.INFO)
```

### 3. Update Instead of Recreate

When changing configuration, use `Log.update()` instead of creating a new logger:

```python
# Good
logger = Log.create_logger("myapp", log_level=LogLevels.INFO)
logger = Log.update("myapp", log_level=LogLevels.DEBUG)

# Avoid
logger = Log.create_logger("myapp", log_level=LogLevels.INFO)
logger = Log.create_logger("myapp", log_level=LogLevels.DEBUG)  # Creates duplicate
```

### 4. Enable Rich Features Explicitly

Rich features are disabled by default. Enable them explicitly when needed:

```python
from rich_logging import RichFeatureSettings

logger = Log.create_logger(
    "myapp",
    log_level=LogLevels.INFO,
    console_handler_type=ConsoleHandlers.RICH,
    rich_features=RichFeatureSettings(enabled=True)
)
```

### 5. Use Task Context for Parallel Execution

When running tasks in parallel, use task context to identify which task generated each log message:

```python
import concurrent.futures

def process_item(item_id):
    with logger.task_context(f"item_{item_id}", f"Processing Item {item_id}"):
        logger.info(f"Processing {item_id}")
        # Do work

with concurrent.futures.ThreadPoolExecutor() as executor:
    executor.map(process_item, range(10))
```

---

## Next Steps

- See [API Reference](api-reference.md) for complete API documentation
- See [Configuration Reference](configuration.md) for all configuration options
- See [Advanced Features](advanced-features.md) for more Rich features

