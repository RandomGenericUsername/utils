# Error Handling Guide

## Purpose

Documents exception behavior and error handling patterns for dotfiles-package-manager. Understanding which exceptions propagate vs. are caught is critical for robust application design.

---

## Exception Hierarchy

```
BaseException
└── Exception
    └── PackageManagerError (base for all library exceptions)
        ├── PackageNotFoundError
        └── PackageInstallationError
```

**Source**: `src/dotfiles_package_manager/core/base.py` (lines 11-34)

---

## Exception Propagation Rules

### Caught Exceptions (Wrapped as PackageManagerError)

The `_run_command()` method catches and wraps these exceptions:

| Original Exception | Wrapped As | When |
|-------------------|------------|------|
| `subprocess.CalledProcessError` | `PackageManagerError` | Command returns non-zero exit code |
| `subprocess.TimeoutExpired` | `PackageManagerError` | Command exceeds timeout |
| `FileNotFoundError` (in `_run_command`) | `PackageManagerError` | Executable not found during command run |

**Source**: `src/dotfiles_package_manager/core/base.py::_run_command` (lines 200-215)

### Propagating Exceptions (NOT Caught)

These exceptions propagate to the caller and are NOT caught by the library:

| Exception | When | Your Responsibility |
|-----------|------|---------------------|
| `FileNotFoundError` | Subprocess executable not found before `_run_command` | Handle in your code |
| `PermissionError` | Insufficient permissions | Handle in your code |
| `subprocess.TimeoutExpired` | If timeout occurs before wrapped | Handle in your code |

**Evidence**: `tests/characterization/test_characterization__subprocess_errors.py` (20 tests)

---

## Handling Patterns

### Pattern 1: Basic Error Handling

```python
from dotfiles_package_manager import PackageManagerFactory
from dotfiles_package_manager.core.base import (
    PackageManagerError,
    PackageNotFoundError,
    PackageInstallationError,
)

try:
    pm = PackageManagerFactory.create_auto()
    result = pm.install(["vim"])
except PackageManagerError as e:
    print(f"Package manager error: {e}")
    print(f"Command: {e.command}")
    print(f"Exit code: {e.exit_code}")
```

### Pattern 2: Comprehensive Error Handling

```python
try:
    pm = PackageManagerFactory.create_auto()
    result = pm.install(["vim"])
    
except PackageNotFoundError as e:
    # Package doesn't exist
    print(f"Package not found: {e}")
    
except PackageInstallationError as e:
    # Installation specifically failed
    print(f"Installation failed: {e}")
    
except PackageManagerError as e:
    # Any other package manager error
    print(f"Error: {e}")
    
except FileNotFoundError:
    # Executable not found (propagates!)
    print("Package manager executable not found")
    
except PermissionError:
    # Permission denied (propagates!)
    print("Permission denied - try with sudo?")
    
except subprocess.TimeoutExpired:
    # Timeout (may propagate!)
    print("Operation timed out")
```

### Pattern 3: Factory Error Handling

```python
try:
    pm = PackageManagerFactory.create_auto()
except PackageManagerError as e:
    if "Unsupported distribution" in str(e):
        print("Your Linux distribution is not supported")
    elif "No package manager found" in str(e):
        print("No package manager available on your system")
    else:
        print(f"Failed to create package manager: {e}")
```

**Evidence**: `tests/contract/test_factory_contracts.py::test_contract__create_auto_raises_on_no_manager_found`

---

## Error Information

`PackageManagerError` includes useful context:

```python
try:
    result = pm.install(["nonexistent-package-xyz"])
except PackageManagerError as e:
    # Error message
    print(f"Message: {e}")
    
    # Command that failed (if available)
    if e.command:
        print(f"Failed command: {e.command}")
    
    # Exit code (if available)
    if e.exit_code is not None:
        print(f"Exit code: {e.exit_code}")
```

---

## Partial Failure vs. Exceptions

**Important distinction**:

- **Partial failures** → Returned in `InstallResult` (NOT exceptions)
- **Complete failures** → May raise exceptions OR return `success=False`

```python
# Partial failure - NO exception raised
result = pm.install(["vim", "nonexistent"])
# result.success = True (vim succeeded)
# result.packages_failed = ["nonexistent"]

# Complete failure - may return failure OR raise exception
result = pm.install(["nonexistent"])
# result.success = False
# result.packages_failed = ["nonexistent"]
```

**Evidence**: `tests/characterization/test_characterization__partial_install_success.py`

---

## Defensive Pattern for Production

```python
def safe_install(pm, packages: list[str]) -> tuple[list[str], list[str]]:
    """Install packages with comprehensive error handling.
    
    Returns:
        Tuple of (installed_packages, failed_packages)
    """
    installed = []
    failed = []
    
    try:
        result = pm.install(packages)
        installed = result.packages_installed or []
        failed = result.packages_failed or []
        
    except FileNotFoundError:
        # Executable not found
        failed = packages
        
    except PermissionError:
        # Permission denied
        failed = packages
        
    except PackageManagerError as e:
        # Library-level error
        failed = packages
        
    return installed, failed
```

---

## Subprocess Exception Verification

The following tests verify that subprocess exceptions propagate correctly:

| Test | Exception Verified |
|------|-------------------|
| `test_subprocess_file_not_found_returns_failure` | `FileNotFoundError` propagates |
| `test_subprocess_permission_error_returns_failure` | `PermissionError` propagates |
| `test_subprocess_timeout_returns_failure` | `TimeoutExpired` propagates |
| `test_package_manager_error_propagates_correctly` | `PackageManagerError` propagates |

**Test File**: `tests/characterization/test_characterization__subprocess_errors.py` (20 tests, 4 tests × 5 managers)

---

## Related Documentation

- [Quick Start Guide](QuickStart.md)
- [Exception Propagation Reference](../reference/ExceptionPropagation.md)
- [Types Reference](../api/Types.md)

