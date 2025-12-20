# Architecture

This document provides a detailed view of the package_manager module's architecture, design patterns, and structural organization.

---

## Table of Contents

1. [Module Structure](#module-structure)
2. [Design Patterns](#design-patterns)
3. [Layered Architecture](#layered-architecture)
4. [Class Hierarchy](#class-hierarchy)
5. [Data Flow](#data-flow)
6. [Extension Points](#extension-points)

---

## Module Structure

### Directory Layout

```
src/common/modules/package_manager/
├── pyproject.toml                          # Project configuration
├── src/
│   └── dotfiles_package_manager/
│       ├── __init__.py                     # Public API exports
│       ├── core/                           # Core abstractions
│       │   ├── __init__.py
│       │   ├── base.py                     # Abstract base class & exceptions
│       │   ├── types.py                    # Enums and dataclasses
│       │   └── factory.py                  # Factory pattern implementation
│       └── implementations/                # Concrete implementations
│           ├── __init__.py
│           ├── pacman.py                   # Pacman implementation
│           ├── yay.py                      # Yay implementation
│           └── paru.py                     # Paru implementation
├── tests/                                  # Test suite
└── docs/                                   # Documentation
```

### File Purposes

| File | Lines | Purpose |
|------|-------|---------|
| `core/base.py` | 195 | Abstract base class, exceptions, common functionality |
| `core/types.py` | 62 | Type definitions (enums, dataclasses) |
| `core/factory.py` | 169 | Factory for creating and detecting package managers |
| `implementations/pacman.py` | 325 | Pacman package manager implementation |
| `implementations/yay.py` | 332 | Yay AUR helper implementation |
| `implementations/paru.py` | 331 | Paru AUR helper implementation |

### Public API Surface

The module exports a clean public API through `__init__.py`:

```python
from dotfiles_package_manager import (
    # Factory
    PackageManagerFactory,

    # Base class (for type hints)
    PackageManager,

    # Types
    PackageManagerType,
    PackageInfo,
    InstallResult,
    SearchResult,

    # Exceptions
    PackageManagerError,
    PackageNotFoundError,
    PackageInstallationError,
)
```

---

## Design Patterns

### 1. Abstract Factory Pattern

**Location:** `core/factory.py`

The `PackageManagerFactory` class implements the Abstract Factory pattern to create package manager instances without exposing implementation details.

```python
class PackageManagerFactory:
    """Factory for creating package manager instances."""

    # Registry of available managers
    _MANAGERS = {
        PackageManagerType.PACMAN: PacmanPackageManager,
        PackageManagerType.YAY: YayPackageManager,
        PackageManagerType.PARU: ParuPackageManager,
    }

    @classmethod
    def create_auto(cls, prefer_aur_helper: bool = True) -> PackageManager:
        """Auto-detect and create best available manager."""
        # Detection logic...

    @classmethod
    def create(cls, manager_type: PackageManagerType) -> PackageManager:
        """Create specific manager instance."""
        # Creation logic...
```

**Benefits:**
- Decouples client code from concrete implementations
- Centralizes manager creation logic
- Enables automatic detection and selection
- Easy to add new package managers

### 2. Template Method Pattern

**Location:** `core/base.py`

The `PackageManager` abstract base class defines the template for all package managers, with `_run_command` as a shared helper method.

```python
class PackageManager(ABC):
    """Abstract base class for package managers."""

    def _run_command(
        self,
        command: list[str],
        check: bool = True,
        capture_output: bool = True,
        text: bool = True,
        timeout: int | None = None,
    ) -> subprocess.CompletedProcess:
        """Template method for running commands."""
        # Common command execution logic
        return subprocess.run(command, ...)

    @abstractmethod
    def install(self, packages: list[str], ...) -> InstallResult:
        """Subclasses implement specific install logic."""
        pass
```

**Benefits:**
- Eliminates code duplication
- Ensures consistent command execution
- Provides common error handling
- Subclasses focus on manager-specific logic

### 3. Strategy Pattern

**Location:** All implementations

Different package managers are interchangeable strategies that implement the same interface.

```python
# All strategies implement the same interface
pm1: PackageManager = PacmanPackageManager()
pm2: PackageManager = YayPackageManager()
pm3: PackageManager = ParuPackageManager()

# Can be used interchangeably
for pm in [pm1, pm2, pm3]:
    result = pm.install(["package"])
```

**Benefits:**
- Package managers are interchangeable
- Easy to switch between managers
- Consistent interface regardless of implementation
- Testable with mock strategies

### 4. Registry Pattern

**Location:** `core/factory.py`

The factory maintains a registry of available package managers.

```python
_MANAGERS = {
    PackageManagerType.PACMAN: PacmanPackageManager,
    PackageManagerType.YAY: YayPackageManager,
    PackageManagerType.PARU: ParuPackageManager,
}
```

**Benefits:**
- Centralized manager registration
- Easy to add new managers
- Type-safe manager lookup
- Supports iteration over available managers

---

## Layered Architecture

The module follows a clean layered architecture:

```
┌─────────────────────────────────────────┐
│         Public API Layer                │
│  (Exports from __init__.py)             │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│         Factory Layer                   │
│  (PackageManagerFactory)                │
│  - Auto-detection                       │
│  - Manager creation                     │
│  - Preference handling                  │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│      Abstraction Layer                  │
│  (PackageManager ABC, Types)            │
│  - Interface definition                 │
│  - Common functionality                 │
│  - Type definitions                     │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│     Implementation Layer                │
│  (Pacman, Yay, Paru)                    │
│  - Manager-specific logic               │
│  - Command construction                 │
│  - Output parsing                       │
└─────────────────────────────────────────┘
```

### Layer Responsibilities

**Public API Layer:**
- Exports clean, minimal interface
- Hides internal implementation details
- Provides type hints for IDE support

**Factory Layer:**
- Detects available package managers
- Selects best manager based on preferences
- Creates and initializes manager instances
- Validates manager availability

**Abstraction Layer:**
- Defines common interface (ABC)
- Provides shared functionality (_run_command)
- Defines data types and exceptions
- Enforces contracts through abstract methods

**Implementation Layer:**
- Implements manager-specific logic
- Constructs appropriate commands
- Parses manager-specific output
- Handles manager-specific quirks

---

## Class Hierarchy

```
PackageManager (ABC)
├── PacmanPackageManager
├── YayPackageManager
└── ParuPackageManager

PackageManagerError (Exception)
├── PackageNotFoundError
└── PackageInstallationError

Enum
└── PackageManagerType
    ├── PACMAN
    ├── YAY
    └── PARU

@dataclass
├── PackageInfo
├── InstallResult
└── SearchResult
```

### Inheritance Details

**PackageManager Hierarchy:**
- All implementations inherit from `PackageManager` ABC
- Must implement all abstract methods
- Can override `_find_executable()` for custom detection
- Share `_run_command()` helper method

**Exception Hierarchy:**
- All exceptions inherit from `PackageManagerError`
- Enables catching all module exceptions with single except clause
- Specific exceptions for specific error types

---

## Data Flow

### Installation Flow

```
User Code
    ↓
pm.install(["vim", "git"])
    ↓
PacmanPackageManager.install()
    ↓
Construct command: ["sudo", "pacman", "-S", "--noconfirm", "vim", "git"]
    ↓
_run_command(command)
    ↓
subprocess.run()
    ↓
Parse output
    ↓
Return InstallResult(success=True, packages_installed=["vim", "git"], ...)
    ↓
User Code
```

### Search Flow

```
User Code
    ↓
pm.search("python")
    ↓
PacmanPackageManager.search()
    ↓
Construct command: ["pacman", "-Ss", "python"]
    ↓
_run_command(command)
    ↓
Parse output with regex
    ↓
Create PackageInfo objects
    ↓
Return SearchResult(packages=[...], query="python", total_found=50)
    ↓
User Code
```

### Factory Auto-Detection Flow

```
User Code
    ↓
PackageManagerFactory.create_auto(prefer_aur_helper=True)
    ↓
Check if Paru available (shutil.which("paru"))
    ↓ (if found)
Create ParuPackageManager()
    ↓
Return instance
    ↓
User Code
```

---

## Extension Points

### Adding a New Package Manager

To add support for a new package manager (e.g., `apt` for Debian):

**Step 1: Add to enum**
```python
# core/types.py
class PackageManagerType(Enum):
    PACMAN = "pacman"
    YAY = "yay"
    PARU = "paru"
    APT = "apt"  # New
```

**Step 2: Create implementation**
```python
# implementations/apt.py
class AptPackageManager(PackageManager):
    @property
    def manager_type(self) -> PackageManagerType:
        return PackageManagerType.APT

    def _find_executable(self) -> Path | None:
        executable = shutil.which("apt")
        return Path(executable) if executable else None

    # Implement all abstract methods...
```

**Step 3: Register in factory**
```python
# core/factory.py
_MANAGERS = {
    PackageManagerType.PACMAN: PacmanPackageManager,
    PackageManagerType.YAY: YayPackageManager,
    PackageManagerType.PARU: ParuPackageManager,
    PackageManagerType.APT: AptPackageManager,  # New
}
```

### Customizing Preference Order

```python
# core/factory.py
_AUR_HELPER_PREFERENCE = [
    PackageManagerType.PARU,   # 1st choice
    PackageManagerType.YAY,    # 2nd choice
    # Add more here
]
```

### Adding Manager-Specific Methods

Implementations can add custom methods beyond the base interface:

```python
class ParuPackageManager(PackageManager):
    # Standard methods...

    def review_aur_package(self, package: str):
        """Paru-specific: Review AUR package before install."""
        # Custom functionality
        pass
```

---

**Next:** [API Reference](api_reference.md) | [Usage Guide](usage_guide.md)
