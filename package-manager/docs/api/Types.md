# Types API Reference

## Purpose

Documents all public types and their contracts used throughout the dotfiles-package-manager library.

---

## Enums

### DistributionFamily

Linux distribution family classification.

**Source**: `src/dotfiles_package_manager/core/types.py::DistributionFamily` (lines 7-14)

**Values**:
| Value | Description |
|-------|-------------|
| `ARCH` | Arch Linux family (Arch, Manjaro, EndeavourOS, Artix) |
| `DEBIAN` | Debian family (Debian, Ubuntu, Mint, Pop!_OS, elementary) |
| `REDHAT` | RedHat family (Fedora, RHEL, CentOS, Rocky, Alma, Oracle) |
| `UNKNOWN` | Unknown or unsupported distribution |

**Test Coverage**: `tests/contract/test_factory_contracts.py::TestDetectDistributionFamilyContract`

---

### PackageManagerType

Enumeration of supported package manager types.

**Source**: `src/dotfiles_package_manager/core/types.py::PackageManagerType` (lines 16-63)

**Values**:
| Value | Distribution Family | Third-Party Helper | Requires Sudo |
|-------|--------------------|--------------------|---------------|
| `PACMAN` | Arch | No | Yes |
| `YAY` | Arch | Yes (AUR) | No |
| `PARU` | Arch | Yes (AUR) | No |
| `APT` | Debian | No | Yes |
| `APT_GET` | Debian | No | Yes |
| `DNF` | RedHat | No | Yes |
| `YUM` | RedHat | No | Yes |

**Properties**:
- `distribution_family` → `DistributionFamily`: Get the distribution family for this package manager
- `is_third_party_helper` → `bool`: True for AUR helpers (yay, paru)
- `requires_sudo` → `bool`: True if manager requires sudo for privileged operations

**Test Coverage**: `tests/contract/test_factory_contracts.py`

---

## Data Classes

### PackageInfo

Information about a package.

**Source**: `src/dotfiles_package_manager/core/types.py::PackageInfo` (lines 65-80)

**Attributes**:
| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | (required) | Package name |
| `version` | `str \| None` | `None` | Package version |
| `description` | `str \| None` | `None` | Package description |
| `repository` | `str \| None` | `None` | Source repository |
| `installed` | `bool` | `False` | Whether package is installed |
| `size` | `str \| None` | `None` | Package size |
| `dependencies` | `list[str] \| None` | `[]` | List of dependencies |

**Test Coverage**: `tests/contract/test_cross_manager_query_contract.py::test_contract__get_package_info_returns_package_info_or_none`

---

### InstallResult

Result of a package installation, removal, or update operation.

**Source**: `src/dotfiles_package_manager/core/types.py::InstallResult` (lines 82-97)

**Attributes**:
| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `success` | `bool` | (required) | Whether operation succeeded |
| `packages_installed` | `list[str] \| None` | `[]` | Packages successfully installed/removed |
| `packages_failed` | `list[str] \| None` | `[]` | Packages that failed |
| `output` | `str` | `""` | Command output |
| `error_message` | `str \| None` | `None` | Error message if failed |

**Verified Behaviors**:
- **Empty list handling**: Returns `success=True` when called with empty package list
  - Evidence: `tests/characterization/test_characterization__empty_package_list.py` (20 tests)
- **Partial failure semantics**: Returns `success=True` if ANY package succeeds
  - Evidence: `tests/characterization/test_characterization__partial_install_success.py` (15 tests)

**Test Coverage**: 
- `tests/contract/test_cross_manager_install_contract.py::test_contract__install_returns_install_result_type`
- `tests/contract/test_cross_manager_remove_contract.py::test_contract__remove_returns_install_result_type`
- `tests/contract/test_cross_manager_update_system_contract.py::test_contract__update_system_returns_install_result_type`

---

### SearchResult

Result of a package search operation.

**Source**: `src/dotfiles_package_manager/core/types.py::SearchResult` (lines 99-112)

**Attributes**:
| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `packages` | `list[PackageInfo] \| None` | `[]` | List of found packages |
| `query` | `str` | `""` | Original search query |
| `total_found` | `int` | `0` | Total number of results found |

**Test Coverage**: `tests/contract/test_cross_manager_query_contract.py::test_contract__search_returns_search_result_type`

---

## Exceptions

### PackageManagerError

Base exception for all package manager operations.

**Source**: `src/dotfiles_package_manager/core/base.py::PackageManagerError` (lines 11-23)

**Attributes**:
| Attribute | Type | Description |
|-----------|------|-------------|
| `message` | `str` | Error message |
| `command` | `str \| None` | Command that failed |
| `exit_code` | `int \| None` | Exit code if applicable |

### PackageNotFoundError

Raised when a package is not found. Subclass of `PackageManagerError`.

**Source**: `src/dotfiles_package_manager/core/base.py::PackageNotFoundError` (lines 25-28)

### PackageInstallationError

Raised when package installation fails. Subclass of `PackageManagerError`.

**Source**: `src/dotfiles_package_manager/core/base.py::PackageInstallationError` (lines 30-34)

---

## Related Documentation

- [PackageManager API](PackageManager.md)
- [PackageManagerFactory API](PackageManagerFactory.md)
- [Exception Propagation Reference](../reference/ExceptionPropagation.md)

