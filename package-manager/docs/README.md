# dotfiles-package-manager Documentation

A unified abstraction layer for Linux package managers.

---

## Quick Links

| I want to... | Go to |
|--------------|-------|
| Get started quickly | [Quick Start Guide](guides/QuickStart.md) |
| Learn all features | [Advanced Usage Guide](guides/AdvancedUsage.md) |
| Handle errors properly | [Error Handling Guide](guides/ErrorHandling.md) |
| Understand the API | [API Reference](#api-reference) |
| Add a new package manager | [Implementation Guide](architecture/ImplementationGuide.md) |

---

## Supported Package Managers

| Manager | Distribution | Third-Party Support |
|---------|--------------|---------------------|
| pacman | Arch Linux | Official repos only |
| yay | Arch Linux | AUR + official |
| paru | Arch Linux | AUR + official |
| apt | Debian/Ubuntu | PPAs + official |
| dnf | Fedora/RHEL | COPR + official |

---

## API Reference

### Core Classes

- [PackageManager](api/PackageManager.md) - Abstract base class for all package managers
- [PackageManagerFactory](api/PackageManagerFactory.md) - Factory for creating package managers
- [Types](api/Types.md) - Enums, data classes, and exceptions

---

## User Guides

- [Quick Start](guides/QuickStart.md) - Get started in 5 minutes
- [Advanced Usage](guides/AdvancedUsage.md) - All features with examples
- [Error Handling](guides/ErrorHandling.md) - Exception patterns

---

## Behavior Reference

These documents describe verified behaviors, backed by characterization tests:

- [Partial Failures](reference/PartialFailures.md) - How partial success is handled
- [Empty Lists](reference/EmptyLists.md) - Behavior with empty package lists
- [Exception Propagation](reference/ExceptionPropagation.md) - Which exceptions propagate

---

## Architecture

- [Overview](architecture/Overview.md) - System design and patterns
- [Implementation Guide](architecture/ImplementationGuide.md) - Adding new package managers

---

## Test Coverage

All documentation is backed by **189 passing tests**:

| Category | Tests | Purpose |
|----------|-------|---------|
| Contract | 134 | Cross-manager consistency |
| Characterization | 55 | Freeze current behavior |
| **Total** | **189** | **100% pass rate** |

### Test Files

```
tests/
├── contract/
│   ├── test_cross_manager_install_contract.py (35 tests)
│   ├── test_cross_manager_remove_contract.py (25 tests)
│   ├── test_cross_manager_update_system_contract.py (30 tests)
│   ├── test_cross_manager_query_contract.py (35 tests)
│   └── test_factory_contracts.py (19 tests)
└── characterization/
    ├── test_characterization__empty_package_list.py (20 tests)
    ├── test_characterization__partial_install_success.py (15 tests)
    └── test_characterization__subprocess_errors.py (20 tests)
```

---

## Documentation Methodology

This documentation follows **Tests-First Documentation** principles:

1. **Evidence-Only Claims** - Every behavior cites test file and source code
2. **No Speculation** - Unknowns are marked as "Unknown" or "Needs confirmation"
3. **Highest-Value First** - Public contracts documented before internals
4. **Cross-Manager Consistency** - All 5 managers satisfy identical contracts

---

## Key Guarantees

These guarantees are verified by contract tests:

| Guarantee | Evidence |
|-----------|----------|
| All 5 managers behave identically | 134 cross-manager tests |
| Empty lists return `success=True` | 20 characterization tests |
| Partial failures return `success=True` | 15 characterization tests |
| Subprocess exceptions propagate | 20 characterization tests |

---

## Running Tests

```bash
# Run all tests
uv run pytest tests/ -v

# Run contract tests only
uv run pytest tests/contract/ -v

# Run characterization tests only
uv run pytest tests/characterization/ -v

# Run with coverage
uv run pytest tests/ --cov=src/dotfiles_package_manager
```

---

## Source Code

- **Repository**: `src/dotfiles_package_manager/`
- **Core**: `core/base.py`, `core/types.py`, `core/factory.py`
- **Implementations**: `implementations/arch/`, `implementations/debian/`, `implementations/redhat/`

