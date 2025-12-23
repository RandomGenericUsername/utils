# PackageManager API Reference

## Purpose

Documents the `PackageManager` abstract base class contract. All 5 implementations (pacman, yay, paru, apt, dnf) satisfy identical contracts as verified by cross-manager tests.

---

## Class Overview

**Source**: `src/dotfiles_package_manager/core/base.py::PackageManager` (lines 37-216)

**Type**: Abstract Base Class (ABC)

**Implementations**:
| Implementation | Distribution | Source Path |
|----------------|--------------|-------------|
| `PacmanPackageManager` | Arch Linux | `implementations/arch/pacman.py` |
| `YayPackageManager` | Arch Linux (AUR) | `implementations/arch/yay.py` |
| `ParuPackageManager` | Arch Linux (AUR) | `implementations/arch/paru.py` |
| `AptPackageManager` | Debian/Ubuntu | `implementations/debian/apt.py` |
| `DnfPackageManager` | RedHat/Fedora | `implementations/redhat/dnf.py` |

---

## Constructor

```python
def __init__(self, executable_path: Path | None = None)
```

**Parameters**:
- `executable_path`: Optional path to the package manager executable. If not provided, auto-detected via `_find_executable()`.

**Raises**: `PackageManagerError` if executable not found

**Source**: `src/dotfiles_package_manager/core/base.py` (lines 40-52)

---

## Properties

### manager_type

```python
@property
def manager_type(self) -> PackageManagerType
```

Returns the type of this package manager.

**Source**: `src/dotfiles_package_manager/core/base.py` (lines 54-58)

---

## Methods

### install()

```python
def install(self, packages: list[str], update_system: bool = False) -> InstallResult
```

Install packages.

**Parameters**:
- `packages`: List of package names to install
- `update_system`: Whether to update system before installing (default: `False`)

**Returns**: `InstallResult` with installation details

**Source**: `src/dotfiles_package_manager/core/base.py` (lines 65-79)

**Verified Behaviors**:

| Behavior | Evidence | Confidence |
|----------|----------|------------|
| Empty list returns `success=True` | `tests/contract/test_cross_manager_install_contract.py::test_contract__install_empty_list` | High |
| Single package success returns `success=True` | `tests/contract/test_cross_manager_install_contract.py::test_contract__install_single_package_success` | High |
| Multiple packages success returns `success=True` | `tests/contract/test_cross_manager_install_contract.py::test_contract__install_multiple_packages_success` | High |
| Total failure returns `success=False` | `tests/contract/test_cross_manager_install_contract.py::test_contract__install_total_failure` | High |
| Partial failure returns `success=True` | `tests/contract/test_cross_manager_install_contract.py::test_contract__install_partial_failure` | High |
| Returns `InstallResult` type | `tests/contract/test_cross_manager_install_contract.py::test_contract__install_returns_install_result_type` | High |
| Subprocess errors propagate | `tests/contract/test_cross_manager_install_contract.py::test_contract__install_subprocess_error_handling` | High |

**Test Coverage**: 35 tests in `tests/contract/test_cross_manager_install_contract.py`

---

### remove()

```python
def remove(self, packages: list[str], remove_dependencies: bool = False) -> InstallResult
```

Remove packages.

**Parameters**:
- `packages`: List of package names to remove
- `remove_dependencies`: Whether to remove unused dependencies (default: `False`)

**Returns**: `InstallResult` with removal details

**Source**: `src/dotfiles_package_manager/core/base.py` (lines 81-95)

**Verified Behaviors**:

| Behavior | Evidence | Confidence |
|----------|----------|------------|
| Empty list returns `success=True` | `tests/contract/test_cross_manager_remove_contract.py::test_contract__remove_empty_list` | High |
| Single package success | `tests/contract/test_cross_manager_remove_contract.py::test_contract__remove_single_package_success` | High |
| Multiple packages success | `tests/contract/test_cross_manager_remove_contract.py::test_contract__remove_multiple_packages_success` | High |
| Returns `InstallResult` type | `tests/contract/test_cross_manager_remove_contract.py::test_contract__remove_returns_install_result_type` | High |
| Respects `remove_dependencies` flag | `tests/contract/test_cross_manager_remove_contract.py::test_contract__remove_with_dependencies_flag` | High |

**Test Coverage**: 25 tests in `tests/contract/test_cross_manager_remove_contract.py`

---

### update_system()

```python
def update_system(self, dry_run: bool = False) -> InstallResult
```

Update the system packages.

**Parameters**:
- `dry_run`: If `True`, only check for updates without applying them (default: `False`)

**Returns**: `InstallResult` with update details

**Source**: `src/dotfiles_package_manager/core/base.py` (lines 111-122)

**Verified Behaviors**:

| Behavior | Evidence | Confidence |
|----------|----------|------------|
| Returns `InstallResult` type | `tests/contract/test_cross_manager_update_system_contract.py::test_contract__update_system_returns_install_result_type` | High |
| Respects `dry_run=False` | `tests/contract/test_cross_manager_update_system_contract.py::test_contract__update_system_dry_run_false` | High |
| Respects `dry_run=True` | `tests/contract/test_cross_manager_update_system_contract.py::test_contract__update_system_dry_run_true` | High |
| Failure handling | `tests/contract/test_cross_manager_update_system_contract.py::test_contract__update_system_failure_handling` | High |
| Subprocess errors propagate | `tests/contract/test_cross_manager_update_system_contract.py::test_contract__update_system_subprocess_error` | High |

**Test Coverage**: 30 tests in `tests/contract/test_cross_manager_update_system_contract.py`

---

### search()

```python
def search(self, query: str, limit: int | None = None) -> SearchResult
```

Search for packages.

**Parameters**:
- `query`: Search query string
- `limit`: Maximum number of results to return (default: `None` for no limit)

**Returns**: `SearchResult` with found packages

**Source**: `src/dotfiles_package_manager/core/base.py` (lines 97-109)

**Verified Behaviors**:

| Behavior | Evidence | Confidence |
|----------|----------|------------|
| Returns `SearchResult` type | `tests/contract/test_cross_manager_query_contract.py::test_contract__search_returns_search_result_type` | High |

**Test Coverage**: `tests/contract/test_cross_manager_query_contract.py`

---

### is_installed()

```python
def is_installed(self, package: str) -> bool
```

Check if a package is installed.

**Parameters**:
- `package`: Package name to check

**Returns**: `True` if package is installed, `False` otherwise

**Source**: `src/dotfiles_package_manager/core/base.py` (lines 124-135)

**Verified Behaviors**:

| Behavior | Evidence | Confidence |
|----------|----------|------------|
| Returns `bool` type | `tests/contract/test_cross_manager_query_contract.py::test_contract__is_installed_returns_bool` | High |
| Returns `True` for installed package | `tests/contract/test_cross_manager_query_contract.py::test_contract__is_installed_true_for_installed_package` | High |
| Returns `False` for not installed package | `tests/contract/test_cross_manager_query_contract.py::test_contract__is_installed_false_for_not_installed_package` | High |

**Test Coverage**: `tests/contract/test_cross_manager_query_contract.py`

---

### get_package_info()

```python
def get_package_info(self, package: str) -> PackageInfo | None
```

Get detailed information about a package.

**Parameters**:
- `package`: Package name

**Returns**: `PackageInfo` if found, `None` otherwise

**Source**: `src/dotfiles_package_manager/core/base.py` (lines 137-148)

**Verified Behaviors**:

| Behavior | Evidence | Confidence |
|----------|----------|------------|
| Returns `PackageInfo` or `None` | `tests/contract/test_cross_manager_query_contract.py::test_contract__get_package_info_returns_package_info_or_none` | High |
| Returns `None` for nonexistent package | `tests/contract/test_cross_manager_query_contract.py::test_contract__get_package_info_none_for_nonexistent` | High |

**Test Coverage**: `tests/contract/test_cross_manager_query_contract.py`

---

## Cross-Manager Consistency

**Critical Guarantee**: All 5 implementations satisfy identical contracts.

This is verified by parametrized tests that run against all implementations:
- `tests/contract/test_cross_manager_install_contract.py` (35 tests)
- `tests/contract/test_cross_manager_remove_contract.py` (25 tests)
- `tests/contract/test_cross_manager_update_system_contract.py` (30 tests)
- `tests/contract/test_cross_manager_query_contract.py` (35 tests)

---

## Related Documentation

- [PackageManagerFactory API](PackageManagerFactory.md)
- [Types Reference](Types.md)
- [Partial Failures Reference](../reference/PartialFailures.md)
- [Exception Propagation Reference](../reference/ExceptionPropagation.md)

