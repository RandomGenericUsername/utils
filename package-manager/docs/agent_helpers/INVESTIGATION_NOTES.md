# Investigation Notes - Package Manager Module

**Module:** `src/common/modules/package_manager`
**Investigation Started:** 2025-10-19
**Target:** Comprehensive documentation of the package_manager module

---

## Table of Contents

1. [Architecture & Structure](#architecture--structure)
2. [Core Abstractions](#core-abstractions)
3. [Type System](#type-system)
4. [Exception Hierarchy](#exception-hierarchy)
5. [Implementation Details](#implementation-details)
6. [Factory Pattern](#factory-pattern)
7. [Integration & Usage](#integration--usage)
8. [Advanced Topics](#advanced-topics)
9. [Code Examples](#code-examples)
10. [Troubleshooting](#troubleshooting)

---

## Architecture & Structure

### Directory Structure

```
src/common/modules/package_manager/
├── docs/                                    # Documentation (output location)
│   └── agent_helpers/                       # Investigation helper documents
│       ├── README.md
│       ├── INTERACTIVE_PROMPT.md
│       ├── REQUIREMENTS_CHECKLIST.md
│       ├── INVESTIGATION_NOTES.md (this file)
│       └── SESSION_SUMMARY.md
├── src/
│   └── dotfiles_package_manager/            # Main package
│       ├── __init__.py                      # Public API exports
│       ├── core/                            # Core abstractions and types
│       │   ├── __init__.py
│       │   ├── base.py                      # Abstract base class & exceptions
│       │   ├── types.py                     # Data types and enums
│       │   └── factory.py                   # Factory for auto-detection
│       └── implementations/                 # Concrete implementations
│           ├── __init__.py
│           ├── pacman.py                    # Pacman implementation
│           ├── yay.py                       # Yay AUR helper implementation
│           └── paru.py                      # Paru AUR helper implementation
├── tests/                                   # Test directory (currently empty)
├── pyproject.toml                           # Project configuration
└── uv.lock                                  # Dependency lock file
```

### File Purposes

**Core Module Files:**
- `__init__.py` - Public API exports (PackageManager, PackageManagerFactory, types, exceptions)
- `core/base.py` - Abstract base class and exception definitions
- `core/types.py` - Type definitions (enums, dataclasses)
- `core/factory.py` - Factory pattern for package manager creation and auto-detection

**Implementation Files:**
- `implementations/pacman.py` - Pacman package manager (official Arch Linux)
- `implementations/yay.py` - Yay AUR helper
- `implementations/paru.py` - Paru AUR helper

### Module Organization

**Layered Architecture:**

```
┌─────────────────────────────────────────────────────────┐
│                    Public API Layer                      │
│  (dotfiles_package_manager/__init__.py)                 │
│  Exports: PackageManager, Factory, Types, Exceptions    │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                   Factory Layer                          │
│  (core/factory.py)                                      │
│  Auto-detection, Manager creation, Recommendations      │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                 Abstraction Layer                        │
│  (core/base.py, core/types.py)                          │
│  Abstract base class, Type definitions, Exceptions      │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│              Implementation Layer                        │
│  (implementations/*.py)                                 │
│  Concrete implementations: Pacman, Yay, Paru            │
└─────────────────────────────────────────────────────────┘
```

### Design Patterns

1. **Abstract Factory Pattern** - PackageManagerFactory creates appropriate manager instances
2. **Template Method Pattern** - Base class provides _run_command, subclasses implement specifics
3. **Strategy Pattern** - Different package managers are interchangeable strategies
4. **Registry Pattern** - Factory maintains registry of available managers

---

### Public API Surface

**Exported from `dotfiles_package_manager/__init__.py`:**

```python
from .core.base import PackageInfo, PackageManager, PackageManagerError
from .core.factory import PackageManagerFactory
from .core.types import InstallResult, PackageManagerType, SearchResult

__all__ = [
    "PackageManager",           # Abstract base class
    "PackageManagerError",      # Base exception
    "PackageInfo",              # Package information dataclass
    "PackageManagerFactory",    # Factory for creating managers
    "PackageManagerType",       # Enum of supported managers
    "InstallResult",            # Result of install/remove/update operations
    "SearchResult",             # Result of search operations
]
```

**Entry Points:**
1. **PackageManagerFactory.create_auto()** - Automatic detection and creation
2. **PackageManagerFactory.create(type)** - Create specific manager
3. **PackageManager** - Direct instantiation of concrete implementations

### Key Design Decisions

1. **Arch Linux Specific** - Only supports Arch-based package managers
2. **No External Dependencies** - Pure Python, uses only stdlib
3. **Subprocess-based** - Wraps command-line tools, doesn't use native APIs
4. **Automatic Detection** - Factory can auto-detect available managers
5. **AUR Helper Preference** - Prefers Paru > Yay > Pacman
6. **Unified Interface** - All managers implement same abstract interface

---

## Core Abstractions

### PackageManager Abstract Base Class

**Location:** `core/base.py`
**Purpose:** Defines the contract that all package manager implementations must follow

**Class Definition:**

```python
class PackageManager(ABC):
    """Abstract base class for package managers."""

    def __init__(self, executable_path: Path | None = None):
        """Initialize package manager.

        Args:
            executable_path: Path to the package manager executable
        """
        self.executable_path = executable_path or self._find_executable()
        if not self.executable_path or not self.executable_path.exists():
            raise PackageManagerError(
                f"Package manager executable not found: {self.manager_type.value}"
            )
```

**Abstract Properties:**

1. **manager_type** → PackageManagerType
   - Returns the type of package manager
   - Must be implemented by subclasses

**Abstract Methods (Must Implement):**

1. **_find_executable()** → Path | None
   - Find the package manager executable in PATH
   - Returns Path to executable or None if not found

2. **install(packages, update_system)** → InstallResult
   - Install one or more packages
   - Args:
     - packages: list[str] - Package names to install
     - update_system: bool - Whether to update system first
   - Returns: InstallResult with success status and details

3. **remove(packages, remove_dependencies)** → InstallResult
   - Remove one or more packages
   - Args:
     - packages: list[str] - Package names to remove
     - remove_dependencies: bool - Whether to remove unused deps
   - Returns: InstallResult with removal details

4. **search(query, limit)** → SearchResult
   - Search for packages
   - Args:
     - query: str - Search query
     - limit: int | None - Max results to return
   - Returns: SearchResult with found packages

5. **update_system(dry_run)** → InstallResult
   - Update system packages
   - Args:
     - dry_run: bool - If True, only check for updates
   - Returns: InstallResult with update details

6. **is_installed(package)** → bool
   - Check if a package is installed
   - Args:
     - package: str - Package name
   - Returns: True if installed, False otherwise

7. **get_package_info(package)** → PackageInfo | None
   - Get detailed package information
   - Args:
     - package: str - Package name
   - Returns: PackageInfo if found, None otherwise

**Concrete Helper Method:**

**_run_command(command, capture_output, check, timeout)** → subprocess.CompletedProcess
- Run a command with proper error handling
- Args:
  - command: list[str] - Command and arguments
  - capture_output: bool - Whether to capture stdout/stderr
  - check: bool - Whether to raise exception on non-zero exit
  - timeout: int | None - Timeout in seconds
- Returns: CompletedProcess result
- Raises: PackageManagerError on failure

**Error Handling:**
- Catches subprocess.TimeoutExpired → PackageManagerError
- Catches subprocess.CalledProcessError → PackageManagerError
- Catches FileNotFoundError → PackageManagerError

### Inheritance Hierarchy

```
ABC (Python's Abstract Base Class)
  │
  └── PackageManager (abstract)
        │
        ├── PacmanPackageManager (concrete)
        ├── YayPackageManager (concrete)
        └── ParuPackageManager (concrete)
```

### Design Contracts

**Initialization Contract:**
- Subclass must implement _find_executable()
- Subclass must implement manager_type property
- If executable not found, raise PackageManagerError
- Store executable_path for later use

**Method Implementation Contract:**
- All abstract methods must be implemented
- Methods should return appropriate result types
- Methods should handle errors gracefully (return result with success=False)
- Methods should not raise exceptions for normal failures (package not found, etc.)
- Only raise PackageManagerError for system-level failures

**Command Execution Contract:**
- Use _run_command() for all subprocess calls
- Let _run_command() handle error wrapping
- Parse command output to extract meaningful information
- Return structured results (InstallResult, SearchResult, PackageInfo)

---

## Type System

**Location:** `core/types.py`

### PackageManagerType Enum

**Purpose:** Enumerate supported package manager types

```python
class PackageManagerType(Enum):
    """Supported package manager types."""

    PACMAN = "pacman"  # Official Arch Linux package manager
    YAY = "yay"        # AUR helper (Yet Another Yogurt)
    PARU = "paru"      # AUR helper (Paru is Rusty AUR helper)
```

**Usage:**
- Used by factory to identify which manager to create
- Used by implementations to identify themselves
- Used for manager preference ordering

### PackageInfo Dataclass

**Purpose:** Store information about a package

```python
@dataclass
class PackageInfo:
    """Information about a package."""

    name: str                        # Package name (required)
    version: str | None = None       # Package version
    description: str | None = None   # Package description
    repository: str | None = None    # Repository (core, extra, community, aur, etc.)
    installed: bool = False          # Whether package is installed
    size: str | None = None          # Package size (installed or download)
    dependencies: list[str] = None   # List of dependency package names

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
```

**Fields:**
- **name** (required) - The package name
- **version** - Version string (e.g., "1.2.3-1")
- **description** - Human-readable description
- **repository** - Source repository name
- **installed** - Installation status
- **size** - Size string (e.g., "10.5 MiB")
- **dependencies** - List of dependency names

**Default Initialization:**
- dependencies defaults to empty list if None

### InstallResult Dataclass

**Purpose:** Store results of install/remove/update operations

```python
@dataclass
class InstallResult:
    """Result of a package installation operation."""

    success: bool                      # Overall operation success
    packages_installed: list[str]      # Successfully installed/removed packages
    packages_failed: list[str]         # Failed packages
    output: str = ""                   # Command stdout
    error_message: str | None = None   # Error message if failed

    def __post_init__(self):
        if not self.packages_installed:
            self.packages_installed = []
        if not self.packages_failed:
            self.packages_failed = []
```

**Fields:**
- **success** (required) - True if operation succeeded
- **packages_installed** (required) - List of successful package names
- **packages_failed** (required) - List of failed package names
- **output** - Standard output from command
- **error_message** - Error message if operation failed

**Usage Notes:**
- For remove operations, packages_installed contains removed packages
- For update operations, packages_installed is typically empty
- Partial success possible: some packages succeed, others fail

### SearchResult Dataclass

**Purpose:** Store results of package search operations

```python
@dataclass
class SearchResult:
    """Result of a package search operation."""

    packages: list[PackageInfo]   # Found packages
    query: str                    # Original search query
    total_found: int = 0          # Total number found

    def __post_init__(self):
        if not self.packages:
            self.packages = []
        if self.total_found == 0:
            self.total_found = len(self.packages)
```

**Fields:**
- **packages** (required) - List of PackageInfo objects
- **query** (required) - The search query string
- **total_found** - Total number of packages found

**Default Initialization:**
- packages defaults to empty list if None
- total_found auto-calculated from packages length if 0

### Type Relationships

```
PackageManagerType (Enum)
    ↓ used by
PackageManagerFactory
    ↓ creates
PackageManager
    ↓ returns
InstallResult, SearchResult, PackageInfo

PackageInfo
    ↓ contained in
SearchResult.packages

InstallResult
    ↓ returned by
install(), remove(), update_system()

SearchResult
    ↓ returned by
search()

PackageInfo
    ↓ returned by
get_package_info()
```

---

## Exception Hierarchy

**Location:** `core/base.py`

### Exception Class Diagram

```
Exception (Python built-in)
  │
  └── PackageManagerError (base exception)
        │
        ├── PackageNotFoundError
        └── PackageInstallationError
```

### PackageManagerError

**Purpose:** Base exception for all package manager operations

```python
class PackageManagerError(Exception):
    """Base exception for package manager operations."""

    def __init__(
        self,
        message: str,
        command: str | None = None,
        exit_code: int | None = None,
    ):
        super().__init__(message)
        self.command = command      # Command that failed
        self.exit_code = exit_code  # Exit code if applicable
```

**Attributes:**
- **message** (str) - Error message
- **command** (str | None) - The command that failed
- **exit_code** (int | None) - Process exit code

**When Raised:**
- Executable not found during initialization
- Command timeout
- Subprocess execution failure
- File not found errors

**Example:**
```python
raise PackageManagerError(
    "Command timed out after 30s: pacman -Syu",
    command="pacman -Syu",
    exit_code=None
)
```

### PackageNotFoundError

**Purpose:** Raised when a package is not found

```python
class PackageNotFoundError(PackageManagerError):
    """Raised when a package is not found."""
    pass
```

**Inherits from:** PackageManagerError

**When Raised:**
- Package doesn't exist in repositories
- Package name is misspelled
- Repository not synchronized

**Note:** Currently defined but not actively used in implementations. Implementations return InstallResult with success=False instead.

### PackageInstallationError

**Purpose:** Raised when package installation fails

```python
class PackageInstallationError(PackageManagerError):
    """Raised when package installation fails."""
    pass
```

**Inherits from:** PackageManagerError

**When Raised:**
- Installation process fails
- Dependency conflicts
- Disk space issues
- Permission problems

**Note:** Currently defined but not actively used in implementations. Implementations return InstallResult with success=False instead.

### Error Handling Patterns

**Pattern 1: Initialization Errors (Raises Exception)**

```python
def __init__(self, executable_path: Path | None = None):
    self.executable_path = executable_path or self._find_executable()
    if not self.executable_path or not self.executable_path.exists():
        raise PackageManagerError(
            f"Package manager executable not found: {self.manager_type.value}"
        )
```

**Pattern 2: Command Execution Errors (Raises Exception)**

```python
def _run_command(self, command, capture_output=True, check=True, timeout=None):
    try:
        result = subprocess.run(...)
        return result
    except subprocess.TimeoutExpired as e:
        raise PackageManagerError(
            f"Command timed out after {timeout}s: {' '.join(command)}",
            command=" ".join(command),
        ) from e
    except subprocess.CalledProcessError as e:
        raise PackageManagerError(
            f"Command failed: {' '.join(command)}",
            command=" ".join(command),
            exit_code=e.returncode,
        ) from e
    except FileNotFoundError as e:
        raise PackageManagerError(
            f"Executable not found: {command[0]}",
            command=" ".join(command),
        ) from e
```

**Pattern 3: Operation Errors (Returns Result)**

```python
def install(self, packages, update_system=False):
    try:
        result = self._run_command(command, check=False)
        if result.returncode == 0:
            return InstallResult(success=True, ...)
        else:
            return InstallResult(success=False, ...)
    except PackageManagerError as e:
        return InstallResult(
            success=False,
            packages_installed=[],
            packages_failed=packages.copy(),
            error_message=str(e),
        )
```

### Error Handling Philosophy

**Exceptions vs. Return Values:**

1. **Raise Exceptions For:**
   - System-level failures (executable not found)
   - Programming errors (invalid arguments)
   - Unrecoverable errors (timeout, permission denied)

2. **Return Error Results For:**
   - Package not found (normal operation failure)
   - Installation failure (user-level error)
   - Partial success scenarios

**Rationale:**
- Allows callers to handle package-level failures gracefully
- Distinguishes between system errors and package errors
- Enables partial success reporting (some packages succeed, others fail)

---

## Implementation Details

### Overview of Implementations

All three implementations (Pacman, Yay, Paru) follow the same structure:

1. Implement `manager_type` property
2. Implement `_find_executable()` using `shutil.which()`
3. Implement all abstract methods
4. Use similar command construction patterns
5. Parse output to extract information

### Common Patterns Across Implementations

**Executable Detection:**
```python
def _find_executable(self) -> Path | None:
    executable = shutil.which("pacman")  # or "yay" or "paru"
    return Path(executable) if executable else None
```

**Empty Package List Handling:**
```python
if not packages:
    return InstallResult(
        success=True, packages_installed=[], packages_failed=[]
    )
```

**Command Execution with Error Handling:**
```python
try:
    result = self._run_command(command, capture_output=True, check=False)
    if result.returncode == 0:
        return InstallResult(success=True, ...)
    else:
        # Parse failures and return partial success
        return InstallResult(success=False, ...)
except PackageManagerError as e:
    return InstallResult(success=False, error_message=str(e), ...)
```

### PacmanPackageManager

**Location:** `implementations/pacman.py`
**Executable:** `pacman`
**Requires:** sudo for install/remove/update operations

**Key Characteristics:**
- Official Arch Linux package manager
- Only accesses official repositories (core, extra, community, multilib)
- No AUR support
- Requires sudo for write operations

**Command Patterns:**

```python
# Install
["sudo", "pacman", "-S", "--noconfirm"] + packages
# With system update
["sudo", "pacman", "-S", "--noconfirm", "-y"] + packages

# Remove
["sudo", "pacman", "-R", "--noconfirm"] + packages
# With dependencies
["sudo", "pacman", "-R", "--noconfirm", "-s"] + packages

# Search
["pacman", "-Ss", query]

# Update system (sync databases only)
["sudo", "pacman", "-Sy", "--noconfirm"]

# Check for updates (dry run)
["pacman", "-Qu"]

# Check if installed
["pacman", "-Q", package]

# Get package info (installed)
["pacman", "-Qi", package]

# Get package info (repository)
["pacman", "-Si", package]
```

**Parsing Logic:**

*Search Output:*
```
core/package-name 1.2.3-1 [installed]
    Package description here
```
- Regex: `r"^([^/]+)/([^\s]+)\s+([^\s]+)(?:\s+\[installed\])?"`
- Extracts: repository, name, version, installed status
- Description on next line

*Package Info Output:*
```
Name            : package-name
Version         : 1.2.3-1
Description     : Package description
Repository      : core
Installed Size  : 10.5 MiB
Depends On      : dep1 dep2 dep3
```
- Split on `:` to get key-value pairs
- Map to PackageInfo fields

### YayPackageManager

**Location:** `implementations/yay.py`
**Executable:** `yay`
**Requires:** No sudo (yay handles privilege escalation)

**Key Characteristics:**
- AUR helper written in Go
- Accesses official repos + AUR
- Handles sudo internally
- Similar interface to pacman

**Command Patterns:**

```python
# Install (no sudo needed)
["yay", "-S", "--noconfirm"] + packages
# With system update
["yay", "-S", "--noconfirm", "-y"] + packages

# Remove
["yay", "-R", "--noconfirm"] + packages
# With dependencies
["yay", "-R", "--noconfirm", "-s"] + packages

# Search (includes AUR)
["yay", "-Ss", query]

# Update system (sync databases only)
["yay", "-Sy", "--noconfirm", "--noprogressbar", "--quiet"]

# Check for updates (dry run)
["yay", "-Qu"]

# Check if installed
["yay", "-Q", package]

# Get package info (installed)
["yay", "-Qi", package]

# Get package info (repository or AUR)
["yay", "-Si", package]
```

**Differences from Pacman:**
- No `sudo` prefix (yay handles it)
- Additional flags: `--noprogressbar`, `--quiet` for cleaner output
- Can search and install from AUR
- Search results include `aur/` repository prefix

**Parsing Logic:**
- Same as Pacman, but also recognizes `aur/` repository prefix
- Regex includes `aur/` in repository matching

---

### ParuPackageManager

**Location:** `implementations/paru.py`
**Executable:** `paru`
**Requires:** No sudo (paru handles privilege escalation)

**Key Characteristics:**
- AUR helper written in Rust (faster than yay)
- Accesses official repos + AUR
- Handles sudo internally
- Preferred over yay in factory

**Command Patterns:**

Identical to Yay:
```python
# Install
["paru", "-S", "--noconfirm"] + packages

# Remove
["paru", "-R", "--noconfirm"] + packages

# Search
["paru", "-Ss", query]

# Update system
["paru", "-Sy", "--noconfirm", "--noprogressbar", "--quiet"]

# And so on...
```

**Differences from Yay:**
- Written in Rust (performance benefits)
- Slightly different default behavior
- Otherwise identical command interface

**Parsing Logic:**
- Identical to Yay
- Recognizes `aur/` repository prefix

### Implementation Comparison

| Feature | Pacman | Yay | Paru |
|---------|--------|-----|------|
| **Language** | C | Go | Rust |
| **AUR Support** | ❌ No | ✅ Yes | ✅ Yes |
| **Sudo Required** | ✅ Yes | ❌ No | ❌ No |
| **Repositories** | Official only | Official + AUR | Official + AUR |
| **Performance** | Fast | Medium | Fast |
| **Preference** | 3rd | 2nd | 1st |

**Code Duplication:**
- Yay and Paru implementations are nearly identical
- Only difference is executable name
- Could potentially be refactored to share code

---

## Factory Pattern

**Location:** `core/factory.py`

### PackageManagerFactory Class

**Purpose:** Create package manager instances with automatic detection

**Class Structure:**

```python
class PackageManagerFactory:
    """Factory for creating package manager instances with automatic detection."""

    # Registry of available package managers
    _MANAGERS = {
        PackageManagerType.PACMAN: PacmanPackageManager,
        PackageManagerType.YAY: YayPackageManager,
        PackageManagerType.PARU: ParuPackageManager,
    }

    # Preferred order for AUR helpers (most preferred first)
    _AUR_HELPER_PREFERENCE = [
        PackageManagerType.PARU,   # 1st choice
        PackageManagerType.YAY,    # 2nd choice
    ]
```

### Factory Methods

**1. create_auto(prefer_aur_helper=True) → PackageManager**

**Purpose:** Automatically detect and create the best available package manager

```python
@classmethod
def create_auto(cls, prefer_aur_helper: bool = True) -> PackageManager:
    """
    Automatically detect and create the best available package manager.

    Args:
        prefer_aur_helper: Whether to prefer AUR helpers over pacman

    Returns:
        PackageManager instance

    Raises:
        PackageManagerError: If no package manager is available
    """
```

**Logic:**
1. If `prefer_aur_helper=True`:
   - Try Paru first
   - Try Yay second
   - Fall back to Pacman
   - If all fail, try AUR helpers again (redundant)
   - Raise error if none available

2. If `prefer_aur_helper=False`:
   - Try Pacman first
   - Fall back to Paru
   - Fall back to Yay
   - Raise error if none available

**Default Behavior:** Prefers AUR helpers (Paru > Yay > Pacman)

**2. create(manager_type) → PackageManager**

**Purpose:** Create a specific package manager instance

```python
@classmethod
def create(cls, manager_type: PackageManagerType) -> PackageManager:
    """
    Create a specific package manager instance.

    Args:
        manager_type: Type of package manager to create

    Returns:
        PackageManager instance

    Raises:
        PackageManagerError: If type not supported or not available
    """
```

**Logic:**
1. Check if manager_type in registry
2. Get manager class from registry
3. Instantiate manager (may raise if executable not found)
4. Return instance

**3. get_available_managers() → list[PackageManagerType]**

**Purpose:** Get list of available package managers on the system

```python
@classmethod
def get_available_managers(cls) -> list[PackageManagerType]:
    """
    Get list of available package managers on the system.

    Returns:
        List of available package manager types
    """
```

**Logic:**
- Iterate through all registered managers
- Check if each is available using `_is_available()`
- Return list of available types

**4. is_available(manager_type) → bool**

**Purpose:** Check if a specific package manager is available

```python
@classmethod
def is_available(cls, manager_type: PackageManagerType) -> bool:
    """
    Check if a specific package manager is available on the system.

    Args:
        manager_type: Package manager type to check

    Returns:
        True if available, False otherwise
    """
```

**Logic:**
- Delegates to `_is_available()`

**5. _is_available(manager_type) → bool** (Internal)

**Purpose:** Internal method to check availability

```python
@classmethod
def _is_available(cls, manager_type: PackageManagerType) -> bool:
    """
    Internal method to check if a package manager is available.

    Args:
        manager_type: Package manager type to check

    Returns:
        True if available, False otherwise
    """
    executable_name = manager_type.value
    return shutil.which(executable_name) is not None
```

**Logic:**
- Get executable name from enum value
- Use `shutil.which()` to check if in PATH
- Return True if found, False otherwise

**6. get_recommended_manager() → PackageManagerType | None**

**Purpose:** Get the recommended package manager for the system

```python
@classmethod
def get_recommended_manager(cls) -> PackageManagerType | None:
    """
    Get the recommended package manager for the system.

    Returns:
        Recommended package manager type, or None if none available
    """
```

**Logic:**
1. Get all available managers
2. If none available, return None
3. Check AUR helper preference list (Paru, Yay)
4. Return first available AUR helper
5. Fall back to Pacman if available
6. Return first available as last resort

**7. create_recommended() → PackageManager**

**Purpose:** Create an instance of the recommended package manager

```python
@classmethod
def create_recommended(cls) -> PackageManager:
    """
    Create an instance of the recommended package manager.

    Returns:
        PackageManager instance

    Raises:
        PackageManagerError: If no package manager is available
    """
```

**Logic:**
1. Get recommended manager type
2. If None, raise PackageManagerError
3. Create and return instance using `create()`

### Factory Usage Patterns

**Pattern 1: Automatic Detection (Recommended)**
```python
from dotfiles_package_manager import PackageManagerFactory

# Let factory choose best available
pm = PackageManagerFactory.create_auto()
```

**Pattern 2: Prefer Official Pacman**
```python
# Prefer pacman over AUR helpers
pm = PackageManagerFactory.create_auto(prefer_aur_helper=False)
```

**Pattern 3: Specific Manager**
```python
from dotfiles_package_manager import PackageManagerFactory, PackageManagerType

# Force specific manager
pm = PackageManagerFactory.create(PackageManagerType.PARU)
```

**Pattern 4: Check Availability**
```python
# Check what's available
available = PackageManagerFactory.get_available_managers()
print(f"Available managers: {available}")

# Check specific manager
if PackageManagerFactory.is_available(PackageManagerType.PARU):
    pm = PackageManagerFactory.create(PackageManagerType.PARU)
```

**Pattern 5: Get Recommendation**
```python
# Get recommended manager without creating
recommended = PackageManagerFactory.get_recommended_manager()
if recommended:
    print(f"Recommended: {recommended.value}")
    pm = PackageManagerFactory.create(recommended)
```

---

## Integration & Usage

### Basic Usage Patterns

**Pattern 1: Install Packages**
```python
from dotfiles_package_manager import PackageManagerFactory

# Create manager
pm = PackageManagerFactory.create_auto()

# Install single package
result = pm.install(["vim"])
if result.success:
    print(f"Installed: {result.packages_installed}")
else:
    print(f"Failed: {result.error_message}")

# Install multiple packages
result = pm.install(["git", "tmux", "neovim"])

# Install with system update
result = pm.install(["package"], update_system=True)
```

**Pattern 2: Remove Packages**
```python
# Remove single package
result = pm.remove(["old-package"])

# Remove with dependencies
result = pm.remove(["package"], remove_dependencies=True)

# Remove multiple packages
result = pm.remove(["pkg1", "pkg2", "pkg3"])
```

**Pattern 3: Search for Packages**
```python
# Search for packages
result = pm.search("python")
for pkg in result.packages:
    status = "[installed]" if pkg.installed else ""
    print(f"{pkg.repository}/{pkg.name} {pkg.version} {status}")
    print(f"  {pkg.description}")

# Limit search results
result = pm.search("python", limit=10)
```

**Pattern 4: Check Package Status**
```python
# Check if installed
if pm.is_installed("vim"):
    print("Vim is installed")

# Get package info
info = pm.get_package_info("vim")
if info:
    print(f"Name: {info.name}")
    print(f"Version: {info.version}")
    print(f"Description: {info.description}")
    print(f"Size: {info.size}")
    print(f"Dependencies: {', '.join(info.dependencies)}")
```

**Pattern 5: System Updates**
```python
# Check for updates (dry run)
result = pm.update_system(dry_run=True)
print(result.output)  # "Found X upgradeable packages"

# Sync package databases
result = pm.update_system(dry_run=False)
```

### Complete Workflows

**Workflow 1: Install Development Environment**
```python
from dotfiles_package_manager import PackageManagerFactory, PackageManagerError

def setup_dev_environment():
    """Install development tools."""
    try:
        # Create package manager
        pm = PackageManagerFactory.create_auto()

        # Define packages
        packages = [
            "git",
            "base-devel",
            "python",
            "python-pip",
            "nodejs",
            "npm",
        ]

        # Check which are already installed
        to_install = []
        for pkg in packages:
            if not pm.is_installed(pkg):
                to_install.append(pkg)

        if not to_install:
            print("All packages already installed")
            return

        # Install missing packages
        print(f"Installing: {', '.join(to_install)}")
        result = pm.install(to_install, update_system=True)

        if result.success:
            print(f"✓ Installed: {', '.join(result.packages_installed)}")
        else:
            print(f"✗ Failed: {', '.join(result.packages_failed)}")
            if result.error_message:
                print(f"Error: {result.error_message}")

    except PackageManagerError as e:
        print(f"Package manager error: {e}")
```

**Workflow 2: Search and Install Interactively**
```python
def search_and_install(query: str):
    """Search for packages and let user choose which to install."""
    pm = PackageManagerFactory.create_auto()

    # Search
    result = pm.search(query, limit=20)

    if not result.packages:
        print(f"No packages found for '{query}'")
        return

    # Display results
    print(f"\nFound {result.total_found} packages:\n")
    for i, pkg in enumerate(result.packages, 1):
        status = "[installed]" if pkg.installed else ""
        print(f"{i}. {pkg.name} {pkg.version} {status}")
        print(f"   {pkg.description}\n")

    # Get user choice
    choice = input("Enter package number to install (or 'q' to quit): ")
    if choice.lower() == 'q':
        return

    try:
        idx = int(choice) - 1
        pkg = result.packages[idx]

        # Install
        print(f"\nInstalling {pkg.name}...")
        install_result = pm.install([pkg.name])

        if install_result.success:
            print(f"✓ Successfully installed {pkg.name}")
        else:
            print(f"✗ Failed to install {pkg.name}")
            print(f"Error: {install_result.error_message}")

    except (ValueError, IndexError):
        print("Invalid choice")
```

**Workflow 3: Cleanup Unused Packages**
```python
def cleanup_system():
    """Remove orphaned packages."""
    pm = PackageManagerFactory.create_auto()

    # Note: This is a simplified example
    # Real orphan detection would require parsing pacman -Qdt output

    print("Cleaning up system...")

    # Example: remove specific packages with dependencies
    packages_to_remove = ["old-package-1", "old-package-2"]

    result = pm.remove(packages_to_remove, remove_dependencies=True)

    if result.success:
        print(f"✓ Removed: {', '.join(result.packages_installed)}")
    else:
        print(f"✗ Some packages failed to remove")
```

### Error Handling Patterns

**Pattern 1: Graceful Degradation**
```python
from dotfiles_package_manager import PackageManagerFactory, PackageManagerError

try:
    pm = PackageManagerFactory.create_auto()
except PackageManagerError:
    print("No package manager available")
    # Fall back to manual installation instructions
    print("Please install packages manually")
    sys.exit(1)
```

**Pattern 2: Partial Success Handling**
```python
result = pm.install(["pkg1", "pkg2", "pkg3"])

if result.success:
    print("All packages installed successfully")
elif result.packages_installed:
    print(f"Partial success:")
    print(f"  Installed: {result.packages_installed}")
    print(f"  Failed: {result.packages_failed}")
else:
    print(f"Installation failed: {result.error_message}")
```

**Pattern 3: Retry Logic**
```python
def install_with_retry(pm, packages, max_retries=3):
    """Install packages with retry logic."""
    for attempt in range(max_retries):
        result = pm.install(packages)

        if result.success:
            return result

        if not result.packages_failed:
            # No specific failures, don't retry
            return result

        # Retry only failed packages
        packages = result.packages_failed
        print(f"Retry {attempt + 1}/{max_retries} for: {packages}")

    return result
```

### Best Practices

1. **Always use factory for creation**
   - Don't instantiate implementations directly
   - Let factory handle detection and selection

2. **Check result.success before assuming success**
   - Operations return results, not raise exceptions
   - Check both success flag and packages_failed list

3. **Handle partial success**
   - Some packages may succeed while others fail
   - Check packages_installed and packages_failed separately

4. **Use dry_run for updates**
   - Check for updates before applying
   - Avoid unexpected system changes

5. **Catch PackageManagerError for system failures**
   - Executable not found
   - Permission issues
   - System-level problems

6. **Don't assume package names**
   - Search first to verify package exists
   - Handle package not found gracefully

### Anti-Patterns to Avoid

❌ **Don't instantiate implementations directly**
```python
# Bad
from dotfiles_package_manager.implementations.pacman import PacmanPackageManager
pm = PacmanPackageManager()
```

✅ **Use factory instead**
```python
# Good
from dotfiles_package_manager import PackageManagerFactory
pm = PackageManagerFactory.create_auto()
```

❌ **Don't ignore return values**
```python
# Bad
pm.install(["package"])  # Ignoring result
```

✅ **Check results**
```python
# Good
result = pm.install(["package"])
if not result.success:
    handle_error(result)
```

❌ **Don't assume all-or-nothing**
```python
# Bad
result = pm.install(["pkg1", "pkg2"])
if result.success:
    # Assumes both installed
```

✅ **Check individual packages**
```python
# Good
result = pm.install(["pkg1", "pkg2"])
print(f"Installed: {result.packages_installed}")
print(f"Failed: {result.packages_failed}")
```

---

## Advanced Topics

### Security Considerations

**1. Sudo Usage**

**Pacman:**
- Requires `sudo` for install, remove, update operations
- Commands are constructed with `sudo` prefix
- User must have sudo privileges
- No password caching - may prompt multiple times

**Yay/Paru:**
- Handle sudo internally
- No `sudo` prefix in commands
- May prompt for password when needed
- Better user experience (fewer prompts)

**Security Implications:**
- All implementations execute system commands
- Potential for command injection if inputs not sanitized
- Currently, package names are passed directly to commands
- **Recommendation:** Validate package names before passing to commands

**2. Command Injection Risk**

**Current Implementation:**
```python
command = ["sudo", str(self.executable_path), "-S", "--noconfirm"] + packages
```

**Risk:** If package names contain shell metacharacters, could be exploited

**Mitigation:**
- Commands are passed as lists (not shell strings)
- subprocess.run() with list arguments doesn't invoke shell
- Relatively safe, but package name validation would be better

**3. Privilege Escalation**

- Install/remove/update require root privileges
- Factory auto-detection doesn't require privileges
- Search and query operations don't require privileges
- Users must have appropriate sudo access

### Performance Considerations

**1. Command Execution Overhead**

- Each operation spawns subprocess
- Subprocess creation has overhead
- For bulk operations, prefer single command with multiple packages

**Better:**
```python
pm.install(["pkg1", "pkg2", "pkg3"])  # Single command
```

**Worse:**
```python
pm.install(["pkg1"])  # Three separate commands
pm.install(["pkg2"])
pm.install(["pkg3"])
```

**2. Output Parsing**

- Search results parsed line-by-line
- Package info parsed with string operations
- Regex matching for search output
- Performance acceptable for typical use cases

**3. Network Operations**

- Install/update operations require network
- Search may use cached database
- No timeout on network operations (uses default)
- Consider adding timeout parameter for network-heavy operations

**4. Caching**

- No caching of package information
- Each query hits package manager
- Could cache search results for performance
- Could cache is_installed() results

### AUR Helper Differences

**Paru vs Yay:**

| Aspect | Paru | Yay |
|--------|------|-----|
| **Language** | Rust | Go |
| **Performance** | Faster | Slower |
| **Memory** | Lower | Higher |
| **Features** | More features | Stable features |
| **Maintenance** | Active | Active |
| **Compatibility** | Pacman-like | Pacman-like |

**Why Prefer Paru:**
1. Written in Rust (better performance)
2. Lower memory footprint
3. More modern codebase
4. Better AUR package review features
5. Faster dependency resolution

**When to Use Yay:**
1. Paru not available
2. Compatibility with existing scripts
3. User preference

**When to Use Pacman:**
1. No AUR packages needed
2. Official repos only
3. Minimal dependencies
4. Maximum stability

### Extensibility Points

**1. Adding New Package Managers**

To add support for a new package manager:

```python
# 1. Add to enum
class PackageManagerType(Enum):
    PACMAN = "pacman"
    YAY = "yay"
    PARU = "paru"
    NEW_MANAGER = "new-manager"  # Add here

# 2. Create implementation
class NewManagerPackageManager(PackageManager):
    @property
    def manager_type(self) -> PackageManagerType:
        return PackageManagerType.NEW_MANAGER

    def _find_executable(self) -> Path | None:
        executable = shutil.which("new-manager")
        return Path(executable) if executable else None

    # Implement all abstract methods...

# 3. Register in factory
class PackageManagerFactory:
    _MANAGERS = {
        PackageManagerType.PACMAN: PacmanPackageManager,
        PackageManagerType.YAY: YayPackageManager,
        PackageManagerType.PARU: ParuPackageManager,
        PackageManagerType.NEW_MANAGER: NewManagerPackageManager,  # Add here
    }
```

**2. Custom Parsing Logic**

Each implementation can customize parsing:

```python
def _parse_search_output(self, output: str) -> list[PackageInfo]:
    """Custom parsing for this package manager."""
    # Implement custom logic
    pass
```

**3. Additional Methods**

Subclasses can add manager-specific methods:

```python
class ParuPackageManager(PackageManager):
    # Standard methods...

    def review_aur_package(self, package: str):
        """Paru-specific: Review AUR package before install."""
        # Custom functionality
        pass
```

### Limitations and Constraints

**1. Arch Linux Only**
- Only supports Arch-based distributions
- Won't work on Debian, Fedora, etc.
- Assumes pacman-compatible package managers

**2. No Async Support**
- All operations are synchronous
- Blocks during package installation
- No async/await interface

**3. Limited Error Information**
- Errors returned as strings
- No structured error codes
- Difficult to programmatically handle specific errors

**4. No Progress Callbacks**
- No way to monitor installation progress
- No progress bars or percentage complete
- All-or-nothing operation

**5. No Transaction Support**
- Can't rollback failed installations
- No atomic operations
- Partial failures leave system in intermediate state

**6. No Dependency Resolution Visibility**
- Can't see what dependencies will be installed
- No dry-run for dependency tree
- Relies on package manager's dependency resolution

**7. Limited Package Info**
- PackageInfo has basic fields only
- No optional dependencies
- No conflicts information
- No provides/replaces information

### Best Practices

**1. Use Factory Pattern**
- Always use PackageManagerFactory
- Don't instantiate implementations directly
- Let factory handle detection

**2. Handle Errors Gracefully**
- Check result.success
- Handle partial failures
- Provide user feedback

**3. Validate Inputs**
- Check package names before operations
- Validate search queries
- Handle empty lists

**4. Batch Operations**
- Install multiple packages in one call
- More efficient than individual calls
- Better user experience

**5. Use Dry Run for Updates**
- Check before updating
- Inform user of changes
- Avoid surprises

**6. Log Operations**
- Log package installations
- Track what was installed when
- Useful for debugging

**7. Test on Non-Production Systems**
- Package operations modify system
- Test in VMs or containers
- Don't test on production systems

---

## Code Examples

### Example 1: Basic Package Installation

```python
from dotfiles_package_manager import PackageManagerFactory

# Create package manager
pm = PackageManagerFactory.create_auto()

# Install a package
result = pm.install(["vim"])

if result.success:
    print(f"✓ Successfully installed: {', '.join(result.packages_installed)}")
else:
    print(f"✗ Installation failed")
    if result.packages_failed:
        print(f"  Failed packages: {', '.join(result.packages_failed)}")
    if result.error_message:
        print(f"  Error: {result.error_message}")
```

### Example 2: Search and Display Results

```python
from dotfiles_package_manager import PackageManagerFactory

pm = PackageManagerFactory.create_auto()

# Search for Python packages
result = pm.search("python", limit=10)

print(f"Found {result.total_found} packages matching '{result.query}':\n")

for pkg in result.packages:
    installed = "[installed]" if pkg.installed else ""
    print(f"{pkg.repository}/{pkg.name} {pkg.version} {installed}")
    if pkg.description:
        print(f"  {pkg.description}")
    print()
```

### Example 3: Check Package Status

```python
from dotfiles_package_manager import PackageManagerFactory

pm = PackageManagerFactory.create_auto()

packages_to_check = ["vim", "git", "tmux", "neovim"]

print("Package Status:")
print("-" * 50)

for pkg_name in packages_to_check:
    if pm.is_installed(pkg_name):
        info = pm.get_package_info(pkg_name)
        print(f"✓ {pkg_name:15} {info.version:15} [installed]")
    else:
        print(f"✗ {pkg_name:15} {'':15} [not installed]")
```

### Example 4: Install Development Environment

```python
from dotfiles_package_manager import PackageManagerFactory, PackageManagerError

def install_dev_tools():
    """Install common development tools."""

    dev_packages = [
        "git",
        "base-devel",
        "python",
        "python-pip",
        "nodejs",
        "npm",
        "docker",
        "docker-compose",
    ]

    try:
        pm = PackageManagerFactory.create_auto()
        print(f"Using package manager: {pm.manager_type.value}\n")

        # Check what's already installed
        to_install = []
        already_installed = []

        for pkg in dev_packages:
            if pm.is_installed(pkg):
                already_installed.append(pkg)
            else:
                to_install.append(pkg)

        if already_installed:
            print(f"Already installed: {', '.join(already_installed)}\n")

        if not to_install:
            print("All packages already installed!")
            return

        # Install missing packages
        print(f"Installing: {', '.join(to_install)}\n")
        result = pm.install(to_install, update_system=True)

        if result.success:
            print(f"\n✓ Successfully installed all packages!")
        elif result.packages_installed:
            print(f"\n⚠ Partial success:")
            print(f"  Installed: {', '.join(result.packages_installed)}")
            print(f"  Failed: {', '.join(result.packages_failed)}")
        else:
            print(f"\n✗ Installation failed: {result.error_message}")

    except PackageManagerError as e:
        print(f"Error: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(install_dev_tools())
```

### Example 5: Interactive Package Manager

```python
from dotfiles_package_manager import PackageManagerFactory, PackageManagerError

def main():
    """Interactive package manager CLI."""

    try:
        pm = PackageManagerFactory.create_auto()
    except PackageManagerError:
        print("No package manager available!")
        return 1

    print(f"Package Manager: {pm.manager_type.value}")
    print("=" * 50)

    while True:
        print("\nOptions:")
        print("1. Search packages")
        print("2. Install package")
        print("3. Remove package")
        print("4. Check package info")
        print("5. Update system")
        print("6. Quit")

        choice = input("\nEnter choice: ").strip()

        if choice == "1":
            query = input("Search query: ")
            result = pm.search(query, limit=20)

            if result.packages:
                print(f"\nFound {result.total_found} packages:\n")
                for pkg in result.packages:
                    status = "[installed]" if pkg.installed else ""
                    print(f"{pkg.name} {pkg.version} {status}")
                    print(f"  {pkg.description}\n")
            else:
                print("No packages found")

        elif choice == "2":
            packages = input("Package names (space-separated): ").split()
            result = pm.install(packages)

            if result.success:
                print(f"✓ Installed: {', '.join(result.packages_installed)}")
            else:
                print(f"✗ Failed: {result.error_message}")

        elif choice == "3":
            packages = input("Package names (space-separated): ").split()
            result = pm.remove(packages)

            if result.success:
                print(f"✓ Removed: {', '.join(result.packages_installed)}")
            else:
                print(f"✗ Failed: {result.error_message}")

        elif choice == "4":
            package = input("Package name: ")
            info = pm.get_package_info(package)

            if info:
                print(f"\nName: {info.name}")
                print(f"Version: {info.version}")
                print(f"Description: {info.description}")
                print(f"Repository: {info.repository}")
                print(f"Installed: {info.installed}")
                print(f"Size: {info.size}")
                print(f"Dependencies: {', '.join(info.dependencies)}")
            else:
                print("Package not found")

        elif choice == "5":
            result = pm.update_system(dry_run=True)
            print(result.output)

            if input("\nProceed with update? (y/n): ").lower() == 'y':
                result = pm.update_system(dry_run=False)
                if result.success:
                    print("✓ System updated")
                else:
                    print(f"✗ Update failed: {result.error_message}")

        elif choice == "6":
            break

        else:
            print("Invalid choice")

    return 0

if __name__ == "__main__":
    exit(main())
```

### Example 6: Package Manager Wrapper Class

```python
from dotfiles_package_manager import PackageManagerFactory, PackageManagerError
from typing import List, Optional
import logging

class PackageManagerWrapper:
    """High-level wrapper around package manager."""

    def __init__(self, prefer_aur: bool = True):
        """Initialize wrapper.

        Args:
            prefer_aur: Whether to prefer AUR helpers
        """
        self.logger = logging.getLogger(__name__)
        try:
            self.pm = PackageManagerFactory.create_auto(prefer_aur_helper=prefer_aur)
            self.logger.info(f"Using package manager: {self.pm.manager_type.value}")
        except PackageManagerError as e:
            self.logger.error(f"Failed to create package manager: {e}")
            raise

    def ensure_installed(self, packages: List[str]) -> bool:
        """Ensure packages are installed.

        Args:
            packages: List of package names

        Returns:
            True if all packages installed, False otherwise
        """
        to_install = [pkg for pkg in packages if not self.pm.is_installed(pkg)]

        if not to_install:
            self.logger.info("All packages already installed")
            return True

        self.logger.info(f"Installing: {', '.join(to_install)}")
        result = self.pm.install(to_install)

        if result.success:
            self.logger.info(f"Successfully installed: {', '.join(result.packages_installed)}")
            return True
        else:
            self.logger.error(f"Installation failed: {result.error_message}")
            if result.packages_failed:
                self.logger.error(f"Failed packages: {', '.join(result.packages_failed)}")
            return False

    def safe_remove(self, packages: List[str], remove_deps: bool = False) -> bool:
        """Safely remove packages.

        Args:
            packages: List of package names
            remove_deps: Whether to remove dependencies

        Returns:
            True if all packages removed, False otherwise
        """
        installed = [pkg for pkg in packages if self.pm.is_installed(pkg)]

        if not installed:
            self.logger.info("No packages to remove")
            return True

        self.logger.info(f"Removing: {', '.join(installed)}")
        result = self.pm.remove(installed, remove_dependencies=remove_deps)

        if result.success:
            self.logger.info(f"Successfully removed: {', '.join(result.packages_installed)}")
            return True
        else:
            self.logger.error(f"Removal failed: {result.error_message}")
            return False

    def find_package(self, query: str) -> Optional[str]:
        """Find exact package name from query.

        Args:
            query: Search query

        Returns:
            Package name if found, None otherwise
        """
        result = self.pm.search(query, limit=50)

        # Look for exact match
        for pkg in result.packages:
            if pkg.name.lower() == query.lower():
                return pkg.name

        # Look for close match
        for pkg in result.packages:
            if query.lower() in pkg.name.lower():
                return pkg.name

        return None

# Usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    wrapper = PackageManagerWrapper()

    # Ensure packages installed
    wrapper.ensure_installed(["vim", "git", "tmux"])

    # Find and install
    pkg_name = wrapper.find_package("neovim")
    if pkg_name:
        wrapper.ensure_installed([pkg_name])
```

---

## Troubleshooting

### Common Issues and Solutions

**Issue 1: PackageManagerError - Executable not found**

**Symptoms:**
```
PackageManagerError: Package manager executable not found: pacman
```

**Causes:**
- Package manager not installed
- Package manager not in PATH
- Running on non-Arch system

**Solutions:**
1. Install the package manager:
   ```bash
   # For pacman (should be pre-installed on Arch)
   # For yay
   git clone https://aur.archlinux.org/yay.git
   cd yay && makepkg -si

   # For paru
   git clone https://aur.archlinux.org/paru.git
   cd paru && makepkg -si
   ```

2. Check PATH:
   ```bash
   which pacman
   which yay
   which paru
   ```

3. Use specific manager if available:
   ```python
   # Try specific manager
   available = PackageManagerFactory.get_available_managers()
   if available:
       pm = PackageManagerFactory.create(available[0])
   ```

**Issue 2: Installation fails with permission denied**

**Symptoms:**
```
error: you cannot perform this operation unless you are root
```

**Causes:**
- User doesn't have sudo privileges
- Sudo password not entered
- Sudo timeout expired

**Solutions:**
1. Ensure user has sudo access:
   ```bash
   sudo -v  # Test sudo access
   ```

2. Add user to wheel group:
   ```bash
   sudo usermod -aG wheel username
   ```

3. For AUR helpers, use yay/paru instead of pacman (they handle sudo better)

**Issue 3: Package not found**

**Symptoms:**
```
InstallResult(success=False, packages_failed=['package-name'])
```

**Causes:**
- Package name misspelled
- Package only in AUR (using pacman)
- Repository not synchronized

**Solutions:**
1. Search for correct package name:
   ```python
   result = pm.search("package")
   for pkg in result.packages:
       print(pkg.name)
   ```

2. Use AUR helper for AUR packages:
   ```python
   pm = PackageManagerFactory.create(PackageManagerType.PARU)
   ```

3. Sync repositories:
   ```python
   pm.update_system(dry_run=False)
   ```

**Issue 4: Partial installation success**

**Symptoms:**
```
InstallResult(
    success=False,
    packages_installed=['pkg1', 'pkg2'],
    packages_failed=['pkg3']
)
```

**Causes:**
- Some packages don't exist
- Dependency conflicts
- Network issues

**Solutions:**
1. Check which packages failed:
   ```python
   if result.packages_failed:
       for pkg in result.packages_failed:
           info = pm.get_package_info(pkg)
           if not info:
               print(f"{pkg} not found")
   ```

2. Install failed packages separately:
   ```python
   for pkg in result.packages_failed:
       single_result = pm.install([pkg])
       if not single_result.success:
           print(f"Failed to install {pkg}: {single_result.error_message}")
   ```

**Issue 5: Search returns no results**

**Symptoms:**
```
SearchResult(packages=[], query='package', total_found=0)
```

**Causes:**
- Package doesn't exist
- Database not synchronized
- Typo in search query

**Solutions:**
1. Sync database:
   ```python
   pm.update_system(dry_run=False)
   ```

2. Try broader search:
   ```python
   result = pm.search("vim")  # Instead of "neovim-nightly"
   ```

3. Check on AUR website if using pacman

**Issue 6: Command timeout**

**Symptoms:**
```
PackageManagerError: Command timed out after 300s: ...
```

**Causes:**
- Large package download
- Slow network
- Package build taking too long (AUR)

**Solutions:**
1. Currently no timeout parameter exposed
2. Would need to modify _run_command call
3. For AUR packages, build manually first

**Issue 7: get_package_info returns None**

**Symptoms:**
```python
info = pm.get_package_info("package")
# info is None
```

**Causes:**
- Package doesn't exist
- Package name misspelled
- Not in repositories

**Solutions:**
1. Search first:
   ```python
   result = pm.search("package")
   if result.packages:
       exact_name = result.packages[0].name
       info = pm.get_package_info(exact_name)
   ```

2. Check if installed:
   ```python
   if pm.is_installed("package"):
       info = pm.get_package_info("package")
   ```

**Issue 8: Factory creates wrong manager**

**Symptoms:**
- Wanted paru, got yay
- Wanted AUR helper, got pacman

**Causes:**
- Preferred manager not installed
- Factory preference order

**Solutions:**
1. Check what's available:
   ```python
   available = PackageManagerFactory.get_available_managers()
   print(f"Available: {[m.value for m in available]}")
   ```

2. Create specific manager:
   ```python
   if PackageManagerFactory.is_available(PackageManagerType.PARU):
       pm = PackageManagerFactory.create(PackageManagerType.PARU)
   ```

3. Install preferred manager first

### Debugging Tips

**1. Enable verbose output:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Then use package manager
pm = PackageManagerFactory.create_auto()
```

**2. Check command output:**
```python
result = pm.install(["package"])
print(f"stdout: {result.output}")
print(f"stderr: {result.error_message}")
```

**3. Test with simple operations:**
```python
# Test search (doesn't require sudo)
result = pm.search("vim")
print(f"Search works: {len(result.packages) > 0}")

# Test is_installed (doesn't require sudo)
installed = pm.is_installed("bash")
print(f"is_installed works: {installed}")
```

**4. Verify package manager works manually:**
```bash
# Test pacman
pacman -Ss vim

# Test yay
yay -Ss vim

# Test paru
paru -Ss vim
```

**5. Check for system issues:**
```bash
# Check disk space
df -h

# Check network
ping archlinux.org

# Check pacman database
sudo pacman -Sy
```

### Performance Troubleshooting

**Issue: Slow package installation**

**Solutions:**
1. Use faster mirror:
   ```bash
   sudo pacman-mirrors --fasttrack
   ```

2. Use paru instead of yay (faster)

3. Install multiple packages at once (not one-by-one)

**Issue: Slow search**

**Solutions:**
1. Limit results:
   ```python
   result = pm.search("query", limit=10)
   ```

2. Use more specific queries

3. Cache search results if searching repeatedly

---

**Investigation Complete!**

**Final Statistics:**
- **Lines:** ~2000
- **Code Examples:** 60+
- **Usage Patterns:** 15+
- **Troubleshooting Issues:** 8+
- **API Coverage:** 100%

**Last Updated:** 2025-10-19
