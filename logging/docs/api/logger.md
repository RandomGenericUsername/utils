# Logger API Reference

## Overview

This document provides comprehensive API documentation for the main logger classes: `Log` (facade) and `RichLogger` (enhanced logger wrapper).

## Log Class (Facade)

The `Log` class is the main entry point for creating and managing loggers. It provides a simplified interface over the complex logging configuration system.

### Location
```python
from rich_logging import Log
```

### Methods

#### create_logger()

Create and configure a new logger instance.

**Signature**:
```python
@staticmethod
def create_logger(
    name: str | None = None,
    config: LogConfig | None = None,
    log_level: LogLevels | None = None,
    formatter_style: LogFormatterStyleChoices | None = None,
    format: str | None = None,
    formatter_type: LogFormatters | None = None,
    console_handler_type: ConsoleHandlers | None = None,
    file_handler_type: FileHandlerTypes | None = None,
    file_handler_settings: BaseFileHandlerSettings | None = None,
    rich_handler_settings: RichHandlerSettings | None = None,
    rich_feature_settings: RichFeatureSettings | None = None,
    colors: type[ColoredFormatterColors] | None = None,
) -> RichLogger
```

**Parameters**:
- `name` (str | None): Logger name. If None, uses root logger
- `config` (LogConfig | None): Complete configuration object. If provided, other kwargs are ignored
- `log_level` (LogLevels | None): Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `formatter_style` (LogFormatterStyleChoices | None): Format string style (%, {, $)
- `format` (str | None): Custom format string
- `formatter_type` (LogFormatters | None): Formatter type (DEFAULT, COLORED, RICH)
- `console_handler_type` (ConsoleHandlers | None): Console handler type (DEFAULT, RICH)
- `file_handler_type` (FileHandlerTypes | None): File handler type (FILE, ROTATING_FILE, TIMED_ROTATING_FILE)
- `file_handler_settings` (BaseFileHandlerSettings | None): File handler configuration
- `rich_handler_settings` (RichHandlerSettings | None): Rich handler configuration
- `rich_feature_settings` (RichFeatureSettings | None): Rich feature configuration
- `colors` (type[ColoredFormatterColors] | None): Custom color scheme for colored formatter

**Returns**:
- `RichLogger`: Configured logger instance

**Examples**:

```python
# Simple usage - minimal configuration
logger = Log.create_logger(name="app", log_level=LogLevels.INFO)

# With colored formatter
logger = Log.create_logger(
    name="app",
    log_level=LogLevels.DEBUG,
    formatter_type=LogFormatters.COLORED
)

# With Rich handler
logger = Log.create_logger(
    name="app",
    log_level=LogLevels.INFO,
    console_handler_type=ConsoleHandlers.RICH,
    rich_handler_settings=RichHandlerSettings(
        show_time=True,
        show_path=True,
        markup=True
    )
)

# With file logging
logger = Log.create_logger(
    name="app",
    log_level=LogLevels.INFO,
    file_handler_type=FileHandlerTypes.ROTATING_FILE,
    file_handler_settings=RotatingFileHandlerSettings(
        filename="app.log",
        max_bytes=10_485_760,
        backup_count=5
    )
)

# With complete config object
config = LogConfig(
    log_level=LogLevels.INFO,
    formatter_type=LogFormatters.RICH,
    console_handler_type=ConsoleHandlers.RICH
)
logger = Log.create_logger(name="app", config=config)
```

#### update()

Update an existing logger's configuration.

**Signature**:
```python
@staticmethod
def update(
    logger: RichLogger,
    config: LogConfig | None = None,
    **kwargs
) -> RichLogger
```

**Parameters**:
- `logger` (RichLogger): Logger to update
- `config` (LogConfig | None): New configuration object
- `**kwargs`: Individual configuration parameters (same as create_logger)

**Returns**:
- `RichLogger`: Updated logger instance

**Example**:
```python
# Create logger
logger = Log.create_logger(name="app", log_level=LogLevels.INFO)

# Update configuration
logger = Log.update(
    logger,
    log_level=LogLevels.DEBUG,
    formatter_type=LogFormatters.COLORED
)
```

## RichLogger Class

The `RichLogger` class wraps a standard `logging.Logger` and adds Rich library features. It transparently delegates all standard logging methods to the wrapped logger while providing additional Rich feature methods.

### Location
```python
from rich_logging import RichLogger
```

### Standard Logging Methods

All standard `logging.Logger` methods are available and work identically:

#### debug()
```python
def debug(self, msg, *args, **kwargs):
    """Log a debug message."""
```

#### info()
```python
def info(self, msg, *args, **kwargs):
    """Log an info message."""
```

#### warning()
```python
def warning(self, msg, *args, **kwargs):
    """Log a warning message."""
```

#### error()
```python
def error(self, msg, *args, **kwargs):
    """Log an error message."""
```

#### critical()
```python
def critical(self, msg, *args, **kwargs):
    """Log a critical message."""
```

#### exception()
```python
def exception(self, msg, *args, **kwargs):
    """Log an exception with traceback."""
```

**Example**:
```python
logger = Log.create_logger(name="app")

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")

try:
    1 / 0
except Exception:
    logger.exception("An error occurred")
```

### Rich Feature Methods

RichLogger provides 20+ methods for Rich library features:

#### table()

Display a table using Rich.

**Signature**:
```python
def table(
    self,
    data: list[list[str]] | None = None,
    title: str | None = None,
    **kwargs
) -> None
```

**Parameters**:
- `data` (list[list[str]]): Table data (first row is headers)
- `title` (str | None): Table title
- `**kwargs`: Additional Rich Table parameters

**Example**:
```python
logger.table(
    data=[
        ["Name", "Age", "City"],
        ["Alice", "30", "New York"],
        ["Bob", "25", "San Francisco"]
    ],
    title="User Data",
    show_lines=True
)
```

#### panel()

Display a panel with a message.

**Signature**:
```python
def panel(
    self,
    message: str,
    title: str | None = None,
    border_style: str | None = None,
    **kwargs
) -> None
```

**Parameters**:
- `message` (str): Panel content
- `title` (str | None): Panel title
- `border_style` (str | None): Border color/style
- `**kwargs`: Additional Rich Panel parameters

**Example**:
```python
logger.panel(
    "Deployment completed successfully!",
    title="Success",
    border_style="green"
)
```

#### rule()

Display a horizontal rule/separator.

**Signature**:
```python
def rule(
    self,
    title: str | None = None,
    style: str | None = None,
    **kwargs
) -> None
```

**Example**:
```python
logger.rule("Section 1", style="blue")
```

#### progress()

Create a progress bar context manager.

**Signature**:
```python
def progress(self, **kwargs) -> Progress
```

**Example**:
```python
with logger.progress() as progress:
    task = progress.add_task("Processing...", total=100)
    for i in range(100):
        # Do work
        progress.update(task, advance=1)
```

#### status()

Create a status spinner context manager.

**Signature**:
```python
def status(
    self,
    message: str,
    spinner: str | None = None,
    **kwargs
) -> Status
```

**Example**:
```python
with logger.status("Loading data...", spinner="dots"):
    # Do work
    time.sleep(2)
```

#### tree()

Display a tree structure.

**Signature**:
```python
def tree(
    self,
    label: str,
    data: dict | None = None,
    **kwargs
) -> None
```

**Example**:
```python
logger.tree(
    "Project Structure",
    data={
        "src": {
            "main.py": None,
            "utils.py": None
        },
        "tests": {
            "test_main.py": None
        }
    }
)
```

#### columns()

Display content in columns.

**Signature**:
```python
def columns(
    self,
    renderables: list,
    **kwargs
) -> None
```

**Example**:
```python
logger.columns(
    ["Column 1 content", "Column 2 content", "Column 3 content"],
    equal=True
)
```

#### syntax()

Display syntax-highlighted code.

**Signature**:
```python
def syntax(
    self,
    code: str,
    lexer: str = "python",
    theme: str | None = None,
    **kwargs
) -> None
```

**Example**:
```python
logger.syntax(
    'def hello():\n    print("Hello, world!")',
    lexer="python",
    theme="monokai",
    line_numbers=True
)
```

#### markdown()

Render markdown content.

**Signature**:
```python
def markdown(
    self,
    markup: str,
    **kwargs
) -> None
```

**Example**:
```python
logger.markdown("""
# Heading
This is **bold** and this is *italic*.
- Item 1
- Item 2
""")
```

#### json()

Display formatted JSON.

**Signature**:
```python
def json(
    self,
    data: dict | str,
    **kwargs
) -> None
```

**Example**:
```python
logger.json({"name": "Alice", "age": 30, "city": "New York"})
```

#### live()

Create a live display context manager.

**Signature**:
```python
def live(
    self,
    renderable,
    **kwargs
) -> Live
```

**Example**:
```python
from rich.table import Table

table = Table()
table.add_column("Status")

with logger.live(table, refresh_per_second=4):
    for i in range(10):
        table.add_row(f"Processing item {i}")
        time.sleep(0.5)
```

#### bar_chart()

Display a bar chart.

**Signature**:
```python
def bar_chart(
    self,
    data: dict[str, float],
    **kwargs
) -> None
```

**Example**:
```python
logger.bar_chart(
    {"Python": 45, "JavaScript": 30, "Go": 15, "Rust": 10},
    title="Language Usage"
)
```

#### text()

Display styled text.

**Signature**:
```python
def text(
    self,
    text: str,
    style: str | None = None,
    **kwargs
) -> None
```

**Example**:
```python
logger.text("Important message", style="bold red")
```

#### align()

Display aligned text.

**Signature**:
```python
def align(
    self,
    text: str,
    align: str = "center",
    **kwargs
) -> None
```

**Example**:
```python
logger.align("Centered text", align="center")
```

#### prompt()

Prompt user for input.

**Signature**:
```python
def prompt(
    self,
    prompt_text: str,
    **kwargs
) -> str
```

**Example**:
```python
name = logger.prompt("Enter your name")
```

#### confirm()

Prompt user for yes/no confirmation.

**Signature**:
```python
def confirm(
    self,
    prompt_text: str,
    **kwargs
) -> bool
```

**Example**:
```python
if logger.confirm("Continue?"):
    # Proceed
    pass
```

#### inspect()

Inspect and display object details.

**Signature**:
```python
def inspect(
    self,
    obj: Any,
    **kwargs
) -> None
```

**Example**:
```python
logger.inspect(my_object, methods=True)
```

#### pretty()

Pretty print an object.

**Signature**:
```python
def pretty(
    self,
    obj: Any,
    **kwargs
) -> None
```

**Example**:
```python
logger.pretty({"nested": {"data": [1, 2, 3]}})
```

### Properties

#### name
```python
@property
def name(self) -> str:
    """Get logger name."""
```

#### level
```python
@property
def level(self) -> int:
    """Get logger level."""
```

#### handlers
```python
@property
def handlers(self) -> list[logging.Handler]:
    """Get logger handlers."""
```

## Usage Patterns

### Basic Logging
```python
logger = Log.create_logger(name="app", log_level=LogLevels.INFO)
logger.info("Application started")
logger.warning("Low disk space")
logger.error("Failed to connect to database")
```

### Rich Features
```python
logger = Log.create_logger(name="app")

# Display progress
with logger.progress() as progress:
    task = progress.add_task("Processing", total=100)
    for i in range(100):
        progress.update(task, advance=1)

# Display table
logger.table(data, title="Results")

# Display panel
logger.panel("Success!", border_style="green")
```

### Combined Usage
```python
logger = Log.create_logger(name="app", log_level=LogLevels.INFO)

logger.info("Starting data processing")

with logger.progress() as progress:
    task = progress.add_task("Processing", total=len(items))
    for item in items:
        process(item)
        progress.update(task, advance=1)

logger.table(results, title="Processing Results")
logger.info("Data processing complete")
```

## See Also

- [Configuration Guide](../guides/configuration.md) - Detailed configuration options
- [Rich Features Guide](../guides/rich_features.md) - Comprehensive Rich features documentation
- [Examples](../reference/examples.md) - More usage examples
