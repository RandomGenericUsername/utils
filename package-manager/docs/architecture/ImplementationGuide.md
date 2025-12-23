# Implementation Guide

## Purpose

Guide for adding new package manager implementations to dotfiles-package-manager.

---

## Overview

To add a new package manager, you must:

1. Create a new implementation class
2. Register it in the factory
3. Write contract tests to verify consistency
4. Update distribution detection (if needed)

---

## Step 1: Create Implementation Class

Create a new file in the appropriate distribution directory:

```python
# src/dotfiles_package_manager/implementations/{distro}/{manager}.py

from pathlib import Path
import shutil

from dotfiles_package_manager.core.base import (
    PackageManager,
    PackageManagerError,
)
from dotfiles_package_manager.core.types import (
    InstallResult,
    PackageInfo,
    PackageManagerType,
    SearchResult,
)


class NewPackageManager(PackageManager):
    """Implementation for new package manager."""
    
    @property
    def manager_type(self) -> PackageManagerType:
        return PackageManagerType.NEW_MANAGER
    
    def _find_executable(self) -> Path | None:
        path = shutil.which("new-manager")
        return Path(path) if path else None
    
    def install(
        self, packages: list[str], update_system: bool = False
    ) -> InstallResult:
        # Handle empty list (REQUIRED - must return success=True)
        if not packages:
            return InstallResult(success=True)
        
        # Implementation...
        pass
    
    def remove(
        self, packages: list[str], remove_dependencies: bool = False
    ) -> InstallResult:
        # Handle empty list
        if not packages:
            return InstallResult(success=True)
        
        # Implementation...
        pass
    
    def update_system(self, dry_run: bool = False) -> InstallResult:
        # Implementation...
        pass
    
    def search(self, query: str, limit: int | None = None) -> SearchResult:
        # Implementation...
        pass
    
    def is_installed(self, package: str) -> bool:
        # Implementation...
        pass
    
    def get_package_info(self, package: str) -> PackageInfo | None:
        # Implementation...
        pass
```

---

## Step 2: Add to PackageManagerType

```python
# src/dotfiles_package_manager/core/types.py

class PackageManagerType(Enum):
    # ... existing types ...
    NEW_MANAGER = "new-manager"
    
    @property
    def distribution_family(self) -> DistributionFamily:
        # Add mapping
        if self == PackageManagerType.NEW_MANAGER:
            return DistributionFamily.NEW_FAMILY
        # ... existing mappings ...
```

---

## Step 3: Register in Factory

```python
# src/dotfiles_package_manager/core/factory.py

from dotfiles_package_manager.implementations.{distro}.{manager} import (
    NewPackageManager,
)

class PackageManagerFactory:
    _MANAGERS = {
        # ... existing managers ...
        PackageManagerType.NEW_MANAGER: NewPackageManager,
    }
```

---

## Step 4: Update Distribution Detection (if needed)

```python
# src/dotfiles_package_manager/core/factory.py

def detect_distribution_family() -> DistributionFamily:
    # Add detection keywords
    if any(x in content for x in ["new-distro", "variant"]):
        return DistributionFamily.NEW_FAMILY
```

---

## Step 5: Add to Contract Tests

Add your manager to the parametrized test list:

```python
# tests/contract/test_cross_manager_install_contract.py

ALL_MANAGERS = [
    # ... existing managers ...
    (NewPackageManager, [...]),
]

@pytest.mark.parametrize("manager_class,expected_command_prefix", ALL_MANAGERS)
def test_contract__install_empty_list(manager_class, expected_command_prefix):
    # Test runs automatically for your new manager
    pass
```

---

## Required Contracts

Your implementation MUST satisfy these contracts (verified by tests):

### Install Contracts

| Contract | Requirement |
|----------|-------------|
| Empty list handling | Return `success=True` immediately |
| Partial failure | Return `success=True` if any succeed |
| Total failure | Return `success=False` if all fail |
| Return type | Always return `InstallResult` |

### Remove Contracts

| Contract | Requirement |
|----------|-------------|
| Empty list handling | Return `success=True` immediately |
| Return type | Always return `InstallResult` |

### Query Contracts

| Contract | Requirement |
|----------|-------------|
| `is_installed()` | Return `bool` |
| `get_package_info()` | Return `PackageInfo` or `None` |
| `search()` | Return `SearchResult` |

---

## Example: Existing Implementations

Study these for reference:

| Implementation | File | Notes |
|----------------|------|-------|
| PacmanPackageManager | `implementations/arch/pacman.py` | Official Arch |
| YayPackageManager | `implementations/arch/yay.py` | AUR helper |
| ParuPackageManager | `implementations/arch/paru.py` | AUR helper |
| AptPackageManager | `implementations/debian/apt.py` | Debian/Ubuntu |
| DnfPackageManager | `implementations/redhat/dnf.py` | Fedora/RHEL |

---

## Testing Your Implementation

```bash
# Run all contract tests (includes your new manager)
uv run pytest tests/contract/ -v

# Run characterization tests
uv run pytest tests/characterization/ -v

# Run all tests
uv run pytest tests/ -v
```

All 189+ tests must pass before your implementation is complete.

---

## Related Documentation

- [Architecture Overview](Overview.md)
- [PackageManager API](../api/PackageManager.md)
- [Types Reference](../api/Types.md)

