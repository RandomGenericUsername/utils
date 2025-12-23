# Architecture Documentation

System design and component relationships for the `rich-logging` library.

---

## Table of Contents

- [Overview](#overview)
- [Component Structure](#component-structure)
- [Design Patterns](#design-patterns)
- [Module Organization](#module-organization)
- [Data Flow](#data-flow)
- [Extension Points](#extension-points)

---

## Overview

The `rich-logging` library is a comprehensive Python logging solution that enhances standard logging with Rich console features. It follows a layered architecture with clear separation of concerns.

### Key Principles

1. **Backward Compatibility**: Full compatibility with Python's standard `logging` module
2. **Graceful Degradation**: All Rich features degrade gracefully when unavailable
3. **Type Safety**: Extensive use of type hints and dataclasses
4. **Extensibility**: Factory patterns for formatters and handlers
5. **Thread Safety**: Thread-local storage for task context

---

## Component Structure

```
rich-logging/
├── Log (Facade)                    # Main entry point
├── RichLogger (Wrapper)            # Enhanced logger wrapper
├── LoggerConfigurator              # Logger configuration
├── Factories                       # Component creation
│   ├── FormatterFactory
│   └── HandlerFactory
├── Formatters                      # Log formatting
│   ├── DefaultFormatter
│   ├── ColoredFormatter
│   └── RichFormatter
├── Handlers                        # Log output
│   ├── ConsoleHandler
│   ├── RichHandler
│   └── FileHandlers
├── Filters                         # Log filtering
│   └── TaskContextFilter
├── Rich Components                 # Rich features
│   ├── RichConsoleManager
│   └── RichFeatureSettings
└── Core Types                      # Type definitions
    ├── LogConfig
    ├── LogLevels
    └── Enums
```

---

## Design Patterns

### 1. Facade Pattern

**Component**: `Log` class

The `Log` class provides a simplified interface to the complex logging subsystem:

```python
# Simple facade interface
logger = Log.create_logger("myapp", log_level=LogLevels.INFO)
logger = Log.update("myapp", log_level=LogLevels.DEBUG)
```

**Location**: `src/rich_logging/log.py`

**Benefits**:
- Hides complexity of logger configuration
- Provides consistent API
- Manages logger registry

**Evidence**: `tests/contract/test_log_api.py::TestLogCreateLogger`, `tests/contract/test_log_api.py::TestLogUpdate`

---

### 2. Wrapper Pattern

**Component**: `RichLogger` class

`RichLogger` wraps `logging.Logger` to add Rich features while maintaining full compatibility:

```python
class RichLogger:
    def __init__(self, logger: logging.Logger, rich_settings: RichFeatureSettings):
        self._logger = logger
        self._rich_settings = rich_settings
    
    def __getattr__(self, name: str):
        """Delegate all standard logging methods to wrapped logger."""
        return getattr(self._logger, name)
```

**Location**: `src/rich_logging/rich/rich_logger.py`

**Benefits**:
- Adds Rich features without modifying stdlib logger
- Full backward compatibility
- Transparent delegation

**Evidence**: `tests/contract/test_rich_logger_api.py::TestRichLoggerStandardLogging`

---

### 3. Factory Pattern

**Components**: `FormatterFactory`, `HandlerFactory`

Factories create formatters and handlers based on configuration:

```python
class FormatterFactory:
    @staticmethod
    def create(
        formatter_type: LogFormatters,
        format_string: str,
        style: LogFormatterStyleChoices,
        colors: ColoredFormatterColors | None = None
    ) -> logging.Formatter:
        # Create appropriate formatter based on type
        ...
```

**Location**: 
- `src/rich_logging/formatters/base.py` (FormatterFactory)
- `src/rich_logging/handlers/base.py` (HandlerFactory)

**Benefits**:
- Centralized creation logic
- Easy to add new formatter/handler types
- Consistent configuration

**Evidence**: `tests/unit/test_formatter_factory.py::TestFormatterFactory`

---

### 4. Singleton Pattern

**Component**: `RichConsoleManager`

Manages shared Rich Console instances across loggers:

```python
# Global singleton instance
console_manager = RichConsoleManager()

# Usage
console = console_manager.get_console(logger_name)
```

**Location**: `src/rich_logging/rich/rich_console_manager.py`

**Benefits**:
- Shared console instances
- Consistent output
- Resource efficiency

---

### 5. Strategy Pattern

**Component**: Formatter types

Different formatting strategies (DEFAULT, COLORED, RICH) can be selected at runtime:

```python
logger = Log.create_logger(
    "myapp",
    log_level=LogLevels.INFO,
    formatter_type=LogFormatters.COLORED  # Strategy selection
)
```

**Location**: `src/rich_logging/formatters/`

**Benefits**:
- Flexible formatting
- Easy to switch strategies
- Extensible

---

## Module Organization

### Core Module (`core/`)

**Purpose**: Core types, utilities, and configuration

**Components**:
- `log_types.py`: Type definitions (LogConfig, LogLevels, enums)
- `utils.py`: Utility functions (log level parsing, validation)
- `configurator.py`: Logger configuration logic
- `log_context.py`: Thread-local task context

**Evidence**: `tests/contract/test_log_level_utils.py`

---

### Formatters Module (`formatters/`)

**Purpose**: Log message formatting

**Components**:
- `base.py`: FormatterFactory
- `colored.py`: ColoredFormatter (ANSI colors)
- `rich.py`: RichFormatter (Rich styling)

**Evidence**: `tests/unit/test_formatter_factory.py`

---

### Handlers Module (`handlers/`)

**Purpose**: Log output destinations

**Components**:
- `base.py`: HandlerFactory
- `console.py`: Console handlers (DEFAULT, RICH)
- `file.py`: File handlers (FILE, ROTATING_FILE, TIMED_ROTATING_FILE)
- `file_settings.py`: File handler configuration
- `rich_settings.py`: Rich handler configuration

---

### Rich Module (`rich/`)

**Purpose**: Rich console features

**Components**:
- `rich_logger.py`: RichLogger wrapper
- `rich_console_manager.py`: Console management
- `rich_feature_settings.py`: Rich feature configuration

**Evidence**: `tests/contract/test_rich_logger_api.py`, `tests/integration/test_rich_features.py`

---

### Filters Module (`filters/`)

**Purpose**: Log filtering

**Components**:
- `task_context_filter.py`: Task context filtering for parallel execution

**Evidence**: `tests/integration/test_rich_features.py::TestTaskContext`

---

## Data Flow

### Logger Creation Flow

```
User Code
    ↓
Log.create_logger()
    ↓
LoggerConfigurator.configure()
    ↓
├─→ FormatterFactory.create()  → Formatter
├─→ HandlerFactory.create()    → Handler(s)
└─→ stdlib logging.getLogger() → Logger
    ↓
RichLogger(logger, rich_settings)
    ↓
Return to User
```

**Evidence**: `tests/integration/test_logger_lifecycle.py::TestLoggerCreationAndLogging::test_create_logger_and_log_messages`

---

### Logging Message Flow

```
User Code: logger.info("message")
    ↓
RichLogger.__getattr__("info")
    ↓
Delegate to stdlib Logger.info()
    ↓
TaskContextFilter (if configured)
    ↓
Formatter (DEFAULT/COLORED/RICH)
    ↓
Handler (Console/File)
    ↓
Output (Console/File)
```

**Evidence**: `tests/contract/test_rich_logger_api.py::TestRichLoggerStandardLogging::test_info_delegates_to_stdlib_logger`

---

### Rich Display Flow

```
User Code: logger.table(data)
    ↓
RichLogger.table()
    ↓
Check RICH_AVAILABLE and enabled
    ↓
├─→ If available: RichConsoleManager.get_console()
│       ↓
│   Create Rich Table
│       ↓
│   console.print(table)
│
└─→ If unavailable: No-op (graceful degradation)
```

**Evidence**: `tests/integration/test_rich_features.py::TestRichDisplayFeatures::test_table_displays_data`

---

## Extension Points

### 1. Custom Formatters

Add new formatter types by:

1. Create formatter class inheriting from `logging.Formatter`
2. Add enum value to `LogFormatters`
3. Update `FormatterFactory.create()` to handle new type

**Example**:
```python
class CustomFormatter(logging.Formatter):
    def format(self, record):
        # Custom formatting logic
        return super().format(record)

# In FormatterFactory.create()
if formatter_type == LogFormatters.CUSTOM:
    return CustomFormatter(format_string, style=style.value)
```

---

### 2. Custom Handlers

Add new handler types by:

1. Create handler class inheriting from `logging.Handler`
2. Add enum value to `ConsoleHandlers` or create new enum
3. Update `HandlerFactory.create()` to handle new type

**Example**:
```python
class CustomHandler(logging.Handler):
    def emit(self, record):
        # Custom output logic
        pass

# In HandlerFactory
if handler_type == ConsoleHandlers.CUSTOM:
    return CustomHandler()
```

---

### 3. Custom Filters

Add custom log filters:

```python
class CustomFilter(logging.Filter):
    def filter(self, record):
        # Custom filtering logic
        return True

# Add to logger
logger._logger.addFilter(CustomFilter())
```

---

### 4. Custom Rich Display Methods

Add new Rich display methods to `RichLogger`:

```python
# In RichLogger class
def custom_display(self, data, **kwargs):
    """Display data in custom format."""
    console = self._get_console()
    if not console:
        return  # Graceful degradation

    # Create Rich renderable
    from rich.custom import CustomRenderable
    renderable = CustomRenderable(data, **kwargs)
    console.print(renderable)
```

---

## Thread Safety

### Task Context

Task context uses thread-local storage for thread safety:

```python
# In log_context.py
class LogContext:
    _context = threading.local()

    @classmethod
    def set_task_context(cls, step_id, task_name=None, **extra_context):
        cls._context.step_id = step_id
        cls._context.task_name = task_name
        cls._context.extra = extra_context
```

**Location**: `src/rich_logging/core/log_context.py`

**Benefits**:
- Each thread has independent context
- Safe for parallel execution
- No race conditions

**Evidence**: `tests/integration/test_rich_features.py::TestTaskContext::test_task_context_workflow`

---

### Console Manager

`RichConsoleManager` uses locks for thread-safe console access:

```python
class RichConsoleManager:
    def __init__(self):
        self._consoles: dict[str, Console] = {}
        self._lock = threading.Lock()

    def get_console(self, name: str) -> Console:
        with self._lock:
            # Thread-safe console retrieval/creation
            ...
```

**Location**: `src/rich_logging/rich/rich_console_manager.py`

---

## Configuration Hierarchy

Configuration follows a hierarchy with later values overriding earlier ones:

```
1. Default values (in code)
    ↓
2. LogConfig object (if provided)
    ↓
3. Individual parameters (override config)
```

**Example**:
```python
config = LogConfig(
    log_level=LogLevels.INFO,
    console_handler=ConsoleHandlers.DEFAULT
)

# Individual parameter overrides config
logger = Log.create_logger(
    config=config,
    log_level=LogLevels.DEBUG  # Overrides config.log_level
)
```

**Evidence**: `tests/contract/test_log_api.py::TestLogCreateLogger::test_create_logger_with_config_object`

---

## Error Handling

### Validation

Configuration is validated at multiple levels:

1. **Type checking**: Static type hints catch errors at development time
2. **Enum validation**: Invalid enum values rejected by Python
3. **Dataclass validation**: `RichFeatureSettings.__post_init__()` validates settings
4. **Runtime validation**: Utility functions validate log level strings

**Example**:
```python
# RichFeatureSettings validation
def __post_init__(self):
    if self.progress_refresh_per_second <= 0:
        raise ValueError("progress_refresh_per_second must be positive")

    if self.panel_box_style not in {"rounded", "square", "double", "heavy", "ascii"}:
        raise ValueError(f"Invalid panel_box_style: {self.panel_box_style}")
```

**Location**: `src/rich_logging/rich/rich_feature_settings.py`

---

### Graceful Degradation

Rich features gracefully degrade when unavailable:

```python
# In RichLogger
def _get_console(self) -> Console | None:
    if not RICH_AVAILABLE or not self._rich_settings.enabled:
        return None
    return console_manager.get_console(self._name)

def table(self, data, **kwargs):
    console = self._get_console()
    if not console:
        return  # Graceful no-op
    # ... create and display table
```

**Evidence**: `tests/contract/test_rich_logger_api.py::TestRichLoggerGracefulDegradation`

---

## Testing Strategy

The architecture supports comprehensive testing:

1. **Contract Tests**: Verify API contracts (inputs → outputs)
   - Evidence: `tests/contract/`

2. **Integration Tests**: Test end-to-end workflows
   - Evidence: `tests/integration/`

3. **Unit Tests**: Test isolated components (factories, formatters)
   - Evidence: `tests/unit/`

4. **Mocking Strategy**: Mock console output, file system, user input
   - Evidence: All test files use `unittest.mock`

---

## Performance Considerations

### Lazy Initialization

- Consoles created on-demand
- Formatters created once per logger
- Handlers reused when possible

### Resource Management

- Context managers ensure cleanup
- Thread-local storage prevents memory leaks
- Singleton console manager reduces resource usage

---

## Dependencies

### Required

- **Python 3.12+**: Modern Python features (type hints, dataclasses)
- **Rich >=13.0.0**: Rich console features

### Optional

- **ipywidgets**: Jupyter notebook support (Rich feature)

---

## See Also

- [API Reference](api-reference.md) - Complete API documentation
- [Usage Guide](usage-guide.md) - Getting started and common workflows
- [Configuration Reference](configuration.md) - All configuration options
- [Advanced Features](advanced-features.md) - Rich display methods and context managers

