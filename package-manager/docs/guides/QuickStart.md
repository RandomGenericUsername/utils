# Quick Start Guide

## Purpose

Get started with dotfiles-package-manager in 5 minutes. This guide covers the most common usage pattern.

---

## Installation

```bash
pip install dotfiles-package-manager
```

Or with uv:

```bash
uv add dotfiles-package-manager
```

---

## Basic Usage Pattern

The most common usage pattern (verified from production usage in dotfiles-installer):

```python
from dotfiles_package_manager import PackageManagerFactory

# 1. Create package manager (auto-detects your system)
pm = PackageManagerFactory.create_auto()

# 2. Update system packages
result = pm.update_system()
if not result.success:
    print(f"Update failed: {result.error_message}")

# 3. Install packages
result = pm.install(["vim", "git", "curl"])
print(f"Installed: {result.packages_installed}")
print(f"Failed: {result.packages_failed}")
```

**Evidence**: This pattern is used in production. See `tests/contract/test_cross_manager_install_contract.py` for verified behavior.

---

## Understanding Results

All operations return `InstallResult`:

```python
result = pm.install(["vim", "nonexistent-package"])

# Check overall success
if result.success:
    print("At least one package succeeded!")

# See what worked
print(f"Installed: {result.packages_installed}")  # ["vim"]

# See what failed
print(f"Failed: {result.packages_failed}")  # ["nonexistent-package"]

# Get full output
print(result.output)

# Get error message (if any)
if result.error_message:
    print(f"Error: {result.error_message}")
```

**Important**: `success=True` means **at least one package succeeded**. This is intentional for pipeline-based workflows.

**Evidence**: `tests/characterization/test_characterization__partial_install_success.py` (15 tests)

---

## Auto-Detection

`create_auto()` detects your Linux distribution and picks the best available package manager:

| Distribution | Default Manager | With `prefer_third_party=True` |
|--------------|-----------------|-------------------------------|
| Arch Linux | pacman | paru → yay → pacman |
| Debian/Ubuntu | apt | apt |
| Fedora/RHEL | dnf | dnf |

```python
# Prefer AUR helpers on Arch (default)
pm = PackageManagerFactory.create_auto(prefer_third_party=True)

# Use only official repos on Arch
pm = PackageManagerFactory.create_auto(prefer_third_party=False)
```

**Evidence**: `tests/contract/test_factory_contracts.py::TestFactoryCreateAutoContract` (5 tests)

---

## Checking Package Status

```python
# Check if a package is installed
if pm.is_installed("vim"):
    print("vim is installed!")

# Get package information
info = pm.get_package_info("vim")
if info:
    print(f"Version: {info.version}")
    print(f"Description: {info.description}")
else:
    print("Package not found")
```

**Evidence**: `tests/contract/test_cross_manager_query_contract.py` (35 tests)

---

## Removing Packages

```python
# Remove packages
result = pm.remove(["vim"])

# Remove with unused dependencies
result = pm.remove(["vim"], remove_dependencies=True)
```

**Evidence**: `tests/contract/test_cross_manager_remove_contract.py` (25 tests)

---

## Searching for Packages

```python
# Search for packages
result = pm.search("editor")

for pkg in result.packages:
    print(f"{pkg.name}: {pkg.description}")
```

**Evidence**: `tests/contract/test_cross_manager_query_contract.py::test_contract__search_returns_search_result_type`

---

## Error Handling

```python
from dotfiles_package_manager import PackageManagerFactory
from dotfiles_package_manager.core.base import PackageManagerError

try:
    pm = PackageManagerFactory.create_auto()
    result = pm.install(["vim"])
except PackageManagerError as e:
    print(f"Package manager error: {e}")
    print(f"Command: {e.command}")
    print(f"Exit code: {e.exit_code}")
except FileNotFoundError:
    # Subprocess errors propagate (not caught internally)
    print("Executable not found")
except PermissionError:
    print("Permission denied")
```

**Important**: Only `PackageManagerError` is caught internally. Other subprocess exceptions (`FileNotFoundError`, `PermissionError`, `TimeoutExpired`) propagate to the caller.

**Evidence**: `tests/characterization/test_characterization__subprocess_errors.py` (20 tests)

---

## Common Patterns

### Pipeline Pattern (from dotfiles-installer)

```python
# Step 1: Update system
result = pm.update_system()
if not result.success:
    log_warning("System update had issues")
    # Continue anyway - partial success is OK

# Step 2: Install required packages
required = ["git", "curl", "wget"]
result = pm.install(required)
for pkg in result.packages_failed:
    log_error(f"Failed to install: {pkg}")

# Step 3: Install optional packages
optional = ["htop", "tree"]
result = pm.install(optional)
# Don't fail if optional packages fail
```

---

## Next Steps

- [Advanced Usage Guide](AdvancedUsage.md) - All features in detail
- [Error Handling Guide](ErrorHandling.md) - Exception handling patterns
- [API Reference](../api/PackageManager.md) - Full API documentation

