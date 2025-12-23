# PackageManagerFactory API Reference

## Purpose

Documents the `PackageManagerFactory` class and `detect_distribution_family()` function for creating and managing package manager instances.

---

## Function: detect_distribution_family()

```python
def detect_distribution_family() -> DistributionFamily
```

Detect the current Linux distribution family by parsing `/etc/os-release`.

**Returns**: `DistributionFamily` enum value

**Source**: `src/dotfiles_package_manager/core/factory.py::detect_distribution_family` (lines 29-72)

**Detection Rules**:
| Keywords in `/etc/os-release` | Result |
|-------------------------------|--------|
| arch linux, manjaro, endeavouros, artix | `DistributionFamily.ARCH` |
| debian, ubuntu, mint, pop, elementary | `DistributionFamily.DEBIAN` |
| fedora, rhel, red hat, centos, rocky, alma, oracle | `DistributionFamily.REDHAT` |
| (file not found or no match) | `DistributionFamily.UNKNOWN` |

**Verified Behaviors**:

| Behavior | Evidence | Confidence |
|----------|----------|------------|
| Returns `DistributionFamily` enum | `tests/contract/test_factory_contracts.py::test_contract__detect_distribution_family_returns_enum` | High |
| Never raises exceptions | `tests/contract/test_factory_contracts.py::test_contract__detect_distribution_family_never_raises` | High |

---

## Class: PackageManagerFactory

Factory for creating package manager instances.

**Source**: `src/dotfiles_package_manager/core/factory.py::PackageManagerFactory` (lines 75-284)

---

### create_auto()

```python
@classmethod
def create_auto(
    cls,
    prefer_third_party: bool = True,
    distribution_family: DistributionFamily | None = None,
) -> PackageManager
```

Auto-detect and create the best available package manager.

**Parameters**:
- `prefer_third_party`: Prefer managers with third-party repo support (default: `True`)
  - Arch: Prefer paru/yay over pacman (for AUR access)
  - Debian/RedHat: No effect (apt/dnf handle third-party natively)
- `distribution_family`: Override automatic distribution detection

**Returns**: `PackageManager` instance

**Raises**: `PackageManagerError` if no suitable package manager found

**Source**: `src/dotfiles_package_manager/core/factory.py` (lines 90-152)

**Preference Order**:
| Distribution | `prefer_third_party=True` | `prefer_third_party=False` |
|--------------|---------------------------|---------------------------|
| Arch | paru → yay → pacman | pacman only |
| Debian | apt | apt |
| RedHat | dnf | dnf |

**Verified Behaviors**:

| Behavior | Evidence | Confidence |
|----------|----------|------------|
| Returns `PackageManager` instance | `tests/contract/test_factory_contracts.py::test_contract__create_auto_returns_package_manager` | High |
| Raises on no manager found | `tests/contract/test_factory_contracts.py::test_contract__create_auto_raises_on_no_manager_found` | High |
| Raises on unsupported distro | `tests/contract/test_factory_contracts.py::test_contract__create_auto_raises_on_unsupported_distro` | High |
| Respects `prefer_third_party=True` | `tests/contract/test_factory_contracts.py::test_contract__create_auto_respects_prefer_third_party_true` | High |
| Respects `prefer_third_party=False` | `tests/contract/test_factory_contracts.py::test_contract__create_auto_respects_prefer_third_party_false` | High |

**Test Coverage**: `tests/contract/test_factory_contracts.py::TestFactoryCreateAutoContract`

---

### create()

```python
@classmethod
def create(cls, manager_type: PackageManagerType) -> PackageManager
```

Create a specific package manager instance.

**Parameters**:
- `manager_type`: Type of package manager to create

**Returns**: `PackageManager` instance

**Raises**: `PackageManagerError` if type not supported or not available

**Source**: `src/dotfiles_package_manager/core/factory.py` (lines 154-181)

**Verified Behaviors**:

| Behavior | Evidence | Confidence |
|----------|----------|------------|
| Returns `PackageManager` instance | `tests/contract/test_factory_contracts.py::test_contract__create_returns_package_manager` | High |
| Raises on unsupported type | `tests/contract/test_factory_contracts.py::test_contract__create_raises_on_unsupported_type` | High |

**Test Coverage**: `tests/contract/test_factory_contracts.py::TestFactoryCreateContract`

---

### get_available_managers()

```python
@classmethod
def get_available_managers(cls) -> list[PackageManagerType]
```

Get list of available package managers on the system.

**Returns**: List of available `PackageManagerType` values

**Source**: `src/dotfiles_package_manager/core/factory.py` (lines 183-195)

**Verified Behaviors**:

| Behavior | Evidence | Confidence |
|----------|----------|------------|
| Returns list type | `tests/contract/test_factory_contracts.py::test_contract__get_available_managers_returns_list` | High |
| Never raises exceptions | `tests/contract/test_factory_contracts.py::test_contract__get_available_managers_never_raises` | High |
| Only includes available managers | `tests/contract/test_factory_contracts.py::test_contract__get_available_managers_includes_available_only` | High |

**Test Coverage**: `tests/contract/test_factory_contracts.py::TestFactoryGetAvailableManagersContract`

---

### is_available()

```python
@classmethod
def is_available(cls, manager_type: PackageManagerType) -> bool
```

Check if a specific package manager is available on the system.

**Parameters**:
- `manager_type`: Package manager type to check

**Returns**: `True` if available, `False` otherwise

**Source**: `src/dotfiles_package_manager/core/factory.py` (lines 197-208)

**Verified Behaviors**:

| Behavior | Evidence | Confidence |
|----------|----------|------------|
| Returns `bool` type | `tests/contract/test_factory_contracts.py::test_contract__is_available_returns_bool` | High |
| Never raises exceptions | `tests/contract/test_factory_contracts.py::test_contract__is_available_never_raises` | High |
| Returns `True` when executable exists | `tests/contract/test_factory_contracts.py::test_contract__is_available_true_when_executable_exists` | High |
| Returns `False` when executable missing | `tests/contract/test_factory_contracts.py::test_contract__is_available_false_when_executable_missing` | High |

**Test Coverage**: `tests/contract/test_factory_contracts.py::TestFactoryIsAvailableContract`

---

### get_recommended_manager()

```python
@classmethod
def get_recommended_manager(
    cls, distribution_family: DistributionFamily | None = None
) -> PackageManagerType | None
```

Get the recommended package manager for the system.

**Parameters**:
- `distribution_family`: Override automatic distribution detection

**Returns**: Recommended `PackageManagerType`, or `None` if none available

**Source**: `src/dotfiles_package_manager/core/factory.py` (lines 224-258)

**Verified Behaviors**:

| Behavior | Evidence | Confidence |
|----------|----------|------------|
| Returns type or `None` | `tests/contract/test_factory_contracts.py::test_contract__get_recommended_manager_returns_type_or_none` | High |
| Never raises exceptions | `tests/contract/test_factory_contracts.py::test_contract__get_recommended_manager_never_raises` | High |
| Respects preference order | `tests/contract/test_factory_contracts.py::test_contract__get_recommended_manager_respects_preference_order` | High |

**Test Coverage**: `tests/contract/test_factory_contracts.py::TestFactoryGetRecommendedManagerContract`

---

## Related Documentation

- [PackageManager API](PackageManager.md)
- [Types Reference](Types.md)
- [Quick Start Guide](../guides/QuickStart.md)

