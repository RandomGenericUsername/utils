# Investigation Notes - Logging Module

**Module:** `src/common/modules/logging`
**Investigation Started:** 2025-10-29
**Last Updated:** 2025-10-29

---

## Table of Contents

1. [Architecture & Structure](#architecture--structure)
2. [Core Abstractions](#core-abstractions)
3. [Type System & Data Models](#type-system--data-models)
4. [Exception Hierarchy](#exception-hierarchy)
5. [Implementation Details](#implementation-details)
6. [Key Features & Capabilities](#key-features--capabilities)
7. [Integration & Usage Patterns](#integration--usage-patterns)
8. [Advanced Topics](#advanced-topics)
9. [Code Examples](#code-examples)
10. [Architecture Diagrams](#architecture-diagrams)

---

## Architecture & Structure

### Directory Structure

**Task 1.1 - COMPLETE**

```
src/common/modules/logging/
├── README.md                    # Module overview and quick start
├── pyproject.toml              # Project configuration (uv project)
├── uv.lock                     # Dependency lock file
├── docs/                       # Documentation directory
│   └── helpers/                # Investigation helper documents
│       ├── README.md
│       ├── INTERACTIVE_PROMPT.md
│       ├── REQUIREMENTS_CHECKLIST.md
│       ├── INVESTIGATION_NOTES.md
│       └── SESSION_SUMMARY.md
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── run_tests.py           # Test runner
│   ├── integration_test.py    # Integration tests
│   ├── interactive_demo.py    # Interactive demonstration
│   ├── test_rich_features.py  # Rich features tests
│   └── test_rich_interactive.py # Rich interactive tests
└── src/logging/      # Main source code
    ├── __init__.py            # Public API exports
    ├── log.py                 # Main Log facade class
    ├── presets.py             # Preset logger configurations
    ├── core/                  # Core functionality
    │   ├── __init__.py
    │   ├── configurator.py    # LoggerConfigurator class
    │   ├── log_types.py       # Type definitions (enums, dataclasses)
    │   └── utils.py           # Utility functions
    ├── handlers/              # Handler implementations
    │   ├── __init__.py
    │   ├── base.py            # Base handler classes
    │   ├── console.py         # Console handler
    │   ├── file.py            # File handlers
    │   ├── file_settings.py   # File handler settings
    │   └── rich_settings.py   # Rich handler settings
    ├── formatters/            # Formatter implementations
    │   ├── __init__.py
    │   ├── base.py            # Base formatter
    │   ├── colored.py         # Colored formatter
    │   └── rich.py            # Rich formatter
    └── rich/                  # Rich library integration
        ├── __init__.py
        ├── rich_console_manager.py  # Console management
        ├── rich_feature_settings.py # Rich feature configuration
        └── rich_logger.py           # RichLogger wrapper class
```

**Directory Purposes:**

- **`core/`**: Core logging abstractions, types, and configuration logic
- **`handlers/`**: Handler implementations (console, file, rich)
- **`formatters/`**: Formatter implementations (default, colored, rich)
- **`rich/`**: Rich library integration and enhanced logging features
- **`tests/`**: Comprehensive test suite with integration and interactive tests
- **`docs/`**: Documentation (currently contains investigation helpers)

### File Organization

**Task 1.2 - COMPLETE**

**Main API Files:**
- `__init__.py` (76 lines): Public API exports - main entry point for users
- `log.py` (292 lines): `Log` facade class with `create_logger()` and `update()` methods
- `presets.py` (8 lines): Preset logger configurations (currently minimal)

**Core Module Files:**
- `core/__init__.py` (45 lines): Core module exports
- `core/log_types.py` (117 lines): Type definitions - enums, dataclasses, type aliases
- `core/configurator.py` (165 lines): `LoggerConfigurator` - manages logger setup
- `core/utils.py` (137 lines): Utility functions for log level parsing and validation

**Handler Files:**
- `handlers/__init__.py`: Handler exports
- `handlers/base.py`: Base handler classes
- `handlers/console.py`: Console handler implementation
- `handlers/file.py`: File handler implementations (file, rotating, timed rotating)
- `handlers/file_settings.py`: File handler configuration dataclasses
- `handlers/rich_settings.py`: Rich handler configuration

**Formatter Files:**
- `formatters/__init__.py`: Formatter exports
- `formatters/base.py`: Base formatter
- `formatters/colored.py`: Colored console formatter
- `formatters/rich.py`: Rich formatter

**Rich Integration Files:**
- `rich/__init__.py`: Rich module exports
- `rich/rich_console_manager.py`: Manages Rich console instances
- `rich/rich_feature_settings.py`: Configuration for Rich features
- `rich/rich_logger.py`: RichLogger wrapper with enhanced methods

**Configuration Files:**
- `pyproject.toml` (112 lines): Project metadata, dependencies, tool configuration
- `uv.lock`: Dependency lock file (managed by uv)

**Documentation Files:**
- `README.md` (73 lines): Module overview, features, usage examples

### Module Organization

**Task 1.3 - COMPLETE**

**Package Structure:**
The module is organized as a standalone uv project named `logging` with clean separation of concerns:

1. **Core Layer** (`core/`):
   - Type definitions and enums
   - Configuration management (`LoggerConfigurator`)
   - Utility functions
   - No dependencies on handlers/formatters/rich

2. **Implementation Layer** (`handlers/`, `formatters/`):
   - Concrete implementations of handlers and formatters
   - Factory patterns for creation
   - Settings/configuration dataclasses
   - Depends on core types

3. **Integration Layer** (`rich/`):
   - Rich library integration
   - Enhanced logger wrapper (`RichLogger`)
   - Console management for shared consoles
   - Feature settings for Rich-specific capabilities

4. **API Layer** (`log.py`, `__init__.py`):
   - Simplified facade (`Log` class)
   - Public API exports
   - Orchestrates all layers
   - User-facing interface

**Dependencies:**
- **External**: `rich>=13.0.0` (only dependency)
- **Dev**: pytest, mypy, black, ruff, isort
- **Python**: >=3.12

**Design Patterns:**
- **Facade Pattern**: `Log` class provides simplified interface
- **Factory Pattern**: `FormatterFactory`, `HandlerFactory`, `FileHandlerFactory`
- **Configurator Pattern**: `LoggerConfigurator` manages logger setup
- **Wrapper Pattern**: `RichLogger` wraps standard logger with enhanced methods

### Public API Surface

**Task 1.4 - IN PROGRESS**

**Main API Class:**
- `Log` - Main facade class
  - `create_logger()` - Create and configure a logger
  - `update()` - Update existing logger configuration

**Type Enums:**
- `LogLevels` - Log level enumeration (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `LogFormatters` - Formatter types (DEFAULT, COLORED, RICH)
- `LogFormatterStyleChoices` - Format styles (PERCENT, BRACE, DOLLAR)
- `ConsoleHandlers` - Console handler types (DEFAULT, RICH)
- `FileHandlerTypes` - File handler types (FILE, ROTATING_FILE, TIMED_ROTATING_FILE)

**Configuration Classes:**
- `LogConfig` - Main configuration dataclass
- `FileHandlerSpec` - File handler specification
- `ColoredFormatterColors` - Color scheme for colored formatter
- `RichHandlerSettings` - Rich handler configuration
- `RichFeatureSettings` - Rich feature configuration
- `FileHandlerSettings` - File handler settings
- `RotatingFileHandlerSettings` - Rotating file handler settings
- `TimedRotatingFileHandlerSettings` - Timed rotating file handler settings

**Utility Functions:**
- `get_log_level_from_verbosity()` - Convert verbosity count to log level
- `parse_log_level()` - Parse log level from string or verbosity
- `validate_log_level_string()` - Validate log level string

**Advanced Classes (for extension):**
- `LoggerConfigurator` - Logger configuration manager
- `FormatterFactory` - Formatter creation
- `HandlerFactory` - Handler creation
- `ColoredFormatter` - Colored formatter implementation
- `RichFormatter` - Rich formatter implementation
- `RichLogger` - Enhanced logger with Rich features

**Constants:**
- `FORMATTER_PLACEHOLDERS` - List of valid LogRecord attributes for format strings

### Entry Points

**Task 1.5 - IN PROGRESS**

**Primary Entry Point:**
```python
from rich_logging import Log, LogLevels

logger = Log.create_logger("myapp", log_level=LogLevels.INFO)
```

**Configuration-Based Entry:**
```python
from rich_logging import Log, LogConfig, LogLevels

config = LogConfig(log_level=LogLevels.DEBUG, ...)
logger = Log.create_logger("myapp", config=config)
```

**Rich Features Entry:**
```python
from rich_logging import Log, LogLevels, ConsoleHandlers, RichFeatureSettings

rich_settings = RichFeatureSettings(enable_panel=True, enable_table=True)
logger = Log.create_logger(
    "myapp",
    log_level=LogLevels.INFO,
    console_handler_type=ConsoleHandlers.RICH,
    rich_features=rich_settings
)
```

**Advanced Entry (Direct Configurator):**
```python
import logging
from rich_logging import LoggerConfigurator, LogConfig, LogLevels

logger = logging.getLogger("myapp")
configurator = LoggerConfigurator(logger)
config = LogConfig(log_level=LogLevels.INFO)
configurator.configure(config)
```

---

## Core Abstractions

### Abstract Base Classes

*To be documented in Task 2.1*

### Interfaces

*To be documented in Task 2.2*

### Core Concepts

*To be documented in Task 2.3*

### Inheritance Hierarchies

*To be documented in Task 2.4*

### Design Contracts

*To be documented in Task 2.5*

---

## Type System & Data Models

### Enums

*To be documented in Task 3.1*

### Dataclasses/Models

*To be documented in Task 3.2*

### Type Relationships

*To be documented in Task 3.3*

### Validation Logic

*To be documented in Task 3.4*

### Default Values

*To be documented in Task 3.5*

### Type Diagrams

*To be documented in Task 3.6*

---

## Exception Hierarchy

### Exception Classes

*To be documented in Task 4.1-4.2*

### Error Contexts

*To be documented in Task 4.3*

### Exception Usage Examples

*To be documented in Task 4.4*

### Error Handling Patterns

*To be documented in Task 4.5*

### Exception Best Practices

*To be documented in Task 4.6*

---

## Implementation Details

### Concrete Implementations

*To be documented in Task 5.1*

### Utility Functions

*To be documented in Task 5.2*

### Helper Modules

*To be documented in Task 5.3*

### Code Walkthroughs

*To be documented in Task 5.4*

### Implementation Patterns

*To be documented in Task 5.5*

### Internal APIs

*To be documented in Task 5.6*

---

## Key Features & Capabilities

### Unique Features

*To be documented in Task 6.1*

### Feature Implementations

*To be documented in Task 6.2-6.3*

### Benefits and Trade-offs

*To be documented in Task 6.4*

### Feature Usage Examples

*To be documented in Task 6.5*

---

## Integration & Usage Patterns

### Common Usage Patterns

*To be documented in Task 7.1*

### Integration with Other Modules

*To be documented in Task 7.2*

### Typical Workflows

*To be documented in Task 7.3*

### Best Practices

*To be documented in Task 7.4*

### Anti-patterns

*To be documented in Task 7.5*

---

## Advanced Topics

### Security Considerations

*To be documented in Task 8.1*

### Performance Considerations

*To be documented in Task 8.2*

### Extensibility Points

*To be documented in Task 8.3*

### Future Roadmap

*To be documented in Task 8.4*

### Migration Guides

*To be documented in Task 8.5*

---

## Code Examples

*Examples will be added throughout the investigation*

### Basic Usage Examples

*To be added*

### Advanced Usage Examples

*To be added*

### Integration Examples

*To be added*

### Complete Workflows

*To be added*

---

## Architecture Diagrams

*Diagrams will be added during Phase 9*

### Component Diagram

*To be added*

### Class Hierarchy Diagram

*To be added*

### Data Flow Diagram

*To be added*

### Integration Diagram

*To be added*

---

## Notes and Observations

*Ad-hoc notes will be added here during investigation*

---

**End of Investigation Notes**

*This document will be continuously updated as the investigation progresses.*
