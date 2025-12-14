# Architecture Overview

## Introduction

The logging module is designed with a clean, layered architecture that separates concerns and provides clear boundaries between different responsibilities. This document provides a comprehensive overview of the module's architecture, design decisions, and component relationships.

## Design Philosophy

### Core Principles

1. **Simplicity**: Provide a simple facade for common use cases while allowing advanced configuration
2. **Type Safety**: Use comprehensive type hints, enums, and dataclasses for compile-time safety
3. **Extensibility**: Use factory patterns to allow easy addition of new handlers and formatters
4. **Graceful Degradation**: Always provide fallbacks when optional dependencies are unavailable
5. **Separation of Concerns**: Clear boundaries between configuration, creation, and usage

### Architectural Goals

- **Single Responsibility**: Each module has one clear purpose
- **Dependency Inversion**: Depend on abstractions (base classes) not implementations
- **Open/Closed Principle**: Open for extension (via factories) but closed for modification
- **Interface Segregation**: Small, focused interfaces rather than large monolithic ones

## Layer Architecture

The module is organized into four distinct layers, each with specific responsibilities:

```
┌─────────────────────────────────────────────────────────────┐
│                        API Layer                            │
│  ┌──────────────┐  ┌────────────────────────────────────┐  │
│  │  log.py      │  │  __init__.py (Public Exports)      │  │
│  │  (Log Facade)│  │                                    │  │
│  └──────────────┘  └────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Integration Layer                        │
│  ┌──────────────────┐  ┌────────────────────────────────┐  │
│  │  rich_logger.py  │  │  rich_console_manager.py       │  │
│  │  (RichLogger)    │  │  rich_feature_settings.py      │  │
│  └──────────────────┘  └────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  Implementation Layer                       │
│  ┌──────────────────┐  ┌────────────────────────────────┐  │
│  │  handlers/       │  │  formatters/                   │  │
│  │  - console.py    │  │  - colored.py                  │  │
│  │  - file.py       │  │  - rich.py                     │  │
│  │  - base.py       │  │  - base.py                     │  │
│  └──────────────────┘  └────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                       Core Layer                            │
│  ┌──────────────────┐  ┌────────────────────────────────┐  │
│  │  log_types.py    │  │  configurator.py               │  │
│  │  (Types & Enums) │  │  (LoggerConfigurator)          │  │
│  │                  │  │                                │  │
│  │  utils.py        │  │                                │  │
│  │  (Utilities)     │  │                                │  │
│  └──────────────────┘  └────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Layer 1: Core Layer

**Purpose**: Provide foundational types, configuration, and utilities

**Components**:
- `log_types.py`: Type definitions, enums, and dataclasses
- `configurator.py`: Logger configuration and setup logic
- `utils.py`: Utility functions for formatting and validation

**Responsibilities**:
- Define all type-safe configuration structures
- Provide enumerations for choices (log levels, handler types, etc.)
- Implement logger configuration logic
- Provide utility functions used across the module

**Key Design Decisions**:
- Use dataclasses for configuration to get free validation and type checking
- Use enums instead of strings for type safety
- Keep utilities pure functions without side effects

### Layer 2: Implementation Layer

**Purpose**: Implement concrete handlers and formatters

**Components**:
- `handlers/`: Handler implementations (console, file, rotating, timed)
- `formatters/`: Formatter implementations (colored, rich, default)

**Responsibilities**:
- Implement concrete handler classes
- Implement concrete formatter classes
- Provide factory registration for extensibility
- Handle graceful degradation when dependencies unavailable

**Key Design Decisions**:
- Use factory pattern for handler/formatter creation
- Each handler/formatter has a config class that implements `create()`
- Factories use registries to map types to config classes
- Separate factories for console handlers and file handlers

### Layer 3: Integration Layer

**Purpose**: Integrate Rich library features with logging

**Components**:
- `rich_logger.py`: RichLogger wrapper class
- `rich_console_manager.py`: Singleton console manager
- `rich_feature_settings.py`: Rich feature configuration

**Responsibilities**:
- Wrap standard logger with Rich feature methods
- Manage shared console instances across loggers
- Provide type-safe configuration for Rich features
- Delegate standard logging methods to wrapped logger

**Key Design Decisions**:
- Use wrapper pattern to add Rich features without modifying standard logger
- Use singleton pattern for console manager to prevent output conflicts
- Use `__getattr__` to transparently delegate standard logging methods
- Provide 20+ Rich feature methods as first-class logger methods

### Layer 4: API Layer

**Purpose**: Provide simple, user-friendly API

**Components**:
- `log.py`: Log facade class
- `__init__.py`: Public API exports

**Responsibilities**:
- Provide simplified interface for common use cases
- Hide complexity of configuration and setup
- Export only public API elements
- Provide sensible defaults

**Key Design Decisions**:
- Use facade pattern to simplify complex subsystems
- Single `create_logger()` method handles most use cases
- Allow both simple (kwargs) and complex (config object) usage
- Export only necessary types and classes

## Component Relationships

### Dependency Flow

```
User Code
    ↓
Log (Facade)
    ↓
LoggerConfigurator
    ↓
┌─────────────┬──────────────┐
↓             ↓              ↓
HandlerFactory  FormatterFactory  RichLogger
    ↓             ↓              ↓
Handler Configs  Formatter Configs  RichConsoleManager
    ↓             ↓
Handlers        Formatters
```

### Key Relationships

1. **Log → LoggerConfigurator**: Facade delegates to configurator
2. **LoggerConfigurator → Factories**: Uses factories to create handlers/formatters
3. **Factories → Config Classes**: Maps types to config classes
4. **Config Classes → Implementations**: Creates concrete instances
5. **RichLogger → Logger**: Wraps standard logger
6. **RichLogger → RichConsoleManager**: Gets shared console instance

## Data Flow

### Logger Creation Flow

```
1. User calls Log.create_logger(name, config, **kwargs)
   ↓
2. Log creates LogConfig from kwargs or uses provided config
   ↓
3. Log calls LoggerConfigurator.configure(name, config)
   ↓
4. Configurator creates formatter via FormatterFactory
   ↓
5. Configurator creates handlers via HandlerFactory/FileHandlerFactory
   ↓
6. Configurator attaches handlers to logger
   ↓
7. Configurator wraps logger in RichLogger
   ↓
8. RichLogger returned to user
```

### Logging Flow

```
1. User calls logger.info("message") or logger.table(data)
   ↓
2. RichLogger checks if method is Rich feature or standard logging
   ↓
3a. Standard logging: Delegate to wrapped logger via __getattr__
    ↓
    Logger processes through handlers
    ↓
    Handlers format via formatters
    ↓
    Output to console/file

3b. Rich feature: Use RichConsoleManager to get console
    ↓
    Render Rich component
    ↓
    Output to console
```

## Extension Points

The module provides several extension points for customization:

### 1. Custom Handlers

```python
from rich_logging.handlers import BaseHandlerConfig, HandlerFactory
from rich_logging.core.log_types import ConsoleHandlers

class MyHandlerConfig(BaseHandlerConfig):
    def create(self) -> logging.Handler:
        handler = MyCustomHandler()
        handler.setFormatter(self.formatter)
        return handler

# Register with factory
HandlerFactory.register(ConsoleHandlers.CUSTOM, MyHandlerConfig)
```

### 2. Custom Formatters

```python
from rich_logging.formatters import BaseFormatterConfig, FormatterFactory
from rich_logging.core.log_types import LogFormatters

class MyFormatterConfig(BaseFormatterConfig):
    def create(self) -> logging.Formatter:
        return MyCustomFormatter(
            fmt=self.format_str,
            style=self.style.value
        )

# Register with factory
FormatterFactory.register(LogFormatters.CUSTOM, MyFormatterConfig)
```

### 3. Custom Rich Features

```python
# Extend RichLogger with custom methods
from rich_logging.rich import RichLogger

class CustomRichLogger(RichLogger):
    def my_custom_feature(self, data):
        console = self._get_console()
        # Custom Rich rendering logic
        console.print(...)
```

## Thread Safety

### Console Manager

The `RichConsoleManager` is thread-safe:
- Uses singleton pattern with double-checked locking
- All console operations protected by locks
- Safe for multi-threaded applications

### Logger Configuration

Logger configuration is thread-safe:
- Python's logging module is thread-safe
- Handler and formatter creation is atomic
- No shared mutable state during configuration

## Performance Considerations

### Lazy Initialization

- Formatters and handlers created only when needed
- Rich console created on first use
- No unnecessary object creation

### Caching

- Console manager caches console instances per logger
- Factories cache registered types
- No repeated lookups

### Graceful Degradation

- Rich features check availability once at import
- Fallback to standard logging has minimal overhead
- No runtime dependency checks in hot paths

## Error Handling

### Validation

- Configuration validated at creation time (dataclass `__post_init__`)
- Type errors caught early via type hints
- Invalid enum values rejected at assignment

### Fallbacks

- Rich unavailable → Standard logging
- RichHandler unavailable → StreamHandler
- RichFormatter unavailable → Standard Formatter

### Error Propagation

- Configuration errors raised immediately
- Runtime errors logged and re-raised
- No silent failures

## Testing Strategy

### Unit Tests

- Test each component in isolation
- Mock dependencies
- Test error conditions

### Integration Tests

- Test component interactions
- Test full logger creation flow
- Test Rich feature integration

### Interactive Tests

- Manual testing of Rich features
- Visual verification of output
- Performance testing

## Future Extensibility

The architecture supports future enhancements:

1. **Additional Handlers**: Network handlers, database handlers, etc.
2. **Additional Formatters**: JSON formatters, structured logging, etc.
3. **Additional Rich Features**: New Rich components as they're added
4. **Configuration Backends**: Load configuration from files, environment, etc.
5. **Async Support**: Async handlers and formatters
6. **Filtering**: Advanced log filtering and routing

## Summary

The logging module uses a clean, layered architecture that:

- Separates concerns across four distinct layers
- Uses design patterns (Facade, Factory, Singleton, Wrapper) appropriately
- Provides clear extension points for customization
- Maintains type safety throughout
- Handles errors gracefully with sensible fallbacks
- Supports both simple and advanced use cases

This architecture makes the module easy to understand, maintain, and extend while providing a powerful and flexible logging solution.
