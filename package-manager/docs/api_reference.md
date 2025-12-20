# API Reference

Complete API documentation for the `dotfiles_package_manager` module.

---

## Table of Contents

1. [PackageManagerFactory](#packagemanagerfactory)
2. [PackageManager](#packagemanager)
3. [Types](#types)
4. [Exceptions](#exceptions)
5. [Distribution Detection](#distribution-detection)

---

## PackageManagerFactory

Factory class for creating package manager instances with automatic detection.

### Methods

#### `create_auto(prefer_third_party=True, distribution_family=None) → PackageManager`

Automatically detect and create the best available package manager.

**Parameters:**
- `prefer_third_party` (bool, optional): Whether to prefer third-party repository helpers. Default: `True`
  - **Arch Linux**: Prefer paru/yay over pacman (for AUR access)
  - **Debian/Ubuntu**: No effect (apt handles PPAs natively)
  - **Fedora/RHEL**: No effect (dnf handles COPR natively)
- `distribution_family` (DistributionFamily, optional): Override automatic distribution detection. Default: `None` (auto-detect)

**Returns:**
- `PackageManager`: Instance of the best available package manager

**Raises:**
- `PackageManagerError`: If no package manager is available

**Behavior by Distribution:**
- **Arch Linux**:
  - If `prefer_third_party=True`: Tries Paru → Yay → Pacman
  - If `prefer_third_party=False`: Tries Pacman only
- **Debian/Ubuntu**: Tries APT
- **Fedora/RHEL**: Tries DNF

**Examples:**
```python
# Auto-detect distribution and use best package manager
pm = PackageManagerFactory.create_auto()

# Prefer official repos only (Arch: pacman, no AUR helpers)
pm = PackageManagerFactory.create_auto(prefer_third_party=False)

# Override distribution detection
from dotfiles_package_manager import DistributionFamily
pm = PackageManagerFactory.create_auto(
    distribution_family=DistributionFamily.DEBIAN
)
```

---

#### `create(manager_type) → PackageManager`

Create a specific package manager instance.

**Parameters:**
- `manager_type` (PackageManagerType): Type of package manager to create

**Returns:**
- `PackageManager`: Instance of the specified package manager

**Raises:**
- `PackageManagerError`: If manager type not supported or not available

**Example:**
```python
from dotfiles_package_manager import PackageManagerFactory, PackageManagerType

pm = PackageManagerFactory.create(PackageManagerType.PARU)
```

---

#### `get_available_managers() → list[PackageManagerType]`

Get list of available package managers on the system.

**Returns:**
- `list[PackageManagerType]`: List of available package manager types

**Example:**
```python
available = PackageManagerFactory.get_available_managers()
print(f"Available: {[m.value for m in available]}")
# Output: Available: ['paru', 'pacman']
```

---

#### `is_available(manager_type) → bool`

Check if a specific package manager is available on the system.

**Parameters:**
- `manager_type` (PackageManagerType): Package manager type to check

**Returns:**
- `bool`: True if available, False otherwise

**Example:**
```python
if PackageManagerFactory.is_available(PackageManagerType.PARU):
    pm = PackageManagerFactory.create(PackageManagerType.PARU)
```

---

#### `get_recommended_manager(distribution_family=None) → PackageManagerType | None`

Get the recommended package manager for the system.

**Parameters:**
- `distribution_family` (DistributionFamily, optional): Override automatic distribution detection

**Returns:**
- `PackageManagerType | None`: Recommended package manager type, or None if none available

**Example:**
```python
recommended = PackageManagerFactory.get_recommended_manager()
if recommended:
    print(f"Recommended: {recommended.value}")
```

---

#### `create_recommended(distribution_family=None) → PackageManager`

Create an instance of the recommended package manager.

**Parameters:**
- `distribution_family` (DistributionFamily, optional): Override automatic distribution detection

**Returns:**
- `PackageManager`: Instance of recommended package manager

**Raises:**
- `PackageManagerError`: If no package manager is available

**Example:**
```python
pm = PackageManagerFactory.create_recommended()
```

---

## PackageManager

Abstract base class defining the package manager interface. All implementations (Pacman, Yay, Paru) implement this interface.

### Properties

#### `manager_type → PackageManagerType`

Get the type of this package manager.

**Returns:**
- `PackageManagerType`: The manager type (PACMAN, YAY, or PARU)

**Example:**
```python
pm = PackageManagerFactory.create_auto()
print(f"Using: {pm.manager_type.value}")
```

---

### Methods

#### `install(packages, update_system=False) → InstallResult`

Install one or more packages.

**Parameters:**
- `packages` (list[str]): List of package names to install
- `update_system` (bool, optional): Whether to update system before installing. Default: `False`

**Returns:**
- `InstallResult`: Result of the installation operation

**Example:**
```python
# Install single package
result = pm.install(["vim"])

# Install multiple packages
result = pm.install(["git", "tmux", "neovim"])

# Install with system update
result = pm.install(["package"], update_system=True)

# Check result
if result.success:
    print(f"Installed: {result.packages_installed}")
else:
    print(f"Failed: {result.packages_failed}")
```

---

#### `remove(packages, remove_dependencies=False) → InstallResult`

Remove one or more packages.

**Parameters:**
- `packages` (list[str]): List of package names to remove
- `remove_dependencies` (bool, optional): Whether to remove dependencies. Default: `False`

**Returns:**
- `InstallResult`: Result of the removal operation

**Example:**
```python
# Remove single package
result = pm.remove(["old-package"])

# Remove with dependencies
result = pm.remove(["package"], remove_dependencies=True)

# Remove multiple packages
result = pm.remove(["pkg1", "pkg2", "pkg3"])
```

---

#### `search(query, limit=None) → SearchResult`

Search for packages matching a query.

**Parameters:**
- `query` (str): Search query string
- `limit` (int | None, optional): Maximum number of results to return. Default: `None` (no limit)

**Returns:**
- `SearchResult`: Search results containing matching packages

**Example:**
```python
# Search without limit
result = pm.search("python")

# Search with limit
result = pm.search("python", limit=10)

# Process results
for pkg in result.packages:
    status = "[installed]" if pkg.installed else ""
    print(f"{pkg.name} {pkg.version} {status}")
    print(f"  {pkg.description}")
```

---

#### `update_system(dry_run=False) → InstallResult`

Update system packages or sync package databases.

**Parameters:**
- `dry_run` (bool, optional): If True, only check for updates without applying. Default: `False`

**Returns:**
- `InstallResult`: Result of the update operation

**Example:**
```python
# Check for updates (dry run)
result = pm.update_system(dry_run=True)
print(result.output)  # "Found X upgradeable packages"

# Sync package databases
result = pm.update_system(dry_run=False)
```

---

#### `is_installed(package) → bool`

Check if a package is installed.

**Parameters:**
- `package` (str): Package name to check

**Returns:**
- `bool`: True if installed, False otherwise

**Example:**
```python
if pm.is_installed("vim"):
    print("Vim is installed")
else:
    print("Vim is not installed")
```

---

#### `get_package_info(package) → PackageInfo | None`

Get detailed information about a package.

**Parameters:**
- `package` (str): Package name

**Returns:**
- `PackageInfo | None`: Package information, or None if package not found

**Example:**
```python
info = pm.get_package_info("vim")
if info:
    print(f"Name: {info.name}")
    print(f"Version: {info.version}")
    print(f"Description: {info.description}")
    print(f"Repository: {info.repository}")
    print(f"Installed: {info.installed}")
    print(f"Size: {info.size}")
    print(f"Dependencies: {', '.join(info.dependencies)}")
else:
    print("Package not found")
```

---

## Types

### DistributionFamily

Enum representing Linux distribution families.

**Values:**
- `ARCH = "arch"` - Arch Linux and derivatives (Manjaro, EndeavourOS, etc.)
- `DEBIAN = "debian"` - Debian and derivatives (Ubuntu, Mint, Pop!_OS, etc.)
- `REDHAT = "redhat"` - RedHat and derivatives (Fedora, RHEL, CentOS, Rocky, etc.)
- `UNKNOWN = "unknown"` - Unknown or unsupported distribution

**Example:**
```python
from dotfiles_package_manager import DistributionFamily, detect_distribution_family

family = detect_distribution_family()
if family == DistributionFamily.ARCH:
    print("Running on Arch Linux")
```

---

### PackageManagerType

Enum representing supported package manager types.

**Values:**

**Arch Linux:**
- `PACMAN = "pacman"` - Official Arch Linux package manager
- `YAY = "yay"` - Yay AUR helper (third-party)
- `PARU = "paru"` - Paru AUR helper (third-party)

**Debian/Ubuntu:**
- `APT = "apt"` - APT package manager

**RedHat/Fedora:**
- `DNF = "dnf"` - DNF package manager

**Properties:**
- `distribution_family` → `DistributionFamily`: Which distribution family this manager belongs to
- `is_third_party_helper` → `bool`: Whether this is a third-party repository helper (e.g., AUR helpers)
- `requires_sudo` → `bool`: Whether this manager requires explicit sudo

**Example:**
```python
from dotfiles_package_manager import PackageManagerType

manager_type = PackageManagerType.PARU
print(manager_type.value)  # "paru"
print(manager_type.distribution_family)  # DistributionFamily.ARCH
print(manager_type.is_third_party_helper)  # True
print(manager_type.requires_sudo)  # False (paru handles sudo internally)
```

---

### PackageInfo

Dataclass containing package information.

**Fields:**
- `name` (str): Package name
- `version` (str | None): Package version
- `description` (str | None): Package description
- `repository` (str | None): Repository name (core, extra, aur, etc.)
- `installed` (bool): Whether package is installed
- `size` (str | None): Package size (e.g., "1.5 MiB")
- `dependencies` (list[str]): List of dependency package names

**Example:**
```python
info = pm.get_package_info("vim")
# PackageInfo(
#     name="vim",
#     version="9.0.1234-1",
#     description="Vi Improved, a highly configurable, improved version of the vi text editor",
#     repository="extra",
#     installed=True,
#     size="1.5 MiB",
#     dependencies=["glibc", "libgcrypt", ...]
# )
```

---

### InstallResult

Dataclass containing results of install/remove/update operations.

**Fields:**
- `success` (bool): Whether operation succeeded overall
- `packages_installed` (list[str]): List of successfully processed packages
- `packages_failed` (list[str]): List of packages that failed
- `output` (str): Command output (stdout)
- `error_message` (str | None): Error message if operation failed

**Example:**
```python
result = pm.install(["pkg1", "pkg2", "pkg3"])
# InstallResult(
#     success=False,
#     packages_installed=["pkg1", "pkg2"],
#     packages_failed=["pkg3"],
#     output="...",
#     error_message="error: target not found: pkg3"
# )
```

---

### SearchResult

Dataclass containing search results.

**Fields:**
- `packages` (list[PackageInfo]): List of found packages
- `query` (str): Original search query
- `total_found` (int): Total number of packages found

**Example:**
```python
result = pm.search("python", limit=5)
# SearchResult(
#     packages=[PackageInfo(...), PackageInfo(...), ...],
#     query="python",
#     total_found=150
# )
```

---

## Exceptions

### PackageManagerError

Base exception for all package manager errors.

**Inherits:** `Exception`

**When Raised:**
- Package manager executable not found
- System-level failures
- Command execution errors

**Example:**
```python
from dotfiles_package_manager import PackageManagerError

try:
    pm = PackageManagerFactory.create_auto()
except PackageManagerError as e:
    print(f"Error: {e}")
```

---

### PackageNotFoundError

Exception raised when a package is not found.

**Inherits:** `PackageManagerError`

**When Raised:**
- Package doesn't exist in repositories
- Package name misspelled

**Example:**
```python
from dotfiles_package_manager import PackageNotFoundError

try:
    # Some operation
    pass
except PackageNotFoundError as e:
    print(f"Package not found: {e}")
```

---

### PackageInstallationError

Exception raised when package installation fails.

**Inherits:** `PackageManagerError`

**When Raised:**
- Installation fails due to system issues
- Dependency conflicts
- Permission issues

**Example:**
```python
from dotfiles_package_manager import PackageInstallationError

try:
    # Some operation
    pass
except PackageInstallationError as e:
    print(f"Installation failed: {e}")
```

---

## Distribution Detection

### `detect_distribution_family() → DistributionFamily`

Detect the current Linux distribution family by reading `/etc/os-release`.

**Returns:**
- `DistributionFamily`: Detected distribution family

**Detection Logic:**
- Reads `/etc/os-release` file
- Checks for distribution-specific keywords:
  - **Arch**: "arch linux", "manjaro", "endeavouros", "artix"
  - **Debian**: "debian", "ubuntu", "mint", "pop", "elementary"
  - **RedHat**: "fedora", "rhel", "red hat", "centos", "rocky", "alma", "oracle"
- Returns `DistributionFamily.UNKNOWN` if no match or file not found

**Example:**
```python
from dotfiles_package_manager import detect_distribution_family, DistributionFamily

family = detect_distribution_family()

if family == DistributionFamily.ARCH:
    print("Running on Arch Linux or derivative")
elif family == DistributionFamily.DEBIAN:
    print("Running on Debian or derivative")
elif family == DistributionFamily.REDHAT:
    print("Running on RedHat or derivative")
else:
    print("Unknown or unsupported distribution")
```

---

**Next:** [Usage Guide](usage_guide.md) | [Examples](examples.md)
