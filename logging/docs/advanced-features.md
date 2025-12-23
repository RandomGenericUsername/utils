# Advanced Features Guide

Guide to advanced Rich features in the `rich-logging` library. All examples are verified by tests.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Display Methods](#display-methods)
  - [Tables](#tables)
  - [Panels](#panels)
  - [Rules](#rules)
  - [Syntax Highlighting](#syntax-highlighting)
  - [Markdown](#markdown)
  - [JSON](#json)
- [Context Managers](#context-managers)
  - [Progress Tracking](#progress-tracking)
  - [Status Spinner](#status-spinner)
  - [Live Updates](#live-updates)
- [Task Context](#task-context)
- [Interactive Methods](#interactive-methods)
  - [Prompts](#prompts)
  - [Confirmations](#confirmations)
- [Graceful Degradation](#graceful-degradation)

---

## Prerequisites

To use Rich features, you must:

1. Enable Rich console handler
2. Enable Rich features in settings

```python
from rich_logging import Log, LogLevels, ConsoleHandlers, RichFeatureSettings

logger = Log.create_logger(
    "myapp",
    log_level=LogLevels.INFO,
    console_handler_type=ConsoleHandlers.RICH,
    rich_features=RichFeatureSettings(enabled=True)
)
```

**Evidence**: `tests/integration/test_rich_features.py::TestRichDisplayFeatures` (all tests)

---

## Display Methods

### Tables

Display data in a formatted table.

**Basic Usage**:
```python
# First row as headers
logger.table(
    [["Name", "Age"], ["Alice", "30"], ["Bob", "25"]],
    show_header=True
)
```

**With Title**:
```python
logger.table(
    [["Name", "Age"], ["Alice", "30"], ["Bob", "25"]],
    show_header=True,
    title="Users"
)
```

**Custom Styling**:
```python
from rich_logging import RichFeatureSettings

rich_settings = RichFeatureSettings(
    enabled=True,
    table_show_lines=True,  # Show lines between rows
    table_expand=True       # Expand to fill width
)

logger = Log.create_logger(
    "myapp",
    log_level=LogLevels.INFO,
    console_handler_type=ConsoleHandlers.RICH,
    rich_features=rich_settings
)

logger.table(
    [["Name", "Age"], ["Alice", "30"], ["Bob", "25"]],
    show_header=True
)
```

**Evidence**: `tests/integration/test_rich_features.py::TestRichDisplayFeatures::test_table_displays_data`

---

### Panels

Display messages in bordered panels.

**Basic Usage**:
```python
logger.panel("Important message")
```

**With Title and Styling**:
```python
logger.panel(
    "Critical alert!",
    title="Alert",
    border_style="red"
)
```

**Custom Settings**:
```python
from rich_logging import RichFeatureSettings

rich_settings = RichFeatureSettings(
    enabled=True,
    panel_border_style="green",
    panel_box_style="double",
    panel_padding=(1, 2)  # (vertical, horizontal)
)

logger = Log.create_logger(
    "myapp",
    log_level=LogLevels.INFO,
    console_handler_type=ConsoleHandlers.RICH,
    rich_features=rich_settings
)

logger.panel("Success!", title="Status")
```

**Evidence**: `tests/integration/test_rich_features.py::TestRichDisplayFeatures::test_panel_displays_message`

---

### Rules

Display horizontal separators with optional titles.

**Basic Usage**:
```python
logger.rule()  # Simple separator
```

**With Title**:
```python
logger.rule("Section 1")
```

**Custom Styling**:
```python
logger.rule("Important Section", style="bold red")
```

**Evidence**: `tests/integration/test_rich_features.py::TestRichDisplayFeatures::test_rule_displays_separator`

---

### Syntax Highlighting

Display syntax-highlighted code.

**Basic Usage**:
```python
code = '''
def hello():
    print("Hello, world!")
'''

logger.syntax(code, "python")
```

**With Line Numbers**:
```python
from rich_logging import RichFeatureSettings

rich_settings = RichFeatureSettings(
    enabled=True,
    syntax_line_numbers=True,
    syntax_theme="monokai"
)

logger = Log.create_logger(
    "myapp",
    log_level=LogLevels.INFO,
    console_handler_type=ConsoleHandlers.RICH,
    rich_features=rich_settings
)

logger.syntax(code, "python")
```

**Different Languages**:
```python
# JavaScript
logger.syntax('const x = 42;', "javascript")

# JSON
logger.syntax('{"key": "value"}', "json")

# Bash
logger.syntax('echo "Hello"', "bash")
```

**Evidence**: `tests/integration/test_rich_features.py::TestRichDisplayFeatures::test_syntax_displays_code`

---

### Markdown

Display formatted markdown text.

**Basic Usage**:
```python
markdown_text = """
# Title

This is a paragraph with **bold** and *italic* text.

## Subsection

- Item 1
- Item 2
- Item 3

```python
def example():
    pass
```
"""

logger.markdown(markdown_text)
```

**Custom Settings**:
```python
from rich_logging import RichFeatureSettings

rich_settings = RichFeatureSettings(
    enabled=True,
    markdown_code_theme="dracula",
    markdown_hyperlinks=True
)

logger = Log.create_logger(
    "myapp",
    log_level=LogLevels.INFO,
    console_handler_type=ConsoleHandlers.RICH,
    rich_features=rich_settings
)

logger.markdown("# Title\n\nParagraph")
```

**Evidence**: `tests/integration/test_rich_features.py::TestRichDisplayFeatures::test_markdown_displays_formatted_text`

---

### JSON

Display formatted JSON data.

**From Dictionary**:
```python
data = {
    "status": "success",
    "count": 42,
    "items": ["a", "b", "c"]
}

logger.json(data)
```

**From JSON String**:
```python
json_string = '{"status": "success", "count": 42}'
logger.json(json_string)
```

**Custom Settings**:
```python
from rich_logging import RichFeatureSettings

rich_settings = RichFeatureSettings(
    enabled=True,
    json_indent=4,
    json_sort_keys=True,
    json_highlight=True
)

logger = Log.create_logger(
    "myapp",
    log_level=LogLevels.INFO,
    console_handler_type=ConsoleHandlers.RICH,
    rich_features=rich_settings
)

logger.json({"key": "value", "number": 42})
```

**Evidence**: `tests/integration/test_rich_features.py::TestRichDisplayFeatures::test_json_displays_formatted_json`

---

## Context Managers

### Progress Tracking

Track progress of long-running operations with progress bars.

**Basic Usage**:
```python
with logger.progress("Processing", total=100) as progress:
    task = progress.add_task("Processing items", total=100)

    for i in range(100):
        # Do work
        time.sleep(0.01)
        progress.update(task, advance=1)
```

**Multiple Tasks**:
```python
with logger.progress() as progress:
    task1 = progress.add_task("Task 1", total=50)
    task2 = progress.add_task("Task 2", total=100)

    for i in range(50):
        progress.update(task1, advance=1)
        time.sleep(0.01)

    for i in range(100):
        progress.update(task2, advance=1)
        time.sleep(0.01)
```

**Custom Settings**:
```python
from rich_logging import RichFeatureSettings

rich_settings = RichFeatureSettings(
    enabled=True,
    progress_refresh_per_second=20,
    progress_auto_refresh=True
)

logger = Log.create_logger(
    "myapp",
    log_level=LogLevels.INFO,
    console_handler_type=ConsoleHandlers.RICH,
    rich_features=rich_settings
)

with logger.progress() as progress:
    task = progress.add_task("Processing", total=100)
    # ...
```

**Evidence**: `tests/integration/test_rich_features.py::TestRichContextManagers::test_progress_context_manager_workflow`

---

### Status Spinner

Display a status spinner for operations without known duration.

**Basic Usage**:
```python
with logger.status("Loading..."):
    # Do work
    time.sleep(2)
```

**Custom Spinner**:
```python
with logger.status("Processing...", spinner="dots"):
    # Do work
    time.sleep(2)
```

**Available Spinners**: `"dots"`, `"line"`, `"arc"`, `"arrow"`, `"bounce"`, `"circle"`, `"moon"`, `"star"`, and many more.

**Custom Settings**:
```python
from rich_logging import RichFeatureSettings

rich_settings = RichFeatureSettings(
    enabled=True,
    status_spinner="moon",
    status_refresh_per_second=15
)

logger = Log.create_logger(
    "myapp",
    log_level=LogLevels.INFO,
    console_handler_type=ConsoleHandlers.RICH,
    rich_features=rich_settings
)

with logger.status("Loading..."):
    # Do work
    pass
```

**Evidence**: `tests/contract/test_rich_logger_api.py::TestRichLoggerContextManagers::test_status_context_manager`

---

### Live Updates

Create live-updating displays that can be modified in real-time.

**Basic Usage**:
```python
from rich.table import Table

table = Table()
table.add_column("Name")
table.add_column("Status")

with logger.live(table, refresh_per_second=4) as live:
    for i in range(10):
        table.add_row(f"Task {i}", "Processing")
        time.sleep(0.5)
        # Table updates automatically
```

**Custom Settings**:
```python
from rich_logging import RichFeatureSettings

rich_settings = RichFeatureSettings(
    enabled=True,
    live_refresh_per_second=10,
    live_vertical_overflow="ellipsis",
    live_auto_refresh=True
)

logger = Log.create_logger(
    "myapp",
    log_level=LogLevels.INFO,
    console_handler_type=ConsoleHandlers.RICH,
    rich_features=rich_settings
)

with logger.live(table) as live:
    # Update table
    pass
```

**Evidence**: `tests/contract/test_rich_logger_api.py::TestRichLoggerContextManagers::test_live_context_manager`

---

## Task Context

Task context is useful for parallel execution where multiple tasks run concurrently.

### Manual Context Management

```python
import concurrent.futures

def process_item(item_id):
    logger.set_task_context(f"item_{item_id}", f"Processing Item {item_id}")

    logger.info(f"Starting processing")
    # Do work
    logger.info(f"Completed processing")

    logger.clear_task_context()

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    executor.map(process_item, range(10))
```

**Evidence**: `tests/integration/test_rich_features.py::TestTaskContext::test_task_context_workflow`

### Context Manager (Recommended)

```python
import concurrent.futures

def process_item(item_id):
    with logger.task_context(f"item_{item_id}", f"Processing Item {item_id}"):
        logger.info(f"Starting processing")
        # Do work
        logger.info(f"Completed processing")
        # Context automatically cleared

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    executor.map(process_item, range(10))
```

**Benefits**:
- Automatic cleanup even if exception occurs
- Cleaner code
- Thread-safe

**Evidence**: `tests/contract/test_rich_logger_api.py::TestRichLoggerTaskContext::test_task_context_manager`

---

## Interactive Methods

### Prompts

Prompt users for input with Rich styling.

**Basic Prompt**:
```python
name = logger.prompt("Enter your name")
```

**With Default Value**:
```python
name = logger.prompt("Enter your name", default="User")
```

**With Choices**:
```python
choice = logger.prompt(
    "Select an option",
    choices=["Option A", "Option B", "Option C"]
)
```

**Custom Settings**:
```python
from rich_logging import RichFeatureSettings

rich_settings = RichFeatureSettings(
    enabled=True,
    prompt_show_default=True,
    prompt_show_choices=True
)

logger = Log.create_logger(
    "myapp",
    log_level=LogLevels.INFO,
    console_handler_type=ConsoleHandlers.RICH,
    rich_features=rich_settings
)

name = logger.prompt("Enter your name", default="User")
```

**Evidence**: `tests/contract/test_rich_logger_api.py::TestRichLoggerInteractiveMethods::test_prompt_returns_user_input`

---

### Confirmations

Prompt users for yes/no confirmation.

**Basic Confirmation**:
```python
if logger.confirm("Continue?"):
    # User confirmed
    pass
```

**With Default Value**:
```python
# Default to True (yes)
if logger.confirm("Continue?", default=True):
    pass

# Default to False (no)
if logger.confirm("Delete file?", default=False):
    pass
```

**Evidence**: `tests/contract/test_rich_logger_api.py::TestRichLoggerInteractiveMethods::test_confirm_returns_boolean`

---

## Graceful Degradation

All Rich features gracefully degrade when Rich is unavailable or disabled.

### When Rich is Disabled

```python
from rich_logging import RichFeatureSettings

# Disable Rich features
rich_settings = RichFeatureSettings(enabled=False)

logger = Log.create_logger(
    "myapp",
    log_level=LogLevels.INFO,
    rich_features=rich_settings
)

# These methods do nothing but don't raise errors
logger.table([["Name", "Age"], ["Alice", "30"]], show_header=True)
logger.panel("Message")
logger.rule("Section")

# Context managers return dummy objects
with logger.progress() as progress:
    # progress has add_task method but doesn't display anything
    task = progress.add_task("Task", total=100)
    progress.update(task, advance=1)

# Interactive methods return default values
name = logger.prompt("Name", default="User")  # Returns "User"
confirmed = logger.confirm("Continue?", default=True)  # Returns True
```

**Evidence**:
- `tests/integration/test_rich_features.py::TestRichContextManagers::test_progress_fallback_when_disabled`
- `tests/contract/test_rich_logger_api.py::TestRichLoggerGracefulDegradation::test_table_fallback_when_rich_unavailable`
- `tests/contract/test_rich_logger_api.py::TestRichLoggerGracefulDegradation::test_panel_fallback_when_rich_unavailable`
- `tests/contract/test_rich_logger_api.py::TestRichLoggerGracefulDegradation::test_progress_fallback_when_rich_unavailable`
- `tests/contract/test_rich_logger_api.py::TestRichLoggerGracefulDegradation::test_prompt_fallback_when_rich_unavailable`
- `tests/contract/test_rich_logger_api.py::TestRichLoggerGracefulDegradation::test_confirm_fallback_when_rich_unavailable`

### Standard Logging Always Works

Standard logging methods (`info()`, `debug()`, `warning()`, `error()`, `critical()`) always work regardless of Rich availability:

```python
# These always work
logger.info("Information")
logger.error("Error occurred")
logger.debug("Debug info")
```

**Evidence**: `tests/contract/test_rich_logger_api.py::TestRichLoggerStandardLogging` (all tests)

---

## Best Practices

### 1. Enable Rich Features Explicitly

Always explicitly enable Rich features when you need them:

```python
rich_settings = RichFeatureSettings(enabled=True)
logger = Log.create_logger(
    "myapp",
    log_level=LogLevels.INFO,
    console_handler_type=ConsoleHandlers.RICH,
    rich_features=rich_settings
)
```

### 2. Use Context Managers for Cleanup

Always use context managers for progress, status, live, and task context:

```python
# Good
with logger.progress() as progress:
    # ...

# Avoid manual cleanup
progress = logger.progress()
# ... (might forget to clean up)
```

### 3. Provide Default Values for Interactive Methods

Always provide sensible defaults for prompts and confirmations:

```python
# Good
name = logger.prompt("Enter name", default="User")
confirmed = logger.confirm("Continue?", default=False)

# Avoid (no fallback when Rich disabled)
name = logger.prompt("Enter name")
```

### 4. Configure Settings Once

Create RichFeatureSettings once and reuse:

```python
# Good
rich_settings = RichFeatureSettings(
    enabled=True,
    table_show_lines=True,
    syntax_line_numbers=True
)

logger1 = Log.create_logger("app1", log_level=LogLevels.INFO, rich_features=rich_settings)
logger2 = Log.create_logger("app2", log_level=LogLevels.INFO, rich_features=rich_settings)
```

### 5. Use Task Context for Parallel Execution

When running tasks in parallel, always use task context:

```python
import concurrent.futures

def process_item(item_id):
    with logger.task_context(f"item_{item_id}"):
        logger.info("Processing")
        # Do work

with concurrent.futures.ThreadPoolExecutor() as executor:
    executor.map(process_item, range(10))
```

---

## See Also

- [API Reference](api-reference.md) - Complete API documentation
- [Usage Guide](usage-guide.md) - Getting started and common workflows
- [Configuration Reference](configuration.md) - All configuration options

