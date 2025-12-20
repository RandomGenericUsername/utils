# Package Manager Module - Overview

**Module:** `dotfiles_package_manager`
**Version:** 0.2.0
**Python:** >=3.12
**Platform:** Linux (Arch, Debian, RedHat families)

---

## Introduction

The `package_manager` module provides a unified, Pythonic interface for managing packages across multiple Linux distributions. It abstracts the differences between package managers (pacman, apt, dnf) and their variants, allowing you to write distribution-agnostic code.

### Key Features

- **Multi-Distribution Support** - Works on Arch, Debian, and RedHat-based systems
- **Unified Interface** - Single API for all package managers
- **Automatic Detection** - Detects distribution and selects best available manager
- **Third-Party Repos** - Seamless access to AUR (Arch), PPAs (Debian), COPR (RedHat)
- **Type-Safe** - Full type hints and dataclass-based results
- **No Dependencies** - Pure Python using only stdlib
- **Error Handling** - Graceful error handling with detailed results
- **Arch Safety** - Prevents partial upgrades on Arch Linux (see [Arch Partial Upgrades](arch-partial-upgrades.md))

---

## Quick Start

### Installation

The module is a standalone uv project. To use it in your project:

```bash
# Add as dependency in your pyproject.toml
uv add dotfiles-package-manager
```

### Basic Usage

```python
from dotfiles_package_manager import PackageManagerFactory

# Create package manager (auto-detects best available)
pm = PackageManagerFactory.create_auto()

# Install packages
result = pm.install(["vim", "git", "tmux"])
if result.success:
    print(f"Installed: {', '.join(result.packages_installed)}")

# Search for packages
result = pm.search("python")
for pkg in result.packages:
    print(f"{pkg.name} - {pkg.description}")

# Check if installed
if pm.is_installed("vim"):
    print("Vim is installed!")

# Get package info
info = pm.get_package_info("vim")
print(f"{info.name} {info.version}")
```

---

## Architecture

### Module Structure

```
dotfiles_package_manager/
├── core/                    # Core abstractions
│   ├── base.py             # Abstract base class & exceptions
│   ├── types.py            # Data types (enums, dataclasses)
│   └── factory.py          # Factory for auto-detection
└── implementations/         # Concrete implementations
    ├── pacman.py           # Pacman (official)
    ├── yay.py              # Yay AUR helper
    └── paru.py             # Paru AUR helper
```

### Design Patterns

1. **Abstract Factory** - `PackageManagerFactory` creates appropriate manager instances
2. **Template Method** - Base class provides common functionality, subclasses implement specifics
3. **Strategy** - Different package managers are interchangeable strategies
4. **Registry** - Factory maintains registry of available managers

### Layered Architecture

```
Public API Layer
    ↓
Factory Layer (auto-detection, creation)
    ↓
Abstraction Layer (base class, types)
    ↓
Implementation Layer (pacman, yay, paru)
```

---

## Supported Package Managers

### Pacman

- **Type:** Official Arch Linux package manager
- **Repositories:** core, extra, community, multilib
- **AUR Support:** ❌ No
- **Sudo Required:** ✅ Yes
- **When to Use:** Official packages only, maximum stability

### Yay

- **Type:** AUR helper (written in Go)
- **Repositories:** Official + AUR
- **AUR Support:** ✅ Yes
- **Sudo Required:** ❌ No (handles internally)
- **When to Use:** Need AUR packages, yay already installed

### Paru

- **Type:** AUR helper (written in Rust)
- **Repositories:** Official + AUR
- **AUR Support:** ✅ Yes
- **Sudo Required:** ❌ No (handles internally)
- **When to Use:** Need AUR packages, prefer performance (recommended)

### Preference Order

By default, the factory prefers: **Paru > Yay > Pacman**

This can be customized:

```python
# Prefer official pacman
pm = PackageManagerFactory.create_auto(prefer_aur_helper=False)

# Force specific manager
pm = PackageManagerFactory.create(PackageManagerType.PARU)
```

---

## Core Concepts

### PackageManager (Abstract Base Class)

All package managers implement this interface:

- `install(packages, update_system)` - Install packages
- `remove(packages, remove_dependencies)` - Remove packages
- `search(query, limit)` - Search for packages
- `update_system(dry_run)` - Update system packages
- `is_installed(package)` - Check if package is installed
- `get_package_info(package)` - Get detailed package information

### Result Types

**InstallResult** - Returned by install/remove/update operations
- `success: bool` - Overall success
- `packages_installed: list[str]` - Successfully processed packages
- `packages_failed: list[str]` - Failed packages
- `output: str` - Command output
- `error_message: str | None` - Error message if failed

**SearchResult** - Returned by search operations
- `packages: list[PackageInfo]` - Found packages
- `query: str` - Original search query
- `total_found: int` - Total number found

**PackageInfo** - Package information
- `name: str` - Package name
- `version: str | None` - Version
- `description: str | None` - Description
- `repository: str | None` - Repository (core, extra, aur, etc.)
- `installed: bool` - Installation status
- `size: str | None` - Package size
- `dependencies: list[str]` - Dependencies

---

## Common Use Cases

### 1. Install Development Environment

```python
pm = PackageManagerFactory.create_auto()
dev_tools = ["git", "base-devel", "python", "nodejs"]
result = pm.install(dev_tools, update_system=True)
```

### 2. Search and Install Interactively

```python
result = pm.search("editor")
for i, pkg in enumerate(result.packages):
    print(f"{i+1}. {pkg.name} - {pkg.description}")
# User selects, then install
```

### 3. Check and Install Missing Packages

```python
required = ["vim", "git", "tmux"]
to_install = [pkg for pkg in required if not pm.is_installed(pkg)]
if to_install:
    pm.install(to_install)
```

### 4. System Maintenance

```python
# Check for updates
result = pm.update_system(dry_run=True)
print(result.output)  # "Found X upgradeable packages"

# Sync databases
pm.update_system(dry_run=False)
```

---

## Error Handling

### Exceptions vs. Results

**Exceptions (PackageManagerError):**
- Raised for system-level failures
- Executable not found
- Permission denied
- Command timeout

**Results (success=False):**
- Returned for package-level failures
- Package not found
- Installation failed
- Partial success scenarios

### Example

```python
from dotfiles_package_manager import PackageManagerFactory, PackageManagerError

try:
    pm = PackageManagerFactory.create_auto()
except PackageManagerError as e:
    print(f"No package manager available: {e}")
    exit(1)

# Package-level errors don't raise exceptions
result = pm.install(["nonexistent-package"])
if not result.success:
    print(f"Failed: {result.error_message}")
    print(f"Failed packages: {result.packages_failed}")
```

---

## Best Practices

1. **Use Factory** - Always use `PackageManagerFactory`, don't instantiate implementations directly
2. **Check Results** - Always check `result.success` before assuming success
3. **Handle Partial Success** - Check both `packages_installed` and `packages_failed`
4. **Batch Operations** - Install multiple packages in one call for efficiency
5. **Use Dry Run** - Check for updates before applying with `dry_run=True`
6. **Validate Inputs** - Search for packages before installing to verify they exist

---

## Limitations

- **Arch Linux Only** - Only works on Arch-based distributions
- **Synchronous** - All operations block until complete
- **No Progress Callbacks** - Can't monitor installation progress
- **No Transactions** - Can't rollback failed installations
- **Basic Package Info** - Limited metadata compared to full pacman output

---

## Next Steps

- **[Architecture](architecture.md)** - Detailed architecture and design patterns
- **[API Reference](api_reference.md)** - Complete API documentation
- **[Usage Guide](usage_guide.md)** - Comprehensive usage patterns
- **[Examples](examples.md)** - Complete code examples
- **[Troubleshooting](troubleshooting.md)** - Common issues and solutions

---

**Module:** `dotfiles_package_manager`
**Documentation Version:** 1.0
**Last Updated:** 2025-10-19
