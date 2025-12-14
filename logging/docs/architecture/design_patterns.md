# Design Patterns

## Overview

The logging module employs several well-established design patterns to achieve its goals of simplicity, extensibility, and maintainability. This document explains each pattern, why it was chosen, and how it's implemented.

## 1. Facade Pattern

### Purpose
Provide a simplified interface to a complex subsystem

### Implementation
The `Log` class serves as a facade over the complex logging configuration system.

### Code Example
```python
class Log:
    """Main logging API facade with simplified interface."""

    @staticmethod
    def create_logger(
        name: str | None = None,
        config: LogConfig | None = None,
        log_level: LogLevels | None = None,
        # ... many optional parameters
    ) -> RichLogger:
        """Create and configure a logger with a single call."""
        # Build config from kwargs if not provided
        if config is None:
            config = LogConfig(
                log_level=log_level or LogLevels.INFO,
                # ... build from kwargs
            )

        # Delegate to configurator
        return LoggerConfigurator.configure(name, config)
```

### Benefits
- **Simplicity**: Users don't need to understand LoggerConfigurator, factories, etc.
- **Flexibility**: Supports both simple (kwargs) and advanced (config object) usage
- **Encapsulation**: Hides complexity of configuration and setup

### Usage
```python
# Simple usage - facade hides complexity
logger = Log.create_logger(name="app", log_level=LogLevels.INFO)

# Advanced usage - still simple interface
logger = Log.create_logger(name="app", config=my_complex_config)
```

## 2. Factory Pattern

### Purpose
Create objects without specifying exact classes

### Implementation
Three factories: `HandlerFactory`, `FileHandlerFactory`, `FormatterFactory`

### Code Example
```python
class HandlerFactory:
    """Factory for creating console handlers."""

    # Registry mapping handler types to config classes
    _registry: dict[ConsoleHandlers, type[BaseHandlerConfig]] = {}

    @classmethod
    def register(
        cls,
        handler_type: ConsoleHandlers,
        config_class: type[BaseHandlerConfig]
    ):
        """Register a handler config class."""
        cls._registry[handler_type] = config_class

    @classmethod
    def create(
        cls,
        handler_type: ConsoleHandlers,
        formatter: logging.Formatter
    ) -> logging.Handler:
        """Create a handler instance."""
        if handler_type not in cls._registry:
            raise ValueError(f"Unknown handler type: {handler_type}")

        config_class = cls._registry[handler_type]
        handler_config = config_class(formatter)
        return handler_config.create()

# Registration
HandlerFactory.register(ConsoleHandlers.DEFAULT, StreamHandlerConfig)
HandlerFactory.register(ConsoleHandlers.RICH, RichHandlerConfig)
```

### Benefits
- **Extensibility**: New handlers can be added without modifying factory
- **Decoupling**: Client code doesn't depend on concrete handler classes
- **Type Safety**: Enum-based type selection prevents typos

### Usage
```python
# Factory creates appropriate handler based on type
handler = HandlerFactory.create(
    handler_type=ConsoleHandlers.RICH,
    formatter=my_formatter
)
```

### Extension Example
```python
# Add custom handler
class MyHandlerConfig(BaseHandlerConfig):
    def create(self) -> logging.Handler:
        return MyCustomHandler()

# Register with factory
HandlerFactory.register(ConsoleHandlers.CUSTOM, MyHandlerConfig)

# Now usable via factory
handler = HandlerFactory.create(ConsoleHandlers.CUSTOM, formatter)
```

## 3. Registry Pattern

### Purpose
Maintain a registry of available implementations

### Implementation
Factories use registries to map types to config classes

### Code Example
```python
class FormatterFactory:
    """Factory for creating formatters."""

    # Registry is a class variable
    _registry: dict[LogFormatters, type[BaseFormatterConfig]] = {}

    @classmethod
    def register(
        cls,
        formatter_type: LogFormatters,
        config_class: type[BaseFormatterConfig]
    ):
        """Register a formatter config class."""
        cls._registry[formatter_type] = config_class

# Formatters register themselves at module load time
FormatterFactory.register(LogFormatters.DEFAULT, DefaultFormatterConfig)
FormatterFactory.register(LogFormatters.COLORED, ColoredFormatterConfig)
FormatterFactory.register(LogFormatters.RICH, RichFormatterConfig)
```

### Benefits
- **Discoverability**: All available types in one place
- **Validation**: Can check if type is registered before use
- **Runtime Extension**: Can add new types at runtime

### Usage
```python
# Check if type is registered
if formatter_type in FormatterFactory._registry:
    formatter = FormatterFactory.create(formatter_type, ...)
```

## 4. Singleton Pattern

### Purpose
Ensure only one instance of a class exists

### Implementation
`RichConsoleManager` uses thread-safe singleton

### Code Example
```python
class RichConsoleManager:
    """Manages shared Rich console instances."""

    _instance: Optional["RichConsoleManager"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "RichConsoleManager":
        """Singleton pattern with double-checked locking."""
        if cls._instance is None:
            with cls._lock:
                # Double-check inside lock
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize only once."""
        if not hasattr(self, "_initialized"):
            self._consoles: dict[str, Console] = {}
            self._console_lock = threading.Lock()
            self._initialized = True

# Global singleton instance
console_manager = RichConsoleManager()
```

### Benefits
- **Shared State**: All loggers share same console manager
- **Coordination**: Prevents output conflicts between loggers
- **Thread Safety**: Double-checked locking prevents race conditions

### Usage
```python
# All code uses same instance
from rich_logging.rich import console_manager

console = console_manager.get_console("my_logger")
```

## 5. Wrapper Pattern (Decorator)

### Purpose
Add functionality to an object without modifying it

### Implementation
`RichLogger` wraps standard `logging.Logger`

### Code Example
```python
class RichLogger:
    """Enhanced logger wrapper that adds Rich features."""

    def __init__(
        self,
        logger: logging.Logger,
        rich_settings: RichFeatureSettings | None = None
    ):
        """Wrap a standard logger."""
        self._logger = logger
        self._rich_settings = rich_settings or RichFeatureSettings()

    def __getattr__(self, name: str) -> Any:
        """Delegate all standard logging methods to wrapped logger."""
        return getattr(self._logger, name)

    # Add Rich feature methods
    def table(self, data, **kwargs):
        """Display a table using Rich."""
        console = self._get_console()
        # ... Rich table rendering

    def panel(self, message, **kwargs):
        """Display a panel using Rich."""
        console = self._get_console()
        # ... Rich panel rendering
```

### Benefits
- **Non-Invasive**: Doesn't modify standard logger
- **Transparent**: Standard logging methods work unchanged
- **Additive**: Only adds new functionality

### Usage
```python
# Standard logging methods work as expected
logger.info("Standard logging")
logger.debug("Debug message")

# Rich features available as well
logger.table(data)
logger.panel("Message")
```

## 6. Template Method Pattern

### Purpose
Define skeleton of algorithm, let subclasses override steps

### Implementation
`BaseHandlerConfig` and `BaseFormatterConfig` use template method

### Code Example
```python
class BaseHandlerConfig(ABC):
    """Abstract base for handler configurations."""

    def __init__(self, formatter: logging.Formatter):
        """Common initialization."""
        self.formatter = formatter

    @abstractmethod
    def create(self) -> logging.Handler:
        """Template method - subclasses must implement."""
        pass

class StreamHandlerConfig(BaseHandlerConfig):
    """Concrete implementation."""

    def create(self) -> logging.StreamHandler:
        """Implement template method."""
        handler = logging.StreamHandler()
        handler.setFormatter(self.formatter)  # Use common formatter
        return handler

class RichHandlerConfig(BaseHandlerConfig):
    """Another concrete implementation."""

    def create(self) -> logging.Handler:
        """Implement template method with different logic."""
        if RICH_AVAILABLE:
            handler = RichHandler(**self.settings.to_dict())
            # Rich does its own formatting
            handler.setFormatter(logging.Formatter("%(message)s"))
        else:
            # Fallback
            handler = logging.StreamHandler()
            handler.setFormatter(self.formatter)
        return handler
```

### Benefits
- **Code Reuse**: Common initialization in base class
- **Flexibility**: Each subclass can customize creation
- **Consistency**: All configs follow same pattern

## 7. Strategy Pattern

### Purpose
Define family of algorithms, make them interchangeable

### Implementation
Formatters and handlers are interchangeable strategies

### Code Example
```python
# Different formatting strategies
class ColoredFormatter(logging.Formatter):
    """Strategy: ANSI color formatting."""
    def format(self, record):
        # ANSI color strategy
        pass

class RichFormatter(logging.Formatter):
    """Strategy: Rich markup formatting."""
    def format(self, record):
        # Rich markup strategy
        pass

# Client code selects strategy
config = LogConfig(
    formatter_type=LogFormatters.COLORED  # Select strategy
)
```

### Benefits
- **Interchangeability**: Can swap formatters without changing code
- **Encapsulation**: Each strategy encapsulates its algorithm
- **Runtime Selection**: Strategy chosen at runtime via configuration

## 8. Builder Pattern (Implicit)

### Purpose
Construct complex objects step by step

### Implementation
`LogConfig` dataclass acts as builder

### Code Example
```python
# Build configuration step by step
config = LogConfig(
    log_level=LogLevels.INFO,
    formatter_type=LogFormatters.COLORED,
    console_handler_type=ConsoleHandlers.RICH,
    rich_handler_settings=RichHandlerSettings(
        show_time=True,
        show_level=True,
        markup=True
    ),
    file_handler_type=FileHandlerTypes.ROTATING_FILE,
    file_handler_settings=RotatingFileHandlerSettings(
        filename="app.log",
        max_bytes=10_485_760,
        backup_count=5
    )
)

# Use built configuration
logger = Log.create_logger(name="app", config=config)
```

### Benefits
- **Clarity**: Each setting is explicit
- **Validation**: Dataclass validates at construction
- **Immutability**: Configuration is immutable after creation

## 9. Dependency Injection

### Purpose
Provide dependencies from outside rather than creating them

### Implementation
Handlers and formatters receive dependencies via constructor

### Code Example
```python
class RichHandlerConfig(BaseHandlerConfig):
    def __init__(
        self,
        formatter: logging.Formatter,  # Injected dependency
        settings: RichHandlerSettings | None = None,  # Injected dependency
        logger_name: str = None  # Injected dependency
    ):
        super().__init__(formatter)
        self.settings = settings or RichHandlerSettings()
        self.logger_name = logger_name
```

### Benefits
- **Testability**: Easy to inject mocks for testing
- **Flexibility**: Can provide different implementations
- **Decoupling**: Classes don't create their dependencies

## 10. Graceful Degradation Pattern

### Purpose
Provide fallback when optional features unavailable

### Implementation
Rich features check availability and fallback

### Code Example
```python
try:
    from rich.logging import RichHandler
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

class RichHandlerConfig(BaseHandlerConfig):
    def create(self) -> logging.Handler:
        """Create RichHandler or fallback to StreamHandler."""
        if RICH_AVAILABLE:
            handler = RichHandler(**self.settings.to_dict())
        else:
            # Graceful fallback
            handler = logging.StreamHandler()

        handler.setFormatter(self.formatter)
        return handler
```

### Benefits
- **Robustness**: Works even without optional dependencies
- **User Experience**: No crashes, just reduced functionality
- **Deployment Flexibility**: Can deploy without Rich if needed

## Pattern Interactions

### How Patterns Work Together

```
User Code
    ↓
[Facade] Log.create_logger()
    ↓
[Builder] LogConfig construction
    ↓
[Template Method] LoggerConfigurator.configure()
    ↓
    ├─→ [Factory + Registry] FormatterFactory.create()
    │       ↓
    │   [Strategy] Formatter implementation
    │
    ├─→ [Factory + Registry] HandlerFactory.create()
    │       ↓
    │   [Template Method] HandlerConfig.create()
    │       ↓
    │   [Graceful Degradation] Check availability
    │       ↓
    │   [Dependency Injection] Inject formatter
    │
    └─→ [Wrapper] RichLogger(logger)
            ↓
        [Singleton] RichConsoleManager
```

## Summary

The logging module uses 10 design patterns:

1. **Facade**: Simplify complex subsystem (Log class)
2. **Factory**: Create objects without specifying classes (3 factories)
3. **Registry**: Maintain available implementations (in factories)
4. **Singleton**: Single console manager instance
5. **Wrapper**: Add Rich features to logger
6. **Template Method**: Handler/formatter creation skeleton
7. **Strategy**: Interchangeable formatters/handlers
8. **Builder**: Step-by-step configuration construction
9. **Dependency Injection**: Provide dependencies externally
10. **Graceful Degradation**: Fallback when Rich unavailable

These patterns work together to create a system that is:
- **Simple** to use (Facade)
- **Extensible** (Factory, Registry, Template Method)
- **Flexible** (Strategy, Dependency Injection)
- **Robust** (Graceful Degradation, Singleton)
- **Maintainable** (All patterns promote clean code)
