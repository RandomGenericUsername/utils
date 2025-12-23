# API Reference

Complete API documentation for the `rich-logging` library. All documented behavior is verified by tests.

---

## Table of Contents

- [Log Class](#log-class)
  - [Log.create_logger()](#logcreate_logger)
  - [Log.update()](#logupdate)
- [RichLogger Class](#richlogger-class)
  - [Standard Logging Methods](#standard-logging-methods)
  - [Properties](#properties)
  - [Display Methods](#display-methods)
  - [Context Managers](#context-managers)
  - [Task Context](#task-context)
  - [Interactive Methods](#interactive-methods)
- [Utility Functions](#utility-functions)
  - [parse_log_level()](#parse_log_level)
  - [validate_log_level_string()](#validate_log_level_string)
  - [get_log_level_from_verbosity()](#get_log_level_from_verbosity)

---

## Log Class

The `Log` class is the main entry point for creating and managing loggers.

### Log.create_logger()

Creates and configures a new logger instance.

**Signature**:
```python
@staticmethod
def create_logger(
    name: str | None = None,
    config: LogConfig | None = None,
    log_level: LogLevels | None = None,
    formatter_style: LogFormatterStyleChoices = LogFormatterStyleChoices.PERCENT,
    format: str = "%(asctime)s | %(levelname)-8s | %(message)s",
    formatter_type: LogFormatters = LogFormatters.DEFAULT,
    colors: type[ColoredFormatterColors] | None = None,
    console_handler_type: ConsoleHandlers = ConsoleHandlers.DEFAULT,
    handler_config: RichHandlerSettings | None = None,
    file_handlers: list[FileHandlerSpec] | None = None,
    rich_features: RichFeatureSettings | None = None,
) -> RichLogger
```

**Parameters**:

- **name** (`str | None`): Logger name. If `None`, uses root logger.
  - Evidence: `tests/contract/test_log_api.py::TestLogCreateLogger::test_create_logger_returns_rich_logger`

- **config** (`LogConfig | None`): LogConfig object with all settings. If provided, individual parameters override config values.
  - Evidence: `tests/contract/test_log_api.py::TestLogCreateLogger::test_create_logger_with_config_object`

- **log_level** (`LogLevels | None`): Log level. Required if config is not provided. Supports: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.
  - Evidence: `tests/contract/test_log_api.py::TestLogCreateLogger::test_create_logger_with_log_level`
  - Evidence: `tests/contract/test_log_api.py::TestLogCreateLogger::test_create_logger_with_debug_level`
  - Evidence: `tests/contract/test_log_api.py::TestLogCreateLogger::test_create_logger_with_info_level`
  - Evidence: `tests/contract/test_log_api.py::TestLogCreateLogger::test_create_logger_with_warning_level`
  - Evidence: `tests/contract/test_log_api.py::TestLogCreateLogger::test_create_logger_with_error_level`
  - Evidence: `tests/contract/test_log_api.py::TestLogCreateLogger::test_create_logger_with_critical_level`

- **formatter_style** (`LogFormatterStyleChoices`): Format style. Supports: `PERCENT` (%), `BRACE` ({}), `DOLLAR` ($). Default: `PERCENT`.
  - Evidence: `tests/unit/test_formatter_factory.py::TestFormatterFactory::test_create_formatter_with_percent_style`
  - Evidence: `tests/unit/test_formatter_factory.py::TestFormatterFactory::test_create_formatter_with_brace_style`
  - Evidence: `tests/unit/test_formatter_factory.py::TestFormatterFactory::test_create_formatter_with_dollar_style`

- **format** (`str`): Format string for log messages. Default: `"%(asctime)s | %(levelname)-8s | %(message)s"`.

- **formatter_type** (`LogFormatters`): Type of formatter. Supports: `DEFAULT`, `COLORED`, `RICH`. Default: `DEFAULT`.
  - Evidence: `tests/unit/test_formatter_factory.py::TestFormatterFactory::test_create_default_formatter`
  - Evidence: `tests/unit/test_formatter_factory.py::TestFormatterFactory::test_create_colored_formatter`
  - Evidence: `tests/unit/test_formatter_factory.py::TestFormatterFactory::test_create_rich_formatter`

- **colors** (`type[ColoredFormatterColors] | None`): Color scheme for colored formatter.

- **console_handler_type** (`ConsoleHandlers`): Type of console handler. Supports: `DEFAULT`, `RICH`. Default: `DEFAULT`.
  - Evidence: `tests/contract/test_log_api.py::TestLogCreateLogger::test_create_logger_with_console_handler_default`
  - Evidence: `tests/contract/test_log_api.py::TestLogCreateLogger::test_create_logger_with_console_handler_rich`

- **handler_config** (`RichHandlerSettings | None`): RichHandlerSettings instance for Rich handler configuration.

- **file_handlers** (`list[FileHandlerSpec] | None`): List of file handler specifications.

- **rich_features** (`RichFeatureSettings | None`): Configuration for Rich features.
  - Evidence: `tests/contract/test_log_api.py::TestLogCreateLogger::test_create_logger_with_rich_features`

**Returns**: `RichLogger` - Enhanced logger instance with Rich features.

**Example**:
```python
from rich_logging import Log, LogLevels, ConsoleHandlers

# Basic logger
logger = Log.create_logger("myapp", log_level=LogLevels.INFO)

# Logger with Rich console handler
logger = Log.create_logger(
    "myapp",
    log_level=LogLevels.DEBUG,
    console_handler_type=ConsoleHandlers.RICH
)

# Logger with config object
from rich_logging import LogConfig

config = LogConfig(
    name="myapp",
    log_level=LogLevels.INFO,
    console_handler_type=ConsoleHandlers.RICH
)
logger = Log.create_logger(config=config)
```

**Evidence**: `tests/contract/test_log_api.py::TestLogCreateLogger` (14 tests)

---

### Log.update()

Updates an existing logger's configuration.

**Signature**:
```python
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
    handler_config: RichHandlerSettings | None = None,
    file_handlers: list[FileHandlerSpec] | None = None,
    rich_features: RichFeatureSettings | None = None,
) -> RichLogger
```

**Parameters**:

- **name** (`str`): Logger name. **Required**. Logger must already exist.
  - Evidence: `tests/contract/test_log_api.py::TestLogUpdate::test_update_requires_existing_logger`

- **config** (`LogConfig | None`): LogConfig object with new settings. Individual parameters override config values.

- **log_level** (`LogLevels | None`): New log level. `None` to keep existing.
  - Evidence: `tests/contract/test_log_api.py::TestLogUpdate::test_update_log_level`

- **formatter_style** (`LogFormatterStyleChoices | None`): New format style. `None` to keep existing.

- **format** (`str | None`): New format string. `None` to keep existing.

- **formatter_type** (`LogFormatters | None`): New formatter type. `None` to keep existing.

- **colors** (`type[ColoredFormatterColors] | None`): New color scheme. `None` to keep existing.

- **console_handler_type** (`ConsoleHandlers | None`): New handler type. `None` to keep existing.
  - Evidence: `tests/contract/test_log_api.py::TestLogUpdate::test_update_console_handler_type`

- **handler_config** (`RichHandlerSettings | None`): New RichHandlerSettings. `None` to keep existing.

- **file_handlers** (`list[FileHandlerSpec] | None`): New file handler specifications. `None` to keep existing.

- **rich_features** (`RichFeatureSettings | None`): New Rich feature configuration. `None` to keep existing.

**Returns**: `RichLogger` - Updated logger instance.

**Raises**: `ValueError` - If logger with given name does not exist.

**Example**:
```python
from rich_logging import Log, LogLevels

# Create logger
logger = Log.create_logger("myapp", log_level=LogLevels.INFO)

# Update log level
logger = Log.update("myapp", log_level=LogLevels.DEBUG)

# Update console handler type
from rich_logging import ConsoleHandlers
logger = Log.update("myapp", console_handler_type=ConsoleHandlers.RICH)
```

**Evidence**: `tests/contract/test_log_api.py::TestLogUpdate` (9 tests)

---

## RichLogger Class

Enhanced logger wrapper that adds Rich features to standard logging while maintaining full compatibility with `logging.Logger`.

### Standard Logging Methods

RichLogger delegates all standard logging methods to the underlying `logging.Logger` instance.

#### info()

Log an informational message.

**Signature**: `def info(message: str, *args, **kwargs) -> None`

**Evidence**: `tests/contract/test_rich_logger_api.py::TestRichLoggerStandardLogging::test_info_delegates_to_stdlib_logger`

#### debug()

Log a debug message.

**Signature**: `def debug(message: str, *args, **kwargs) -> None`

**Evidence**: `tests/contract/test_rich_logger_api.py::TestRichLoggerStandardLogging::test_debug_delegates_to_stdlib_logger`

#### warning()

Log a warning message.

**Signature**: `def warning(message: str, *args, **kwargs) -> None`

**Evidence**: `tests/contract/test_rich_logger_api.py::TestRichLoggerStandardLogging::test_warning_delegates_to_stdlib_logger`

#### error()

Log an error message.

**Signature**: `def error(message: str, *args, **kwargs) -> None`

**Evidence**: `tests/contract/test_rich_logger_api.py::TestRichLoggerStandardLogging::test_error_delegates_to_stdlib_logger`

#### critical()

Log a critical message.

**Signature**: `def critical(message: str, *args, **kwargs) -> None`

**Evidence**: `tests/contract/test_rich_logger_api.py::TestRichLoggerStandardLogging::test_critical_delegates_to_stdlib_logger`

#### exception()

Log an exception with traceback.

**Signature**: `def exception(message: str, *args, **kwargs) -> None`

**Evidence**: `tests/contract/test_rich_logger_api.py::TestRichLoggerStandardLogging::test_exception_delegates_to_stdlib_logger`

#### log()

Log a message with specified level.

**Signature**: `def log(level: int, message: str, *args, **kwargs) -> None`

**Evidence**: `tests/contract/test_rich_logger_api.py::TestRichLoggerStandardLogging::test_log_delegates_to_stdlib_logger`

---

### Properties

#### name

Get the logger name.

**Type**: `str` (read-only)

**Example**:
```python
logger = Log.create_logger("myapp", log_level=LogLevels.INFO)
print(logger.name)  # "myapp"
```

**Evidence**: `tests/contract/test_rich_logger_api.py::TestRichLoggerProperties::test_logger_has_name_property`

#### level

Get or set the logger level.

**Type**: `int` (read-write)

**Evidence**: `tests/contract/test_rich_logger_api.py::TestRichLoggerProperties::test_logger_has_level_property`

#### handlers

Get the list of handlers attached to the logger.

**Type**: `list[logging.Handler]` (read-only)

**Evidence**: `tests/contract/test_rich_logger_api.py::TestRichLoggerProperties::test_logger_has_handlers_property`

---

### Display Methods

Rich display methods for enhanced console output. All methods gracefully degrade when Rich is unavailable.

#### table()

Display data in a table format.

**Signature**:
```python
def table(
    data: list[list[str]],
    headers: list[str] | None = None,
    title: str | None = None,
    **kwargs
) -> None
```

**Parameters**:
- **data**: List of rows (each row is a list of strings)
- **headers**: Optional column headers
- **title**: Optional table title
- **kwargs**: Additional arguments passed to Rich Table

**Example**:
```python
logger.table(
    [["Alice", "30"], ["Bob", "25"]],
    headers=["Name", "Age"],
    title="Users"
)
```

**Evidence**: `tests/contract/test_rich_logger_api.py::TestRichLoggerDisplayMethods::test_table_displays_data`

#### panel()

Display a message in a bordered panel.

**Signature**:
```python
def panel(
    message: str,
    title: str | None = None,
    border_style: str = "blue",
    **kwargs
) -> None
```

**Parameters**:
- **message**: Message to display
- **title**: Optional panel title
- **border_style**: Border color/style
- **kwargs**: Additional arguments passed to Rich Panel

**Example**:
```python
logger.panel("Important message", title="Alert", border_style="red")
```

**Evidence**: `tests/contract/test_rich_logger_api.py::TestRichLoggerDisplayMethods::test_panel_displays_message`

#### rule()

Display a horizontal rule/separator.

**Signature**:
```python
def rule(
    title: str | None = None,
    style: str = "blue",
    **kwargs
) -> None
```

**Parameters**:
- **title**: Optional title text
- **style**: Rule color/style
- **kwargs**: Additional arguments passed to Rich Rule

**Example**:
```python
logger.rule("Section 1")
```

**Evidence**: `tests/contract/test_rich_logger_api.py::TestRichLoggerDisplayMethods::test_rule_displays_separator`

#### syntax()

Display syntax-highlighted code.

**Signature**:
```python
def syntax(
    code: str,
    lexer: str = "python",
    theme: str = "monokai",
    line_numbers: bool = True,
    **kwargs
) -> None
```

**Parameters**:
- **code**: Code to display
- **lexer**: Language for syntax highlighting
- **theme**: Color theme
- **line_numbers**: Whether to show line numbers
- **kwargs**: Additional arguments passed to Rich Syntax

**Example**:
```python
logger.syntax('def hello():\n    print("Hello")', lexer="python")
```

**Evidence**: `tests/contract/test_rich_logger_api.py::TestRichLoggerDisplayMethods::test_syntax_displays_code`

#### markdown()

Display formatted markdown text.

**Signature**:
```python
def markdown(text: str, **kwargs) -> None
```

**Parameters**:
- **text**: Markdown text to display
- **kwargs**: Additional arguments passed to Rich Markdown

**Example**:
```python
logger.markdown("# Title\n\nThis is **bold** text.")
```

**Evidence**: `tests/contract/test_rich_logger_api.py::TestRichLoggerDisplayMethods::test_markdown_displays_formatted_text`

#### json()

Display formatted JSON data.

**Signature**:
```python
def json(data: dict | str, **kwargs) -> None
```

**Parameters**:
- **data**: Dictionary or JSON string to display
- **kwargs**: Additional arguments passed to Rich JSON

**Example**:
```python
logger.json({"status": "success", "count": 42})
```

**Evidence**: `tests/contract/test_rich_logger_api.py::TestRichLoggerDisplayMethods::test_json_displays_formatted_json`

---

### Context Managers

Context managers for progress tracking and status updates.

#### progress()

Context manager for progress tracking.

**Signature**:
```python
@contextmanager
def progress(
    *columns,
    transient: bool = False,
    **kwargs
) -> Iterator[Progress]
```

**Parameters**:
- **columns**: Progress columns to display
- **transient**: Whether progress disappears after completion
- **kwargs**: Additional arguments passed to Rich Progress

**Returns**: `Progress` object for tracking tasks

**Example**:
```python
with logger.progress() as progress:
    task = progress.add_task("Processing...", total=100)
    for i in range(100):
        progress.update(task, advance=1)
```

**Evidence**: `tests/contract/test_rich_logger_api.py::TestRichLoggerContextManagers::test_progress_context_manager`

#### status()

Context manager for status spinner.

**Signature**:
```python
@contextmanager
def status(
    message: str,
    spinner: str = "dots",
    **kwargs
) -> Iterator[Status]
```

**Parameters**:
- **message**: Status message to display
- **spinner**: Spinner style
- **kwargs**: Additional arguments passed to Rich Status

**Returns**: `Status` object

**Example**:
```python
with logger.status("Loading..."):
    # Do work
    time.sleep(2)
```

**Evidence**: `tests/contract/test_rich_logger_api.py::TestRichLoggerContextManagers::test_status_context_manager`

#### live()

Context manager for live-updating displays.

**Signature**:
```python
@contextmanager
def live(
    renderable,
    refresh_per_second: int = 4,
    **kwargs
) -> Iterator[Live]
```

**Parameters**:
- **renderable**: Content to display and update
- **refresh_per_second**: Refresh rate
- **kwargs**: Additional arguments passed to Rich Live

**Returns**: `Live` object for updating display

**Example**:
```python
from rich.table import Table

table = Table()
with logger.live(table, refresh_per_second=4) as live:
    # Update table
    table.add_row("data", "value")
```

**Evidence**: `tests/contract/test_rich_logger_api.py::TestRichLoggerContextManagers::test_live_context_manager`

---

### Task Context

Methods for managing task context in parallel execution scenarios.

#### set_task_context()

Set the task context for the current thread.

**Signature**:
```python
def set_task_context(
    step_id: str,
    task_name: str | None = None,
    **extra_context: Any
) -> None
```

**Parameters**:
- **step_id**: Unique identifier for the current step/task
- **task_name**: Optional human-readable task name
- **extra_context**: Additional context data to store

**Example**:
```python
logger.set_task_context("install_nodejs", "Node.js Installation")
logger.info("Installing package...")
# Output: [install_nodejs] Installing package...
```

**Evidence**: `tests/contract/test_rich_logger_api.py::TestRichLoggerTaskContext::test_set_task_context`

#### clear_task_context()

Clear the task context for the current thread.

**Signature**: `def clear_task_context() -> None`

**Example**:
```python
logger.clear_task_context()
```

**Evidence**: `tests/contract/test_rich_logger_api.py::TestRichLoggerTaskContext::test_clear_task_context`

#### task_context()

Context manager for task context (automatically sets and clears).

**Signature**:
```python
@contextmanager
def task_context(
    step_id: str,
    task_name: str | None = None,
    **extra_context: Any
) -> Iterator[None]
```

**Parameters**:
- **step_id**: Unique identifier for the current step/task
- **task_name**: Optional human-readable task name
- **extra_context**: Additional context data to store

**Example**:
```python
with logger.task_context("install_nodejs", "Node.js Installation"):
    logger.info("Installing package...")
    # Context automatically cleared after block
```

**Evidence**: `tests/contract/test_rich_logger_api.py::TestRichLoggerTaskContext::test_task_context_manager`

---

### Interactive Methods

Methods for user interaction (prompts and confirmations).

#### prompt()

Prompt user for input.

**Signature**:
```python
def prompt(
    message: str,
    choices: list[str] | None = None,
    default: str | None = None,
    **kwargs
) -> str
```

**Parameters**:
- **message**: Prompt message
- **choices**: Optional list of valid choices
- **default**: Default value if user provides no input
- **kwargs**: Additional arguments passed to Rich Prompt

**Returns**: User input string

**Example**:
```python
name = logger.prompt("Enter your name", default="User")
choice = logger.prompt("Select option", choices=["A", "B", "C"])
```

**Evidence**: `tests/contract/test_rich_logger_api.py::TestRichLoggerInteractiveMethods::test_prompt_returns_user_input`

**Graceful Degradation**: When Rich is unavailable, returns the default value.
- Evidence: `tests/contract/test_rich_logger_api.py::TestRichLoggerGracefulDegradation::test_prompt_fallback_when_rich_unavailable`

#### confirm()

Prompt user for yes/no confirmation.

**Signature**:
```python
def confirm(
    message: str,
    default: bool = False,
    **kwargs
) -> bool
```

**Parameters**:
- **message**: Confirmation message
- **default**: Default value if user provides no input
- **kwargs**: Additional arguments passed to Rich Confirm

**Returns**: Boolean confirmation result

**Example**:
```python
if logger.confirm("Continue?", default=True):
    # User confirmed
    pass
```

**Evidence**: `tests/contract/test_rich_logger_api.py::TestRichLoggerInteractiveMethods::test_confirm_returns_boolean`

**Graceful Degradation**: When Rich is unavailable, returns the default value.
- Evidence: `tests/contract/test_rich_logger_api.py::TestRichLoggerGracefulDegradation::test_confirm_fallback_when_rich_unavailable`

---

## Utility Functions

Utility functions for log level parsing and validation.

### parse_log_level()

Parse log level from string or verbosity count.

**Signature**:
```python
def parse_log_level(
    log_level_str: str | None,
    verbosity: int,
    fallback: LogLevels
) -> LogLevels
```

**Parameters**:
- **log_level_str**: String representation of log level (e.g., "DEBUG", "info")
- **verbosity**: Verbosity count (1-3)
- **fallback**: Fallback log level if neither log_level_str nor verbosity is provided

**Returns**: `LogLevels` enum value

**Behavior**:
- If `verbosity > 0`, uses verbosity to determine level (ignores log_level_str)
- If `verbosity == 0` and `log_level_str` is provided, parses the string
- Otherwise, returns fallback

**Example**:
```python
level = parse_log_level("debug", 0, LogLevels.INFO)  # Returns LogLevels.DEBUG
level = parse_log_level(None, 2, LogLevels.INFO)     # Returns LogLevels.INFO (verbosity 2)
level = parse_log_level(None, 0, LogLevels.WARNING)  # Returns LogLevels.WARNING (fallback)
```

**Evidence**: `tests/contract/test_log_level_utils.py::TestParseLogLevel` (4 tests)

---

### validate_log_level_string()

Validate and convert a string log level to LogLevels enum.

**Signature**:
```python
def validate_log_level_string(
    value: str,
    options_class: type[LogLevelOptions] = LogLevelOptions
) -> LogLevels
```

**Parameters**:
- **value**: String representation of log level
- **options_class**: Class containing log level options (default: LogLevelOptions)

**Returns**: `LogLevels` enum value

**Raises**: `ValueError` if the log level string is invalid

**Supported Values** (case-insensitive):
- `"DEBUG"`, `"debug"`, `"DeBuG"` → `LogLevels.DEBUG`
- `"INFO"`, `"info"` → `LogLevels.INFO`
- `"WARNING"`, `"warning"`, `"WARN"`, `"warn"` → `LogLevels.WARNING`
- `"ERROR"`, `"error"` → `LogLevels.ERROR`
- `"CRITICAL"`, `"critical"`, `"FATAL"`, `"fatal"` → `LogLevels.CRITICAL`

**Example**:
```python
level = validate_log_level_string("debug")    # LogLevels.DEBUG
level = validate_log_level_string("INFO")     # LogLevels.INFO
level = validate_log_level_string("warn")     # LogLevels.WARNING
level = validate_log_level_string("invalid")  # Raises ValueError
```

**Evidence**: `tests/contract/test_log_level_utils.py::TestValidateLogLevelString` (16 tests)

---

### get_log_level_from_verbosity()

Convert verbosity count to LogLevels enum.

**Signature**:
```python
def get_log_level_from_verbosity(verbosity: int) -> LogLevels
```

**Parameters**:
- **verbosity**: Verbosity count (0-3)

**Returns**: `LogLevels` enum value

**Raises**: `ValueError` if verbosity is negative or exceeds maximum (3)

**Mapping**:
- `0` → `LogLevels.CRITICAL`
- `1` → `LogLevels.ERROR`
- `2` → `LogLevels.INFO`
- `3` → `LogLevels.DEBUG`

**Example**:
```python
level = get_log_level_from_verbosity(0)  # LogLevels.CRITICAL
level = get_log_level_from_verbosity(1)  # LogLevels.ERROR
level = get_log_level_from_verbosity(2)  # LogLevels.INFO
level = get_log_level_from_verbosity(3)  # LogLevels.DEBUG
level = get_log_level_from_verbosity(-1) # Raises ValueError
level = get_log_level_from_verbosity(4)  # Raises ValueError
```

**Evidence**: `tests/contract/test_log_level_utils.py::TestGetLogLevelFromVerbosity` (6 tests)

---

## Graceful Degradation

All Rich features gracefully degrade when Rich is unavailable or disabled:

- **Display methods** (table, panel, rule, etc.): Silently do nothing
  - Evidence: `tests/contract/test_rich_logger_api.py::TestRichLoggerGracefulDegradation::test_table_fallback_when_rich_unavailable`
  - Evidence: `tests/contract/test_rich_logger_api.py::TestRichLoggerGracefulDegradation::test_panel_fallback_when_rich_unavailable`

- **Context managers** (progress, status, live): Return dummy objects
  - Evidence: `tests/contract/test_rich_logger_api.py::TestRichLoggerGracefulDegradation::test_progress_fallback_when_rich_unavailable`
  - Evidence: `tests/contract/test_rich_logger_api.py::TestRichLoggerGracefulDegradation::test_status_fallback_when_rich_unavailable`

- **Interactive methods** (prompt, confirm): Return default values
  - Evidence: `tests/contract/test_rich_logger_api.py::TestRichLoggerGracefulDegradation::test_prompt_fallback_when_rich_unavailable`
  - Evidence: `tests/contract/test_rich_logger_api.py::TestRichLoggerGracefulDegradation::test_confirm_fallback_when_rich_unavailable`

Standard logging methods always work regardless of Rich availability.

