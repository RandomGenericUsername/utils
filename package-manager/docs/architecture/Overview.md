# Architecture Overview

## Purpose

Documents the system architecture and design decisions of dotfiles-package-manager.

---

## System Structure

```
dotfiles-package-manager/
├── core/
│   ├── base.py          # Abstract base class + exceptions
│   ├── types.py         # Enums and data classes
│   └── factory.py       # Factory + distribution detection
└── implementations/
    ├── arch/
    │   ├── pacman.py    # Pacman implementation
    │   ├── yay.py       # Yay implementation (AUR)
    │   └── paru.py      # Paru implementation (AUR)
    ├── debian/
    │   └── apt.py       # APT implementation
    └── redhat/
        └── dnf.py       # DNF implementation
```

---

## Design Patterns

### Abstract Base Class Pattern

All package managers inherit from `PackageManager` ABC:

```python
class PackageManager(ABC):
    @abstractmethod
    def install(self, packages: list[str], update_system: bool = False) -> InstallResult: ...
    @abstractmethod
    def remove(self, packages: list[str], remove_dependencies: bool = False) -> InstallResult: ...
    @abstractmethod
    def update_system(self, dry_run: bool = False) -> InstallResult: ...
    @abstractmethod
    def search(self, query: str, limit: int | None = None) -> SearchResult: ...
    @abstractmethod
    def is_installed(self, package: str) -> bool: ...
    @abstractmethod
    def get_package_info(self, package: str) -> PackageInfo | None: ...
```

**Source**: `src/dotfiles_package_manager/core/base.py` (lines 37-148)

### Factory Pattern

`PackageManagerFactory` handles:
- Auto-detection of distribution family
- Creation of appropriate package manager
- Availability checking

```python
pm = PackageManagerFactory.create_auto()  # Auto-detect
pm = PackageManagerFactory.create(PackageManagerType.PACMAN)  # Specific
```

**Source**: `src/dotfiles_package_manager/core/factory.py` (lines 75-284)

---

## Key Design Decisions

### 1. Cross-Manager Consistency

**Decision**: All 5 implementations MUST satisfy identical contracts.

**Rationale**: Consuming applications should work identically regardless of which package manager is used.

**Enforcement**: 134 contract tests verify identical behavior across all managers.

**Evidence**: `tests/contract/test_cross_manager_*.py`

### 2. Partial Failure Semantics

**Decision**: `success=True` if ANY package succeeds.

**Rationale**: Enables pipeline-based workflows where partial success is acceptable.

**Evidence**: `tests/characterization/test_characterization__partial_install_success.py`

### 3. Exception Propagation

**Decision**: Subprocess exceptions propagate; only internal errors are wrapped.

**Rationale**: Caller has context to decide recovery strategy.

**Evidence**: `tests/characterization/test_characterization__subprocess_errors.py`

### 4. Subprocess Execution Model

**Decision**: All commands run via `subprocess.run()` with explicit PIPE handling.

**Rationale**: Consistent output capture across TTY/non-TTY environments.

**Source**: `src/dotfiles_package_manager/core/base.py::_run_command` (lines 150-215)

---

## Component Relationships

```
┌─────────────────────────────────────┐
│     PackageManagerFactory           │
│  ┌──────────────────────────────┐   │
│  │ detect_distribution_family() │   │
│  │ create_auto()                │   │
│  │ create()                     │   │
│  │ is_available()               │   │
│  └──────────────────────────────┘   │
└─────────────┬───────────────────────┘
              │ creates
              ▼
┌─────────────────────────────────────┐
│     PackageManager (ABC)            │
│  ┌──────────────────────────────┐   │
│  │ install()                    │   │
│  │ remove()                     │   │
│  │ update_system()              │   │
│  │ search()                     │   │
│  │ is_installed()               │   │
│  │ get_package_info()           │   │
│  │ _run_command()               │   │
│  └──────────────────────────────┘   │
└─────────────┬───────────────────────┘
              │ implemented by
              ▼
┌─────────────────────────────────────┐
│     Implementations                 │
│  ┌──────────┐ ┌──────────┐          │
│  │ Pacman   │ │ Apt      │          │
│  └──────────┘ └──────────┘          │
│  ┌──────────┐ ┌──────────┐          │
│  │ Yay      │ │ Dnf      │          │
│  └──────────┘ └──────────┘          │
│  ┌──────────┐                       │
│  │ Paru     │                       │
│  └──────────┘                       │
└─────────────────────────────────────┘
```

---

## Distribution Detection

`detect_distribution_family()` parses `/etc/os-release`:

| Keywords | Result |
|----------|--------|
| arch linux, manjaro, endeavouros, artix | `ARCH` |
| debian, ubuntu, mint, pop, elementary | `DEBIAN` |
| fedora, rhel, centos, rocky, alma | `REDHAT` |
| (not found) | `UNKNOWN` |

**Source**: `src/dotfiles_package_manager/core/factory.py` (lines 29-72)

---

## Test Architecture

```
tests/
├── contract/           # Cross-manager consistency (134 tests)
├── characterization/   # Freeze current behavior (55 tests)
└── unit/               # Implementation-specific (reserved)
```

**Total**: 189 tests, 100% pass rate

---

## Related Documentation

- [Implementation Guide](ImplementationGuide.md)
- [PackageManager API](../api/PackageManager.md)
- [PackageManagerFactory API](../api/PackageManagerFactory.md)

