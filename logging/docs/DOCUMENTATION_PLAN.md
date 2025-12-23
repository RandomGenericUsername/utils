# Documentation Plan - Tests-First Approach

## Overview

This documentation plan follows the **Tests-First Documentation Enablement** guidelines. All documentation will be grounded in verified behavior from our 140 passing tests.

**Principle**: Documentation must cite the tests that prove each documented behavior.

---

## Test Coverage Summary

### Contract Tests (91 tests)
- **Log API** (23 tests): `tests/contract/test_log_api.py`
  - `Log.create_logger()` - 14 tests
  - `Log.update()` - 9 tests
  
- **Log Level Utilities** (26 tests): `tests/contract/test_log_level_utils.py`
  - `validate_log_level_string()` - 16 tests
  - `get_log_level_from_verbosity()` - 6 tests
  - `parse_log_level()` - 4 tests

- **RichLogger API** (42 tests): `tests/contract/test_rich_logger_api.py`
  - Standard logging delegation - 10 tests
  - Properties - 4 tests
  - Display methods - 8 tests
  - Context managers - 5 tests
  - Task context - 4 tests
  - Interactive methods - 4 tests
  - Graceful degradation - 7 tests

### Integration Tests (16 tests)
- **Logger Lifecycle** (7 tests): `tests/integration/test_logger_lifecycle.py`
  - Logger creation and logging - 3 tests
  - Logger updates - 2 tests
  - Multiple loggers - 2 tests

- **Rich Features** (9 tests): `tests/integration/test_rich_features.py`
  - Display features - 6 tests
  - Context managers - 2 tests
  - Task context - 1 test

### Unit Tests (6 tests)
- **FormatterFactory** (6 tests): `tests/unit/test_formatter_factory.py`
  - Formatter creation - 5 tests
  - Error handling - 1 test

### Pre-existing Tests (27 tests)
- **Rich Features** (12 tests): `tests/test_rich_features.py`
- **Rich Interactive** (12 tests): `tests/test_rich_interactive.py`
- **Task Context** (3 tests): `tests/test_task_context.py`

---

## Documentation Structure

### 1. API Reference (`docs/api-reference.md`)
**Purpose**: Complete API documentation for all public interfaces

**Content** (evidence-based):
- `Log.create_logger()` - all parameters, return types, examples
  - Evidence: `tests/contract/test_log_api.py::TestLogCreateLogger`
- `Log.update()` - all parameters, return types, examples
  - Evidence: `tests/contract/test_log_api.py::TestLogUpdate`
- `RichLogger` methods - all public methods with signatures
  - Evidence: `tests/contract/test_rich_logger_api.py`
- Utility functions - `parse_log_level()`, `validate_log_level_string()`, etc.
  - Evidence: `tests/contract/test_log_level_utils.py`

**Format**: Each API entry includes:
- Signature
- Parameters (with types and defaults)
- Return type
- Description
- Example usage (from tests)
- Test citation

---

### 2. Usage Guide (`docs/usage-guide.md`)
**Purpose**: Getting started and common workflows

**Content** (evidence-based):
- Quick start
  - Evidence: `tests/integration/test_logger_lifecycle.py::test_create_logger_and_log_messages`
- Basic logging
  - Evidence: `tests/integration/test_logger_lifecycle.py::test_logger_respects_log_level`
- Configuration examples
  - Evidence: `tests/contract/test_log_api.py::test_create_logger_with_config_object`
- Updating logger configuration
  - Evidence: `tests/integration/test_logger_lifecycle.py::test_update_logger_level`
- Multiple loggers
  - Evidence: `tests/integration/test_logger_lifecycle.py::test_multiple_loggers_independent`

**Format**: Tutorial-style with code examples from integration tests

---

### 3. Configuration Reference (`docs/configuration.md`)
**Purpose**: Complete configuration options reference

**Content** (evidence-based):
- `LogConfig` dataclass
  - Evidence: `tests/contract/test_log_api.py::test_create_logger_with_config_object`
- Log levels (`LogLevels` enum)
  - Evidence: `tests/contract/test_log_api.py::TestLogCreateLogger` (levels tests)
- Console handlers (`ConsoleHandlers` enum)
  - Evidence: `tests/contract/test_log_api.py::test_create_logger_with_console_handler_*`
- Formatters (`LogFormatters` enum)
  - Evidence: `tests/unit/test_formatter_factory.py`
- Formatter styles (`LogFormatterStyleChoices` enum)
  - Evidence: `tests/unit/test_formatter_factory.py::test_create_formatter_with_*_style`
- Rich feature settings (`RichFeatureSettings`)
  - Evidence: `tests/contract/test_rich_logger_api.py::test_logger_has_rich_settings`

**Format**: Reference table with all options, types, defaults, and descriptions

---

### 4. Advanced Features Guide (`docs/advanced-features.md`)
**Purpose**: Rich display methods, context managers, and advanced usage

**Content** (evidence-based):
- Rich display methods
  - `table()` - Evidence: `tests/integration/test_rich_features.py::test_table_displays_data`
  - `panel()` - Evidence: `tests/integration/test_rich_features.py::test_panel_displays_message`
  - `rule()` - Evidence: `tests/integration/test_rich_features.py::test_rule_displays_separator`
  - `syntax()` - Evidence: `tests/integration/test_rich_features.py::test_syntax_displays_code`
  - `markdown()` - Evidence: `tests/integration/test_rich_features.py::test_markdown_displays_formatted_text`
  - `json()` - Evidence: `tests/integration/test_rich_features.py::test_json_displays_formatted_json`
- Context managers
  - `progress()` - Evidence: `tests/integration/test_rich_features.py::test_progress_context_manager_workflow`
  - `status()` - Evidence: `tests/contract/test_rich_logger_api.py::test_status_context_manager`
  - `live()` - Evidence: `tests/contract/test_rich_logger_api.py::test_live_context_manager`
- Task context for parallel execution
  - Evidence: `tests/integration/test_rich_features.py::test_task_context_workflow`
- Interactive methods
  - `prompt()` - Evidence: `tests/contract/test_rich_logger_api.py::test_prompt_returns_user_input`
  - `confirm()` - Evidence: `tests/contract/test_rich_logger_api.py::test_confirm_returns_boolean`
- Graceful degradation when Rich disabled
  - Evidence: `tests/contract/test_rich_logger_api.py::TestRichLoggerGracefulDegradation`

**Format**: Feature-focused with examples and use cases

---

### 5. Architecture Documentation (`docs/architecture.md`)
**Purpose**: System design and component relationships

**Content** (evidence-based from code structure):
- Component overview
- Design patterns (Factory, Wrapper, Singleton)
- Module structure
- Extension points

**Format**: Diagrams and explanations with code references

---

## Documentation Creation Order

1. ✅ **Documentation Plan** (this document)
2. **API Reference** - Most critical, defines contracts
3. **Usage Guide** - Second priority, helps users get started
4. **Configuration Reference** - Third priority, comprehensive options
5. **Advanced Features Guide** - Fourth priority, power user features
6. **Architecture Documentation** - Fifth priority, for contributors
7. **Update README** - Final step, link to all documentation

---

## Evidence Citation Format

Every documented behavior must cite the test that proves it:

```markdown
### Log.create_logger()

Creates and configures a new logger instance.

**Signature**:
```python
def create_logger(
    name: str | None = None,
    log_level: LogLevels = LogLevels.INFO,
    ...
) -> RichLogger
```

**Evidence**: `tests/contract/test_log_api.py::TestLogCreateLogger::test_create_logger_returns_rich_logger`
```

---

## Next Steps

1. Create `docs/` directory
2. Generate API Reference from contract tests
3. Generate Usage Guide from integration tests
4. Generate Configuration Reference from contract/unit tests
5. Generate Advanced Features Guide from integration tests
6. Generate Architecture Documentation from code structure
7. Update README.md with links to new documentation

