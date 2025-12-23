# Test Plan for dotfiles-package-manager

**Status**: Starting from scratch - existing tests are legacy and will be replaced  
**Priority**: Cross-manager consistency is CRITICAL - all 5 package managers must behave identically

---

## Real-World Usage Analysis

Based on analysis of the consuming project (`dotfiles-installer`), the library is used in the following ways:

### Actual API Usage in Production

**File**: `dotfiles-installer/src/pipeline_steps/package_management_steps.py`

1. **DetectPackageManagerStep**:
   ```python
   package_manager = PackageManagerFactory.create_auto(prefer_third_party=True)
   manager_type = package_manager.manager_type
   available = PackageManagerFactory.get_available_managers()
   ```

2. **UpdateSystemStep**:
   ```python
   result = pm.update_system(dry_run=dry_run)
   # Checks: result.success, result.output, result.error_message
   ```

3. **InstallPackagesStep**:
   ```python
   result = pm.install(packages, update_system=False)
   # Checks: result.success, result.packages_installed, result.packages_failed
   # Handles: PackageManagerError, TypeError (defensive)
   ```

**File**: `dotfiles-installer/src/system/detector.py`

- Uses custom detection logic (NOT the library's `detect_distribution_family`)
- Checks package manager availability with `shutil.which(pm.value)`

---

## Critical Flows (Evidence-Based)

| # | Flow | Entry Points | Why Critical | Evidence |
|---|------|--------------|--------------|----------|
| **1** | **Auto-detect & create manager** | `create_auto(prefer_third_party)` | Primary initialization path | `package_management_steps.py:60-62` |
| **2** | **Update system before install** | `update_system(dry_run)` → `install(update_system=False)` | Prevents partial upgrades on Arch | `package_management_steps.py:140-145`, `pacman.py:161-179` |
| **3** | **Install with partial failures** | `install(packages)` | Must track which succeeded/failed | `package_management_steps.py:260-280` |
| **4** | **Get available managers** | `get_available_managers()` | Debugging/logging | `package_management_steps.py:73-76` |
| **5** | **Cross-manager consistency** | Same operation on all 5 managers | ALL managers must behave identically | User requirement #5 |
| **6** | **Error handling** | `PackageManagerError` exceptions | Pipeline must handle gracefully | `package_management_steps.py:78-82, 147-152, 282-286` |
| **7** | **Dry-run mode** | `update_system(dry_run=True)` | Check updates without applying | `package_management_steps.py:140` |
| **8** | **Empty package list** | `install([])`, `remove([])` | Should succeed without errors | Common edge case |

---

## Candidate Contracts (Evidence-Backed)

### Contract 1: Factory Auto-Creation
**Method**: `PackageManagerFactory.create_auto(prefer_third_party, distribution_family)`  
**Evidence**: `factory.py:91-152`, `package_management_steps.py:60-62`

**Guarantees**:
- Returns a `PackageManager` instance
- Raises `PackageManagerError` if no manager found
- Respects `prefer_third_party` on Arch (paru > yay > pacman)
- Ignores `prefer_third_party` on Debian/RedHat
- Uses `detect_distribution_family()` if `distribution_family` is None

**Open Questions**:
- ❓ What if `/etc/os-release` is missing? (Currently returns `UNKNOWN`, then raises error)

---

### Contract 2: Get Available Managers
**Method**: `PackageManagerFactory.get_available_managers()`  
**Evidence**: `factory.py:184-195`, `package_management_steps.py:73-76`

**Guarantees**:
- Returns `list[PackageManagerType]`
- Never raises exceptions
- Only includes managers whose executables exist in PATH
- Order is not guaranteed

---

### Contract 3: Package Installation
**Method**: `PackageManager.install(packages, update_system)`  
**Evidence**: `base.py:54-81`, `pacman.py:30-91`, `package_management_steps.py:260-280`

**Guarantees**:
- Returns `InstallResult` with `success`, `packages_installed`, `packages_failed`
- Empty list returns `InstallResult(success=True, packages_installed=[], packages_failed=[])`
- If `update_system=True`, runs system update first (Arch: `-Syu`, Debian: `apt update`)
- Partial failures: `success=True` if ANY package succeeded

**Open Questions**:
- ❓ **Partial failure behavior**: Should `success=True` if some packages succeed? (Current: YES)
- ❓ **Sudo authentication failure**: What's the expected contract? (Current: raises `PackageManagerError`)

---

### Contract 4: System Update
**Method**: `PackageManager.update_system(dry_run)`  
**Evidence**: `base.py:97-109`, `pacman.py:161-179`, `package_management_steps.py:140-145`

**Guarantees**:
- Returns `InstallResult` with `success`, `output`, `error_message`
- `dry_run=True`: Check for updates without applying (no sudo)
- `dry_run=False`: Apply updates (requires sudo)
- Arch: Uses `-Syu` to prevent partial upgrades

**Open Questions**:
- ❓ **Dry-run output format**: What format is expected? (Current: varies by manager)

---

### Contract 5: Package Removal
**Method**: `PackageManager.remove(packages, remove_dependencies)`  
**Evidence**: `base.py:82-95`, `pacman.py:93-141`

**Guarantees**:
- Returns `InstallResult` (reuses same type as install)
- `remove_dependencies=True`: Remove unused dependencies (Arch: `-Rs`, Debian: `autoremove`)
- Empty list returns success

**Open Questions**:
- ❓ **Non-existent packages**: Should removing a non-existent package fail or succeed? (Current: varies)

---

### Contract 6: Cross-Manager Consistency
**Evidence**: User requirement #5, all implementations in `implementations/`

**Guarantees**:
- ALL 5 managers (pacman, yay, paru, apt, dnf) must behave identically for:
  - Empty input lists
  - Error handling (same exceptions for same conditions)
  - Return type structure
  - Partial failure handling
  - Dry-run behavior

**This is the HIGHEST PRIORITY contract to test.**

---

## Test Strategy

### Priority 1: Cross-Manager Contract Tests
**Location**: `tests/contract/test_cross_manager_consistency.py`

Parametrized tests that run the SAME test against ALL 5 managers:
```python
@pytest.mark.parametrize("manager_class", [
    PacmanPackageManager, YayPackageManager, ParuPackageManager,
    AptPackageManager, DnfPackageManager
])
def test_install_empty_list(manager_class, mock_subprocess):
    """All managers must handle empty list identically."""
    manager = manager_class()
    result = manager.install([])
    assert result.success is True
    assert result.packages_installed == []
    assert result.packages_failed == []
```

**Test Cases**:
- Empty package lists (install, remove)
- Single package success
- Multiple packages success
- Partial failures
- Total failures
- Error handling consistency
- Return type structure

---

### Priority 2: Characterization Tests
**Location**: `tests/characterization/`

Freeze current behavior for ambiguous cases:
- `test_characterization__partial_install_success.py`: Freeze `success=True` when some packages succeed
- `test_characterization__sudo_auth_failure.py`: Freeze current error handling
- `test_characterization__remove_nonexistent_package.py`: Freeze current behavior
- `test_characterization__dry_run_output_format.py`: Freeze current output format

---

### Priority 3: Factory Contract Tests
**Location**: `tests/contract/test_factory_contracts.py`

Test all factory methods:
- `create_auto()` with all distribution families
- `create()` with all manager types
- `get_available_managers()`
- `get_recommended_manager()`
- `create_recommended()`
- `is_available()`
- Error message consistency

---

### Priority 4: Unit Tests (Keep Existing)
**Location**: `tests/unit/`

Implementation-specific details:
- Command construction
- Output parsing
- Subprocess handling

---

## Out of Scope

- ❌ Testing all package manager **versions** (e.g., pacman 6.0 vs 6.1)
- ❌ Testing all distro **variants** (e.g., every Ubuntu version)
- ❌ Network failures during downloads
- ❌ Disk space exhaustion
- ❌ Performance/benchmarking
- ✅ **IN SCOPE**: Testing ALL 5 package managers for consistency (CRITICAL)

---

## Next Steps

1. ✅ Analyze real usage in dotfiles-installer
2. ⏳ Write characterization tests (freeze ambiguous behaviors)
3. ⏳ Write cross-manager contract tests (HIGHEST PRIORITY)
4. ⏳ Write factory contract tests
5. ⏳ Organize test directory structure

