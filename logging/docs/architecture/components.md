# Component Breakdown

## Overview

This document provides a detailed breakdown of all components in the logging module, their responsibilities, interfaces, and relationships.

## Core Components

### 1. Log Types (`core/log_types.py`)

**Purpose**: Define all type-safe configuration structures and enumerations

**Key Classes**:

#### LogLevels (Enum)
```python
class LogLevels(Enum):
    DEBUG = logging.DEBUG      # 10
    INFO = logging.INFO        # 20
    WARNING = logging.WARNING  # 30
    ERROR = logging.ERROR      # 40
    CRITICAL = logging.CRITICAL # 50
```

**Purpose**: Type-safe log level selection
**Usage**: `log_level=LogLevels.INFO`

#### LogFormatterStyleChoices (Enum)
```python
class LogFormatterStyleChoices(Enum):
    PERCENT = "%"    # %(levelname)s
    BRACE = "{"      # {levelname}
    DOLLAR = "$"     # $levelname
```

**Purpose**: Format string style selection
**Usage**: `formatter_style=LogFormatterStyleChoices.BRACE`

#### LogFormatters (Enum)
```python
class LogFormatters(Enum):
    DEFAULT = "default"  # Standard logging.Formatter
    COLORED = "colored"  # ANSI colored formatter
    RICH = "rich"        # Rich markup formatter
```

**Purpose**: Formatter type selection
**Usage**: `formatter_type=LogFormatters.COLORED`

#### ConsoleHandlers (Enum)
```python
class ConsoleHandlers(Enum):
    DEFAULT = "default"  # StreamHandler
    RICH = "rich"        # RichHandler
```

**Purpose**: Console handler type selection
**Usage**: `console_handler_type=ConsoleHandlers.RICH`

#### FileHandlerTypes (Enum)
```python
class FileHandlerTypes(Enum):
    FILE = "file"                          # Basic FileHandler
    ROTATING_FILE = "rotating_file"        # RotatingFileHandler
    TIMED_ROTATING_FILE = "timed_rotating" # TimedRotatingFileHandler
```

**Purpose**: File handler type selection
**Usage**: `file_handler_type=FileHandlerTypes.ROTATING_FILE`

#### ColoredFormatterColors (Class)
```python
class ColoredFormatterColors:
    """ANSI color codes for log levels."""
    DEBUG = "\033[36m"      # Cyan
    INFO = "\033[32m"       # Green
    WARNING = "\033[33m"    # Yellow
    ERROR = "\033[31m"      # Red
    CRITICAL = "\033[35m"   # Magenta
    RESET = "\033[0m"       # Reset
```

**Purpose**: ANSI color code definitions
**Usage**: Internal to ColoredFormatter

#### LogConfig (Dataclass)
```python
@dataclass
class LogConfig:
    log_level: LogLevels
    formatter_style: LogFormatterStyleChoices | None = None
    format: str | None = None
    formatter_type: LogFormatters | None = None
    console_handler_type: ConsoleHandlers | None = None
    file_handler_type: FileHandlerTypes | None = None
    file_handler_settings: BaseFileHandlerSettings | None = None
    rich_handler_settings: RichHandlerSettings | None = None
    rich_feature_settings: RichFeatureSettings | None = None
    colors: type[ColoredFormatterColors] | None = None
```

**Purpose**: Main configuration dataclass
**Validation**: Type checking via dataclass
**Usage**: Pass to `Log.create_logger(config=...)`

### 2. Logger Configurator (`core/configurator.py`)

**Purpose**: Manage logger configuration and setup

**Key Class**: `LoggerConfigurator`

**Responsibilities**:
- Create formatters via FormatterFactory
- Create handlers via HandlerFactory/FileHandlerFactory
- Attach handlers to loggers
- Wrap loggers in RichLogger
- Update existing logger configurations

**Key Methods**:

```python
@staticmethod
def configure(
    name: str,
    config: LogConfig,
    logger: logging.Logger | None = None
) -> RichLogger:
    """Configure a logger with the given configuration."""
```

**Process**:
1. Get or create logger by name
2. Set log level
3. Create formatter
4. Create and attach console handler (if configured)
5. Create and attach file handler (if configured)
6. Wrap in RichLogger
7. Return RichLogger instance

### 3. Utilities (`core/utils.py`)

**Purpose**: Provide utility functions for formatting and validation

**Key Functions**:

```python
def get_default_format(style: LogFormatterStyleChoices) -> str:
    """Get default format string for given style."""

def validate_format_string(format_str: str, style: LogFormatterStyleChoices) -> bool:
    """Validate format string matches style."""

def format_exception(exc: Exception) -> str:
    """Format exception with traceback."""
```

**Usage**: Internal utilities used by configurator and formatters

## Handler Components

### 1. Base Handler (`handlers/base.py`)

**Purpose**: Define handler abstraction and factory

**Key Classes**:

#### BaseHandlerConfig (ABC)
```python
class BaseHandlerConfig(ABC):
    def __init__(self, formatter: logging.Formatter):
        self.formatter = formatter

    @abstractmethod
    def create(self) -> logging.Handler:
        """Create a handler instance."""
```

**Purpose**: Abstract base for handler configurations
**Pattern**: Template Method pattern

#### HandlerFactory
```python
class HandlerFactory:
    _registry: dict[ConsoleHandlers, type[BaseHandlerConfig]] = {}

    @classmethod
    def register(cls, handler_type, config_class):
        """Register a handler config class."""

    @classmethod
    def create(cls, handler_type, formatter) -> logging.Handler:
        """Create a handler instance."""
```

**Purpose**: Factory for creating console handlers
**Pattern**: Factory + Registry pattern

### 2. Console Handlers (`handlers/console.py`)

**Key Classes**:

#### StreamHandlerConfig
```python
class StreamHandlerConfig(BaseHandlerConfig):
    def create(self) -> logging.StreamHandler:
        """Create a StreamHandler instance."""
```

**Purpose**: Standard console output
**Registered As**: `ConsoleHandlers.DEFAULT`

#### RichHandlerConfig
```python
class RichHandlerConfig(BaseHandlerConfig):
    def __init__(
        self,
        formatter: logging.Formatter,
        settings: RichHandlerSettings | None = None,
        logger_name: str = None
    ):
        """Initialize Rich handler configuration."""

    def create(self) -> logging.Handler:
        """Create RichHandler or fallback to StreamHandler."""
```

**Purpose**: Rich-enhanced console output
**Registered As**: `ConsoleHandlers.RICH`
**Fallback**: StreamHandler if Rich unavailable

### 3. File Handlers (`handlers/file.py`)

**Key Classes**:

#### FileHandlerConfig
```python
class FileHandlerConfig(BaseHandlerConfig):
    def __init__(self, formatter, settings: FileHandlerSettings):
        """Initialize file handler configuration."""

    def create(self) -> logging.FileHandler:
        """Create a FileHandler instance."""
```

**Purpose**: Basic file logging
**Registered As**: `FileHandlerTypes.FILE`

#### RotatingFileHandlerConfig
```python
class RotatingFileHandlerConfig(BaseHandlerConfig):
    def __init__(self, formatter, settings: RotatingFileHandlerSettings):
        """Initialize rotating file handler configuration."""

    def create(self) -> RotatingFileHandler:
        """Create a RotatingFileHandler instance."""
```

**Purpose**: File logging with size-based rotation
**Registered As**: `FileHandlerTypes.ROTATING_FILE`

#### TimedRotatingFileHandlerConfig
```python
class TimedRotatingFileHandlerConfig(BaseHandlerConfig):
    def __init__(self, formatter, settings: TimedRotatingFileHandlerSettings):
        """Initialize timed rotating file handler configuration."""

    def create(self) -> TimedRotatingFileHandler:
        """Create a TimedRotatingFileHandler instance."""
```

**Purpose**: File logging with time-based rotation
**Registered As**: `FileHandlerTypes.TIMED_ROTATING_FILE`

#### FileHandlerFactory
```python
class FileHandlerFactory:
    _registry: dict[FileHandlerTypes, type[BaseHandlerConfig]] = {}

    @classmethod
    def create(cls, handler_type, formatter, config) -> logging.Handler:
        """Create a file handler instance."""
```

**Purpose**: Factory for creating file handlers
**Pattern**: Factory + Registry pattern

### 4. Handler Settings (`handlers/file_settings.py`, `handlers/rich_settings.py`)

**File Handler Settings**:

```python
@dataclass
class BaseFileHandlerSettings:
    """Base settings for file handlers."""
    filename: str
    mode: str = "a"
    encoding: str = "utf-8"
    delay: bool = False

@dataclass
class FileHandlerSettings(BaseFileHandlerSettings):
    """Settings for basic file handler."""

@dataclass
class RotatingFileHandlerSettings(BaseFileHandlerSettings):
    """Settings for rotating file handler."""
    max_bytes: int = 10_485_760  # 10 MB
    backup_count: int = 5

@dataclass
class TimedRotatingFileHandlerSettings(BaseFileHandlerSettings):
    """Settings for timed rotating file handler."""
    when: str = "midnight"
    interval: int = 1
    backup_count: int = 7
    utc: bool = False
```

**Rich Handler Settings**:

```python
@dataclass
class RichHandlerSettings:
    """Settings for Rich handler."""
    show_time: bool = True
    show_level: bool = True
    show_path: bool = True
    enable_link_path: bool = True
    markup: bool = False
    rich_tracebacks: bool = True
    tracebacks_show_locals: bool = False
    # ... more settings

    def to_dict(self) -> dict:
        """Convert settings to dict for RichHandler."""
```

## Formatter Components

### 1. Base Formatter (`formatters/base.py`)

**Key Classes**:

#### BaseFormatterConfig (ABC)
```python
class BaseFormatterConfig(ABC):
    def __init__(self, format_str: str, style: LogFormatterStyleChoices):
        self.format_str = format_str
        self.style = style

    @abstractmethod
    def create(self) -> logging.Formatter:
        """Create a formatter instance."""
```

**Purpose**: Abstract base for formatter configurations

#### FormatterFactory
```python
class FormatterFactory:
    _registry: dict[LogFormatters, type[BaseFormatterConfig]] = {}

    @classmethod
    def create(cls, formatter_type, format_str, style, **kwargs) -> logging.Formatter:
        """Create a formatter instance."""
```

**Purpose**: Factory for creating formatters

### 2. Colored Formatter (`formatters/colored.py`)

**Key Classes**:

#### ColoredFormatter
```python
class ColoredFormatter(logging.Formatter):
    """Formatter that adds ANSI colors based on log level."""

    def format(self, record):
        """Format the log record with colors."""
```

**Purpose**: Add ANSI colors to log output
**Registered As**: `LogFormatters.COLORED`

### 3. Rich Formatter (`formatters/rich.py`)

**Key Classes**:

#### RichFormatter
```python
class RichFormatter(logging.Formatter):
    """Formatter that outputs Rich markup for use with regular handlers."""

    def format(self, record):
        """Format the log record with Rich markup, then render to plain text."""
```

**Purpose**: Add Rich markup to log output
**Registered As**: `LogFormatters.RICH`
**Fallback**: Standard Formatter if Rich unavailable

## Rich Integration Components

### 1. RichLogger (`rich/rich_logger.py`)

**Purpose**: Wrap standard logger with Rich features

**Key Class**: `RichLogger`

**Responsibilities**:
- Delegate standard logging methods to wrapped logger
- Provide 20+ Rich feature methods
- Manage console access via RichConsoleManager
- Handle graceful degradation

**Rich Feature Methods** (20+):
- `table()` - Display tables
- `panel()` - Display panels
- `rule()` - Display horizontal rules
- `progress()` - Progress bars
- `status()` - Status spinners
- `tree()` - Tree structures
- `columns()` - Column layouts
- `syntax()` - Syntax highlighting
- `markdown()` - Markdown rendering
- `json()` - JSON display
- `live()` - Live displays
- `bar_chart()` - Bar charts
- `text()` - Styled text
- `align()` - Text alignment
- `prompt()` - User prompts
- `confirm()` - Confirmation prompts
- `inspect()` - Object inspection
- `pretty()` - Pretty printing
- And more...

### 2. RichConsoleManager (`rich/rich_console_manager.py`)

**Purpose**: Manage shared Rich console instances

**Key Class**: `RichConsoleManager`

**Pattern**: Singleton with thread-safe initialization

**Key Methods**:
```python
def register_console(self, logger_name: str, console: Console):
    """Register a console for a specific logger."""

def get_console(self, logger_name: str) -> Console | None:
    """Get the console for a specific logger."""

def remove_console(self, logger_name: str):
    """Remove console registration for a logger."""

def has_console(self, logger_name: str) -> bool:
    """Check if a console is registered for a logger."""

def clear_all(self):
    """Clear all registered consoles."""
```

**Thread Safety**: All methods protected by locks

### 3. RichFeatureSettings (`rich/rich_feature_settings.py`)

**Purpose**: Type-safe configuration for Rich features

**Key Class**: `RichFeatureSettings` (Dataclass with 50+ settings)

**Setting Categories**:
- Global features control
- Table settings
- Panel settings
- Rule settings
- Progress settings
- Status settings
- Console settings
- Tree settings
- Columns settings
- Syntax highlighting settings
- Markdown settings
- JSON settings
- Live display settings
- Bar chart settings
- Text and alignment settings
- Prompt settings
- Inspection settings
- Pretty printing settings

**Validation**: Comprehensive validation in `__post_init__`

## API Components

### 1. Log Facade (`log.py`)

**Purpose**: Provide simplified API for logger creation

**Key Class**: `Log`

**Key Methods**:

```python
@staticmethod
def create_logger(
    name: str | None = None,
    config: LogConfig | None = None,
    log_level: LogLevels | None = None,
    # ... many optional parameters
) -> RichLogger:
    """Create and configure a logger."""

@staticmethod
def update(
    logger: RichLogger,
    config: LogConfig | None = None,
    **kwargs
) -> RichLogger:
    """Update an existing logger's configuration."""
```

**Usage Patterns**:
1. Simple: `Log.create_logger(name="app", log_level=LogLevels.INFO)`
2. With kwargs: `Log.create_logger(name="app", log_level=LogLevels.INFO, formatter_type=LogFormatters.COLORED)`
3. With config: `Log.create_logger(name="app", config=my_config)`

### 2. Public Exports (`__init__.py`)

**Exported Types**:
- `Log` - Main facade
- `RichLogger` - Enhanced logger
- `LoggerConfigurator` - Configuration manager
- `LogConfig` - Configuration dataclass
- `LogLevels` - Log level enum
- `LogFormatters` - Formatter type enum
- `ConsoleHandlers` - Console handler enum
- `FileHandlerTypes` - File handler enum
- `LogFormatterStyleChoices` - Format style enum
- `ColoredFormatterColors` - Color definitions

**Exported from Submodules**:
- Handler settings classes
- Rich settings classes
- Formatter classes

## Component Interaction Diagram

```
User Code
    ↓
Log.create_logger()
    ↓
LoggerConfigurator.configure()
    ↓
    ├─→ FormatterFactory.create() → Formatter
    ├─→ HandlerFactory.create() → Console Handler
    ├─→ FileHandlerFactory.create() → File Handler
    └─→ RichLogger(logger, settings)
            ↓
            ├─→ Standard logging methods → Wrapped Logger
            └─→ Rich feature methods → RichConsoleManager → Console
```

## Summary

The logging module consists of:

- **4 layers**: Core, Implementation, Integration, API
- **3 factories**: HandlerFactory, FileHandlerFactory, FormatterFactory
- **6 handler types**: Stream, Rich, File, RotatingFile, TimedRotatingFile
- **3 formatter types**: Default, Colored, Rich
- **20+ Rich features**: Tables, panels, progress, syntax, etc.
- **50+ configuration settings**: Type-safe dataclasses
- **1 singleton**: RichConsoleManager for console coordination

All components work together to provide a powerful, flexible, and easy-to-use logging solution.
