# Configuration Reference

Complete reference for all configuration options in the `rich-logging` library.

---

## Table of Contents

- [LogConfig](#logconfig)
- [Enumerations](#enumerations)
  - [LogLevels](#loglevels)
  - [ConsoleHandlers](#consolehandlers)
  - [LogFormatters](#logformatters)
  - [LogFormatterStyleChoices](#logformatterstylechoices)
  - [FileHandlerTypes](#filehandlertypes)
- [RichFeatureSettings](#richfeaturesettings)
- [ColoredFormatterColors](#coloredformattercolors)
- [FileHandlerSpec](#filehandlerspec)

---

## LogConfig

Dataclass for logger configuration. All parameters are optional except `log_level`.

**Source**: `rich_logging.core.log_types.LogConfig`

### Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `log_level` | `LogLevels` | **Required** | Log level for the logger |
| `formatter_style` | `LogFormatterStyleChoices \| None` | `None` | Format style (%, {}, $) |
| `format` | `str \| None` | `None` | Format string for log messages |
| `formatter_type` | `LogFormatters \| None` | `None` | Type of formatter to use |
| `name` | `str \| None` | `None` | Logger name |
| `colors` | `ColoredFormatterColors \| None` | `None` | Color scheme for colored formatter |
| `console_handler` | `ConsoleHandlers` | `ConsoleHandlers.DEFAULT` | Type of console handler |
| `handler_config` | `RichHandlerSettings \| None` | `None` | Console handler configuration |
| `file_handlers` | `list[FileHandlerSpec] \| None` | `None` | File handler specifications |
| `rich_features` | `RichFeatureSettings \| None` | `None` | Rich features configuration |

### Example

```python
from rich_logging import LogConfig, LogLevels, ConsoleHandlers, RichFeatureSettings

config = LogConfig(
    name="myapp",
    log_level=LogLevels.DEBUG,
    console_handler=ConsoleHandlers.RICH,
    rich_features=RichFeatureSettings(enabled=True)
)

logger = Log.create_logger(config=config)
```

**Evidence**: `tests/contract/test_log_api.py::TestLogCreateLogger::test_create_logger_with_config_object`

---

## Enumerations

### LogLevels

Log level enumeration mapping to standard Python logging levels.

**Source**: `rich_logging.core.log_types.LogLevels`

| Value | Numeric Value | Description |
|-------|---------------|-------------|
| `LogLevels.DEBUG` | 10 | Detailed debugging information |
| `LogLevels.INFO` | 20 | General informational messages |
| `LogLevels.WARNING` | 30 | Warning messages |
| `LogLevels.ERROR` | 40 | Error messages |
| `LogLevels.CRITICAL` | 50 | Critical errors |

**Example**:
```python
from rich_logging import Log, LogLevels

logger = Log.create_logger("myapp", log_level=LogLevels.DEBUG)
```

**Evidence**: 
- `tests/contract/test_log_api.py::TestLogCreateLogger::test_create_logger_with_debug_level`
- `tests/contract/test_log_api.py::TestLogCreateLogger::test_create_logger_with_info_level`
- `tests/contract/test_log_api.py::TestLogCreateLogger::test_create_logger_with_warning_level`
- `tests/contract/test_log_api.py::TestLogCreateLogger::test_create_logger_with_error_level`
- `tests/contract/test_log_api.py::TestLogCreateLogger::test_create_logger_with_critical_level`

---

### ConsoleHandlers

Console handler types.

**Source**: `rich_logging.core.log_types.ConsoleHandlers`

| Value | Description |
|-------|-------------|
| `ConsoleHandlers.DEFAULT` | Standard Python logging StreamHandler |
| `ConsoleHandlers.RICH` | Rich console handler with enhanced formatting |

**Example**:
```python
from rich_logging import Log, LogLevels, ConsoleHandlers

# Standard handler
logger = Log.create_logger(
    "myapp",
    log_level=LogLevels.INFO,
    console_handler_type=ConsoleHandlers.DEFAULT
)

# Rich handler
logger = Log.create_logger(
    "myapp",
    log_level=LogLevels.INFO,
    console_handler_type=ConsoleHandlers.RICH
)
```

**Evidence**:
- `tests/contract/test_log_api.py::TestLogCreateLogger::test_create_logger_with_console_handler_default`
- `tests/contract/test_log_api.py::TestLogCreateLogger::test_create_logger_with_console_handler_rich`

---

### LogFormatters

Formatter types for log messages.

**Source**: `rich_logging.core.log_types.LogFormatters`

| Value | Description |
|-------|-------------|
| `LogFormatters.DEFAULT` | Standard Python logging formatter |
| `LogFormatters.COLORED` | Colored formatter with ANSI color codes |
| `LogFormatters.RICH` | Rich formatter with enhanced styling |

**Example**:
```python
from rich_logging import Log, LogLevels, LogFormatters

logger = Log.create_logger(
    "myapp",
    log_level=LogLevels.INFO,
    formatter_type=LogFormatters.COLORED
)
```

**Evidence**:
- `tests/unit/test_formatter_factory.py::TestFormatterFactory::test_create_default_formatter`
- `tests/unit/test_formatter_factory.py::TestFormatterFactory::test_create_colored_formatter`
- `tests/unit/test_formatter_factory.py::TestFormatterFactory::test_create_rich_formatter`

---

### LogFormatterStyleChoices

Format string styles for log messages.

**Source**: `rich_logging.core.log_types.LogFormatterStyleChoices`

| Value | Style | Example Format String |
|-------|-------|----------------------|
| `LogFormatterStyleChoices.PERCENT` | `%` | `"%(asctime)s - %(message)s"` |
| `LogFormatterStyleChoices.BRACE` | `{` | `"{asctime} - {message}"` |
| `LogFormatterStyleChoices.DOLLAR` | `$` | `"$asctime - $message"` |

**Example**:
```python
from rich_logging import Log, LogLevels, LogFormatterStyleChoices

logger = Log.create_logger(
    "myapp",
    log_level=LogLevels.INFO,
    formatter_style=LogFormatterStyleChoices.BRACE,
    format="{asctime} | {levelname} | {message}"
)
```

**Evidence**:
- `tests/unit/test_formatter_factory.py::TestFormatterFactory::test_create_formatter_with_percent_style`
- `tests/unit/test_formatter_factory.py::TestFormatterFactory::test_create_formatter_with_brace_style`
- `tests/unit/test_formatter_factory.py::TestFormatterFactory::test_create_formatter_with_dollar_style`

---

### FileHandlerTypes

File handler types for logging to files.

**Source**: `rich_logging.core.log_types.FileHandlerTypes`

| Value | Description |
|-------|-------------|
| `FileHandlerTypes.FILE` | Standard file handler |
| `FileHandlerTypes.ROTATING_FILE` | Rotating file handler (size-based rotation) |
| `FileHandlerTypes.TIMED_ROTATING_FILE` | Timed rotating file handler (time-based rotation) |

---

## RichFeatureSettings

Dataclass for configuring Rich features. All fields have sensible defaults.

**Source**: `rich_logging.rich.rich_feature_settings.RichFeatureSettings`

### Global Settings

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enabled` | `bool` | `True` | Whether Rich features are enabled (fallback to no-op if False) |

**Evidence**: `tests/contract/test_rich_logger_api.py::TestRichLoggerProperties::test_logger_has_rich_settings`

### Table Settings

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `table_show_header` | `bool` | `True` | Whether to show table headers by default |
| `table_show_lines` | `bool` | `False` | Whether to show lines between table rows |
| `table_show_edge` | `bool` | `True` | Whether to show table border |
| `table_expand` | `bool` | `False` | Whether tables should expand to fill available width |

### Panel Settings

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `panel_border_style` | `str` | `"blue"` | Default border color/style for panels |
| `panel_box_style` | `str` | `"rounded"` | Default box style ('rounded', 'square', 'double', 'heavy', 'ascii') |
| `panel_expand` | `bool` | `True` | Whether panels should expand to fill available width |
| `panel_padding` | `tuple[int, int]` | `(0, 1)` | Default padding (vertical, horizontal) |

### Rule Settings

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `rule_style` | `str` | `"rule.line"` | Default style for rules/separators |
| `rule_align` | `str` | `"center"` | Default alignment for rule titles ('left', 'center', 'right') |

### Progress Settings

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `progress_auto_refresh` | `bool` | `True` | Whether progress bars should auto-refresh |
| `progress_refresh_per_second` | `int` | `10` | Refresh rate for progress bars (times per second) |
| `progress_speed_estimate_period` | `float` | `30.0` | Period for speed estimation (seconds) |

### Status Settings

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `status_spinner` | `str` | `"dots"` | Default spinner style for status indicators |
| `status_refresh_per_second` | `float` | `12.5` | Refresh rate for status spinners (times per second) |

### Console Settings

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `console_width` | `int \| None` | `None` | Fixed console width (None for auto-detection) |
| `console_height` | `int \| None` | `None` | Fixed console height (None for auto-detection) |

### Syntax Highlighting Settings

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `syntax_theme` | `str` | `"monokai"` | Default theme for syntax highlighting |
| `syntax_line_numbers` | `bool` | `False` | Whether to show line numbers |
| `syntax_word_wrap` | `bool` | `False` | Whether to enable word wrap |
| `syntax_background_color` | `str \| None` | `None` | Background color (None for default) |

### Markdown Settings

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `markdown_code_theme` | `str` | `"monokai"` | Theme for code blocks in markdown |
| `markdown_hyperlinks` | `bool` | `True` | Whether to enable hyperlinks |
| `markdown_inline_code_lexer` | `str \| None` | `None` | Lexer for inline code |

### JSON Settings

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `json_indent` | `int` | `2` | Default indentation for JSON display |
| `json_highlight` | `bool` | `True` | Whether to enable syntax highlighting |
| `json_sort_keys` | `bool` | `False` | Whether to sort keys in JSON display |

### Live Display Settings

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `live_refresh_per_second` | `int` | `4` | Refresh rate for live displays (times per second) |
| `live_vertical_overflow` | `str` | `"ellipsis"` | How to handle vertical overflow ('crop', 'ellipsis', 'visible') |
| `live_auto_refresh` | `bool` | `True` | Whether live displays should auto-refresh |

### Prompt Settings

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `prompt_show_default` | `bool` | `True` | Whether to show default values in prompts |
| `prompt_show_choices` | `bool` | `True` | Whether to show available choices in prompts |

### Example

```python
from rich_logging import Log, LogLevels, ConsoleHandlers, RichFeatureSettings

# Custom Rich settings
rich_settings = RichFeatureSettings(
    enabled=True,
    table_show_lines=True,
    panel_border_style="red",
    syntax_line_numbers=True,
    json_indent=4
)

logger = Log.create_logger(
    "myapp",
    log_level=LogLevels.INFO,
    console_handler_type=ConsoleHandlers.RICH,
    rich_features=rich_settings
)
```

---

## ColoredFormatterColors

Dataclass for ANSI color codes used in colored formatter.

**Source**: `rich_logging.core.log_types.ColoredFormatterColors`

### Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `DEBUG` | `str` | `"\033[36m"` | Cyan color for DEBUG messages |
| `INFO` | `str` | `"\033[32m"` | Green color for INFO messages |
| `WARNING` | `str` | `"\033[33m"` | Yellow color for WARNING messages |
| `ERROR` | `str` | `"\033[31m"` | Red color for ERROR messages |
| `CRITICAL` | `str` | `"\033[35m"` | Magenta color for CRITICAL messages |
| `RESET` | `str` | `"\033[0m"` | Reset color code |

### Example

```python
from rich_logging import Log, LogLevels, LogFormatters, ColoredFormatterColors

# Custom colors
custom_colors = ColoredFormatterColors(
    DEBUG="\033[94m",    # Bright blue
    INFO="\033[92m",     # Bright green
    WARNING="\033[93m",  # Bright yellow
    ERROR="\033[91m",    # Bright red
    CRITICAL="\033[95m"  # Bright magenta
)

logger = Log.create_logger(
    "myapp",
    log_level=LogLevels.INFO,
    formatter_type=LogFormatters.COLORED,
    colors=custom_colors
)
```

---

## FileHandlerSpec

Dataclass for specifying file handler configuration.

**Source**: `rich_logging.core.log_types.FileHandlerSpec`

### Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `handler_type` | `FileHandlerTypes` | **Required** | Type of file handler |
| `config` | `BaseFileHandlerSettings` | **Required** | File handler configuration |
| `formatter_override` | `LogFormatters \| None` | `None` | Override formatter type for this handler |
| `format_override` | `str \| None` | `None` | Override format string for this handler |

### Example

```python
from rich_logging import (
    Log,
    LogLevels,
    FileHandlerSpec,
    FileHandlerTypes,
    FileHandlerSettings
)

# File handler configuration
file_config = FileHandlerSettings(
    filename="app.log",
    mode="a",
    encoding="utf-8"
)

file_spec = FileHandlerSpec(
    handler_type=FileHandlerTypes.FILE,
    config=file_config
)

logger = Log.create_logger(
    "myapp",
    log_level=LogLevels.INFO,
    file_handlers=[file_spec]
)
```

---

## Validation

### RichFeatureSettings Validation

`RichFeatureSettings` validates configuration on initialization:

- `progress_refresh_per_second` must be positive
- `status_refresh_per_second` must be positive
- `progress_speed_estimate_period` must be positive
- `panel_box_style` must be one of: 'rounded', 'square', 'double', 'heavy', 'ascii'
- `rule_align` must be one of: 'left', 'center', 'right'
- `panel_padding` must be a tuple of 2 non-negative integers
- `json_indent` must be non-negative
- `live_refresh_per_second` must be positive
- `live_vertical_overflow` must be one of: 'crop', 'ellipsis', 'visible'
- `text_justify` must be one of: 'left', 'center', 'right', 'full'
- `text_overflow` must be one of: 'crop', 'fold', 'ellipsis'

Invalid values raise `ValueError` with descriptive error messages.

---

## See Also

- [API Reference](api-reference.md) - Complete API documentation
- [Usage Guide](usage-guide.md) - Getting started and common workflows
- [Advanced Features](advanced-features.md) - Rich display methods and context managers

