# Advanced Usage Guide

## Purpose

Comprehensive guide to all features of dotfiles-package-manager with working examples from the test suite.

---

## Creating Package Managers

### Auto-Detection (Recommended)

```python
from dotfiles_package_manager import PackageManagerFactory

# Auto-detect with AUR helpers preferred (Arch only)
pm = PackageManagerFactory.create_auto(prefer_third_party=True)

# Auto-detect with official repos only
pm = PackageManagerFactory.create_auto(prefer_third_party=False)

# Override distribution detection
from dotfiles_package_manager.core.types import DistributionFamily
pm = PackageManagerFactory.create_auto(
    distribution_family=DistributionFamily.ARCH
)
```

**Evidence**: `tests/contract/test_factory_contracts.py::TestFactoryCreateAutoContract`

### Specific Manager Creation

```python
from dotfiles_package_manager.core.types import PackageManagerType

# Create specific manager
pm = PackageManagerFactory.create(PackageManagerType.PACMAN)
pm = PackageManagerFactory.create(PackageManagerType.APT)
pm = PackageManagerFactory.create(PackageManagerType.DNF)
```

**Evidence**: `tests/contract/test_factory_contracts.py::TestFactoryCreateContract`

### Checking Availability

```python
# Check if specific manager is available
if PackageManagerFactory.is_available(PackageManagerType.PACMAN):
    pm = PackageManagerFactory.create(PackageManagerType.PACMAN)

# Get all available managers
available = PackageManagerFactory.get_available_managers()
print(f"Available: {[m.value for m in available]}")

# Get recommended manager for system
recommended = PackageManagerFactory.get_recommended_manager()
if recommended:
    print(f"Recommended: {recommended.value}")
```

**Evidence**: `tests/contract/test_factory_contracts.py::TestFactoryIsAvailableContract`, `TestFactoryGetAvailableManagersContract`

---

## Installation Operations

### Basic Installation

```python
# Install single package
result = pm.install(["vim"])

# Install multiple packages
result = pm.install(["vim", "git", "curl", "wget"])

# Install with system update first
result = pm.install(["vim"], update_system=True)
```

**Evidence**: `tests/contract/test_cross_manager_install_contract.py` (35 tests)

### Handling Partial Failures

```python
result = pm.install(["vim", "nonexistent-package", "git"])

# success=True if ANY package succeeded
if result.success:
    print(f"Installed: {result.packages_installed}")  # ["vim", "git"]
    print(f"Failed: {result.packages_failed}")        # ["nonexistent-package"]

# Process results
for pkg in result.packages_installed:
    log_success(f"Installed: {pkg}")
    
for pkg in result.packages_failed:
    log_warning(f"Failed: {pkg}")
```

**Evidence**: `tests/characterization/test_characterization__partial_install_success.py` (15 tests)

### Empty Package Lists

```python
# Empty list returns success=True (no-op)
result = pm.install([])
assert result.success is True
```

**Evidence**: `tests/characterization/test_characterization__empty_package_list.py` (20 tests)

---

## Removal Operations

### Basic Removal

```python
# Remove single package
result = pm.remove(["vim"])

# Remove multiple packages
result = pm.remove(["vim", "git"])
```

### Removing Dependencies

```python
# Remove with unused dependencies
result = pm.remove(["vim"], remove_dependencies=True)
```

**Note**: Behavior of `remove_dependencies` varies by package manager:
- **pacman/yay/paru**: Uses `-Rns` (remove with dependencies and config files)
- **apt**: Uses `autoremove` 
- **dnf**: Uses `autoremove`

**Evidence**: `tests/contract/test_cross_manager_remove_contract.py` (25 tests)

---

## System Updates

### Basic Update

```python
# Update all system packages
result = pm.update_system()

if result.success:
    print("System updated successfully")
else:
    print(f"Update failed: {result.error_message}")
```

### Dry Run Mode

```python
# Check for updates without applying
result = pm.update_system(dry_run=True)
print(f"Updates available: {result.output}")
```

**Evidence**: `tests/contract/test_cross_manager_update_system_contract.py` (30 tests)

---

## Query Operations

### Checking Installation Status

```python
# Check if package is installed
is_vim_installed = pm.is_installed("vim")

# Batch check
packages_to_check = ["vim", "git", "nonexistent"]
for pkg in packages_to_check:
    status = "installed" if pm.is_installed(pkg) else "not installed"
    print(f"{pkg}: {status}")
```

**Evidence**: `tests/contract/test_cross_manager_query_contract.py`

### Getting Package Information

```python
info = pm.get_package_info("vim")

if info:
    print(f"Name: {info.name}")
    print(f"Version: {info.version}")
    print(f"Description: {info.description}")
    print(f"Repository: {info.repository}")
    print(f"Installed: {info.installed}")
    print(f"Size: {info.size}")
    print(f"Dependencies: {info.dependencies}")
else:
    print("Package not found")
```

**Evidence**: `tests/contract/test_cross_manager_query_contract.py::test_contract__get_package_info_returns_package_info_or_none`

### Searching Packages

```python
# Search for packages
result = pm.search("editor")

print(f"Found {result.total_found} packages for '{result.query}'")

for pkg in result.packages:
    installed = "✓" if pkg.installed else " "
    print(f"[{installed}] {pkg.name}: {pkg.description}")

# Search with limit
result = pm.search("editor", limit=10)
```

**Evidence**: `tests/contract/test_cross_manager_query_contract.py::test_contract__search_returns_search_result_type`

---

## Package Manager Type Information

```python
# Get manager type
pm_type = pm.manager_type
print(f"Using: {pm_type.value}")  # e.g., "pacman", "apt", "dnf"

# Get distribution family
family = pm_type.distribution_family
print(f"Family: {family.value}")  # e.g., "arch", "debian", "redhat"

# Check if it's an AUR helper
if pm_type.is_third_party_helper:
    print("This manager supports AUR packages")

# Check if sudo is required
if pm_type.requires_sudo:
    print("This manager requires sudo for privileged operations")
```

---

## Related Documentation

- [Quick Start Guide](QuickStart.md)
- [Error Handling Guide](ErrorHandling.md)
- [Partial Failures Reference](../reference/PartialFailures.md)

