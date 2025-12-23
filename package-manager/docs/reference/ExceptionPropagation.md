# Exception Propagation Reference

## Purpose

Documents which exceptions are caught vs. propagated by dotfiles-package-manager. This is critical for robust error handling.

---

## Verified Behavior

**Subprocess exceptions propagate to the caller. Only `PackageManagerError` wraps certain internal exceptions.**

This is a **characterization** of current behavior, verified by 20 tests across all 5 package managers.

---

## Evidence

**Test File**: `tests/characterization/test_characterization__subprocess_errors.py`

**Number of Tests**: 20 (4 tests × 5 package managers)

---

## Propagation Matrix

| Exception | Behavior | Where Handled |
|-----------|----------|---------------|
| `FileNotFoundError` | **Propagates** | Caller must handle |
| `PermissionError` | **Propagates** | Caller must handle |
| `subprocess.TimeoutExpired` | **Propagates** | Caller must handle |
| `PackageManagerError` | **Propagates** | Caller must handle |
| `subprocess.CalledProcessError` | **Wrapped** | Converted to `PackageManagerError` in `_run_command()` |

---

## Tests Verifying Propagation

| Test | Exception | Verified Behavior |
|------|-----------|------------------|
| `test_subprocess_file_not_found_returns_failure` | `FileNotFoundError` | Propagates unchanged |
| `test_subprocess_permission_error_returns_failure` | `PermissionError` | Propagates unchanged |
| `test_subprocess_timeout_returns_failure` | `TimeoutExpired` | Propagates unchanged |
| `test_package_manager_error_propagates_correctly` | `PackageManagerError` | Propagates unchanged |

---

## Source Code Reference

### Where Exceptions Are Caught

**File**: `src/dotfiles_package_manager/core/base.py`  
**Method**: `_run_command()` (lines 150-215)

The `_run_command()` method catches and wraps:
- `subprocess.TimeoutExpired` → `PackageManagerError`
- `subprocess.CalledProcessError` → `PackageManagerError`
- `FileNotFoundError` → `PackageManagerError`

**However**, exceptions can occur BEFORE `_run_command()` is called (e.g., in install logic), and those propagate.

### Where Exceptions Are NOT Caught

Individual method implementations (`install()`, `remove()`, etc.) do NOT catch:
- `FileNotFoundError`
- `PermissionError`
- `subprocess.TimeoutExpired`

These propagate directly to the caller.

---

## Example: Handling Propagated Exceptions

```python
import subprocess
from dotfiles_package_manager.core.base import PackageManagerError

try:
    result = pm.install(["vim"])
    
except FileNotFoundError as e:
    # Executable not found
    print(f"Package manager not found: {e}")
    
except PermissionError as e:
    # Permission denied
    print(f"Permission denied: {e}")
    
except subprocess.TimeoutExpired as e:
    # Command timed out
    print(f"Operation timed out: {e}")
    
except PackageManagerError as e:
    # Library-wrapped error
    print(f"Package manager error: {e}")
    print(f"Command: {e.command}")
    print(f"Exit code: {e.exit_code}")
```

---

## Cross-Manager Consistency

Exception propagation is **guaranteed identical** across all 5 package managers:

| Manager | Exception Propagation Verified |
|---------|-------------------------------|
| `PacmanPackageManager` | ✅ 4 tests pass |
| `YayPackageManager` | ✅ 4 tests pass |
| `ParuPackageManager` | ✅ 4 tests pass |
| `AptPackageManager` | ✅ 4 tests pass |
| `DnfPackageManager` | ✅ 4 tests pass |

---

## Why Exceptions Propagate

This is intentional design:

1. **Caller knows context** - The caller knows whether to retry, fallback, or fail
2. **No silent failures** - Exceptions force explicit handling
3. **Composability** - Library doesn't make policy decisions about recovery

---

## Contrast with Partial Failures

| Scenario | Behavior | Type |
|----------|----------|------|
| Package not found | `success=False`, `packages_failed=["pkg"]` | Return value |
| Executable not found | `FileNotFoundError` raised | Exception |
| Permission denied | `PermissionError` raised | Exception |

**Rule**: Package-level failures → return value. System-level failures → exception.

---

## Related Documentation

- [Error Handling Guide](../guides/ErrorHandling.md)
- [Partial Failures Reference](PartialFailures.md)
- [Types Reference](../api/Types.md)

