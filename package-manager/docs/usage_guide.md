# Usage Guide

Comprehensive guide to using the `dotfiles_package_manager` module effectively.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Basic Operations](#basic-operations)
3. [Advanced Patterns](#advanced-patterns)
4. [Error Handling](#error-handling)
5. [Best Practices](#best-practices)
6. [Anti-Patterns](#anti-patterns)

---

## Getting Started

### Installation

Add the module as a dependency:

```bash
uv add dotfiles-package-manager
```

### First Steps

```python
from dotfiles_package_manager import PackageManagerFactory

# Create package manager (auto-detects best available)
pm = PackageManagerFactory.create_auto()

# Check which manager is being used
print(f"Using: {pm.manager_type.value}")
```

---

## Basic Operations

### Installing Packages

**Single Package:**
```python
result = pm.install(["vim"])
if result.success:
    print("✓ Vim installed successfully")
```

**Multiple Packages:**
```python
packages = ["git", "tmux", "neovim"]
result = pm.install(packages)

if result.success:
    print(f"✓ Installed: {', '.join(result.packages_installed)}")
```

**With System Update:**
```python
# Update package databases before installing
result = pm.install(["package"], update_system=True)
```

---

### Removing Packages

**Single Package:**
```python
result = pm.remove(["old-package"])
```

**With Dependencies:**
```python
# Remove package and its dependencies
result = pm.remove(["package"], remove_dependencies=True)
```

**Multiple Packages:**
```python
result = pm.remove(["pkg1", "pkg2", "pkg3"])
```

---

### Searching for Packages

**Basic Search:**
```python
result = pm.search("python")

for pkg in result.packages:
    status = "[installed]" if pkg.installed else ""
    print(f"{pkg.repository}/{pkg.name} {pkg.version} {status}")
    print(f"  {pkg.description}\n")
```

**Limited Results:**
```python
# Get only first 10 results
result = pm.search("python", limit=10)
```

**Finding Exact Package:**
```python
result = pm.search("neovim")
for pkg in result.packages:
    if pkg.name == "neovim":
        print(f"Found: {pkg.name} {pkg.version}")
        break
```

---

### Checking Package Status

**Check if Installed:**
```python
if pm.is_installed("vim"):
    print("Vim is installed")
else:
    print("Vim is not installed")
```

**Get Package Information:**
```python
info = pm.get_package_info("vim")
if info:
    print(f"Name: {info.name}")
    print(f"Version: {info.version}")
    print(f"Description: {info.description}")
    print(f"Repository: {info.repository}")
    print(f"Size: {info.size}")
    print(f"Dependencies: {', '.join(info.dependencies)}")
else:
    print("Package not found")
```

---

### System Updates

**Check for Updates (Dry Run):**
```python
result = pm.update_system(dry_run=True)
print(result.output)  # Shows available updates
```

**Sync Package Databases:**
```python
result = pm.update_system(dry_run=False)
if result.success:
    print("✓ Package databases synchronized")
```

---

## Advanced Patterns

### Pattern 1: Ensure Packages Installed

Install only packages that aren't already installed:

```python
def ensure_installed(pm, packages):
    """Ensure packages are installed."""
    to_install = []
    already_installed = []

    for pkg in packages:
        if pm.is_installed(pkg):
            already_installed.append(pkg)
        else:
            to_install.append(pkg)

    if already_installed:
        print(f"Already installed: {', '.join(already_installed)}")

    if to_install:
        print(f"Installing: {', '.join(to_install)}")
        result = pm.install(to_install)
        return result.success

    return True

# Usage
packages = ["vim", "git", "tmux"]
ensure_installed(pm, packages)
```

---

### Pattern 2: Interactive Package Selection

Search and let user choose which package to install:

```python
def search_and_install(pm, query):
    """Search for packages and let user choose."""
    # Search
    result = pm.search(query, limit=20)

    if not result.packages:
        print(f"No packages found for '{query}'")
        return

    # Display results
    print(f"\nFound {result.total_found} packages:\n")
    for i, pkg in enumerate(result.packages, 1):
        status = "[installed]" if pkg.installed else ""
        print(f"{i}. {pkg.name} {pkg.version} {status}")
        print(f"   {pkg.description}\n")

    # Get user choice
    choice = input("Enter package number to install (or 'q' to quit): ")
    if choice.lower() == 'q':
        return

    try:
        idx = int(choice) - 1
        pkg = result.packages[idx]

        # Install
        print(f"\nInstalling {pkg.name}...")
        install_result = pm.install([pkg.name])

        if install_result.success:
            print(f"✓ Successfully installed {pkg.name}")
        else:
            print(f"✗ Failed to install {pkg.name}")

    except (ValueError, IndexError):
        print("Invalid choice")

# Usage
search_and_install(pm, "editor")
```

---

### Pattern 3: Batch Installation with Progress

Install multiple packages with progress reporting:

```python
def install_with_progress(pm, packages):
    """Install packages one by one with progress."""
    total = len(packages)
    installed = []
    failed = []

    for i, pkg in enumerate(packages, 1):
        print(f"[{i}/{total}] Installing {pkg}...")

        result = pm.install([pkg])

        if result.success:
            installed.append(pkg)
            print(f"  ✓ Success")
        else:
            failed.append(pkg)
            print(f"  ✗ Failed: {result.error_message}")

    print(f"\nSummary:")
    print(f"  Installed: {len(installed)}/{total}")
    if failed:
        print(f"  Failed: {', '.join(failed)}")

    return len(failed) == 0

# Usage
packages = ["vim", "git", "tmux", "neovim"]
install_with_progress(pm, packages)
```

---

### Pattern 4: Conditional Installation

Install different packages based on what's available:

```python
def install_preferred(pm, preferences):
    """Install first available package from preferences.

    Args:
        pm: Package manager instance
        preferences: List of package names in order of preference

    Returns:
        Name of installed package, or None
    """
    for pkg in preferences:
        # Check if already installed
        if pm.is_installed(pkg):
            print(f"✓ {pkg} already installed")
            return pkg

        # Check if available
        result = pm.search(pkg, limit=1)
        if result.packages and result.packages[0].name == pkg:
            # Install
            install_result = pm.install([pkg])
            if install_result.success:
                print(f"✓ Installed {pkg}")
                return pkg

    print("✗ None of the preferred packages could be installed")
    return None

# Usage - install preferred editor
editor = install_preferred(pm, ["neovim", "vim", "vi"])
```

---

### Pattern 5: Package Manager Wrapper Class

Create a high-level wrapper for common operations:

```python
from dotfiles_package_manager import PackageManagerFactory, PackageManagerError
import logging

class PackageManagerWrapper:
    """High-level wrapper around package manager."""

    def __init__(self, prefer_aur=True):
        self.logger = logging.getLogger(__name__)
        try:
            self.pm = PackageManagerFactory.create_auto(prefer_aur_helper=prefer_aur)
            self.logger.info(f"Using: {self.pm.manager_type.value}")
        except PackageManagerError as e:
            self.logger.error(f"Failed to create package manager: {e}")
            raise

    def ensure_installed(self, packages):
        """Ensure packages are installed."""
        to_install = [pkg for pkg in packages if not self.pm.is_installed(pkg)]

        if not to_install:
            self.logger.info("All packages already installed")
            return True

        self.logger.info(f"Installing: {', '.join(to_install)}")
        result = self.pm.install(to_install)

        if result.success:
            self.logger.info(f"Installed: {', '.join(result.packages_installed)}")
            return True
        else:
            self.logger.error(f"Failed: {result.error_message}")
            return False

    def safe_remove(self, packages, remove_deps=False):
        """Safely remove packages."""
        installed = [pkg for pkg in packages if self.pm.is_installed(pkg)]

        if not installed:
            self.logger.info("No packages to remove")
            return True

        self.logger.info(f"Removing: {', '.join(installed)}")
        result = self.pm.remove(installed, remove_dependencies=remove_deps)

        return result.success

    def find_package(self, query):
        """Find exact package name from query."""
        result = self.pm.search(query, limit=50)

        # Look for exact match
        for pkg in result.packages:
            if pkg.name.lower() == query.lower():
                return pkg.name

        # Look for close match
        for pkg in result.packages:
            if query.lower() in pkg.name.lower():
                return pkg.name

        return None

# Usage
wrapper = PackageManagerWrapper()
wrapper.ensure_installed(["vim", "git", "tmux"])
```

---

### Pattern 6: Development Environment Setup

Complete workflow for setting up a development environment:

```python
def setup_dev_environment(pm):
    """Install development tools."""

    # Define package groups
    base_tools = ["git", "base-devel"]
    python_tools = ["python", "python-pip", "python-virtualenv"]
    node_tools = ["nodejs", "npm"]
    editors = ["neovim", "vim"]

    all_packages = base_tools + python_tools + node_tools + editors

    print("Setting up development environment...")
    print(f"Using package manager: {pm.manager_type.value}\n")

    # Update system first
    print("Updating package databases...")
    pm.update_system(dry_run=False)

    # Check what's already installed
    to_install = []
    for pkg in all_packages:
        if not pm.is_installed(pkg):
            to_install.append(pkg)

    if not to_install:
        print("✓ All packages already installed!")
        return True

    print(f"\nPackages to install: {', '.join(to_install)}\n")

    # Install
    result = pm.install(to_install)

    if result.success:
        print(f"\n✓ Successfully installed all packages!")
        return True
    elif result.packages_installed:
        print(f"\n⚠ Partial success:")
        print(f"  Installed: {', '.join(result.packages_installed)}")
        print(f"  Failed: {', '.join(result.packages_failed)}")
        return False
    else:
        print(f"\n✗ Installation failed: {result.error_message}")
        return False

# Usage
pm = PackageManagerFactory.create_auto()
setup_dev_environment(pm)
```

---

## Error Handling

### Handling Factory Errors

```python
from dotfiles_package_manager import PackageManagerFactory, PackageManagerError

try:
    pm = PackageManagerFactory.create_auto()
except PackageManagerError as e:
    print(f"No package manager available: {e}")
    print("Please install pacman, yay, or paru")
    exit(1)
```

---

### Handling Operation Failures

```python
result = pm.install(["package1", "package2", "package3"])

if result.success:
    print("✓ All packages installed successfully")
elif result.packages_installed:
    # Partial success
    print("⚠ Partial success:")
    print(f"  Installed: {', '.join(result.packages_installed)}")
    print(f"  Failed: {', '.join(result.packages_failed)}")
    print(f"  Error: {result.error_message}")
else:
    # Complete failure
    print(f"✗ Installation failed: {result.error_message}")
```

---

### Retry Logic

```python
def install_with_retry(pm, packages, max_retries=3):
    """Install packages with retry logic."""
    for attempt in range(max_retries):
        result = pm.install(packages)

        if result.success:
            return result

        if not result.packages_failed:
            # No specific failures, don't retry
            return result

        # Retry only failed packages
        packages = result.packages_failed
        print(f"Retry {attempt + 1}/{max_retries} for: {packages}")

    return result
```

---

## Best Practices

1. **Always use factory for creation**
   ```python
   # Good
   pm = PackageManagerFactory.create_auto()

   # Bad
   from dotfiles_package_manager.implementations.pacman import PacmanPackageManager
   pm = PacmanPackageManager()
   ```

2. **Check result.success before assuming success**
   ```python
   result = pm.install(["package"])
   if result.success:
       # Proceed
       pass
   ```

3. **Handle partial success**
   ```python
   if result.packages_installed:
       print(f"Installed: {result.packages_installed}")
   if result.packages_failed:
       print(f"Failed: {result.packages_failed}")
   ```

4. **Batch operations for efficiency**
   ```python
   # Good - single command
   pm.install(["pkg1", "pkg2", "pkg3"])

   # Bad - three commands
   pm.install(["pkg1"])
   pm.install(["pkg2"])
   pm.install(["pkg3"])
   ```

5. **Use dry_run for updates**
   ```python
   # Check first
   result = pm.update_system(dry_run=True)
   print(result.output)

   # Then apply
   if user_confirms():
       pm.update_system(dry_run=False)
   ```

---

## Anti-Patterns

### ❌ Ignoring Return Values

```python
# Bad
pm.install(["package"])  # Ignoring result
```

### ✅ Check Results

```python
# Good
result = pm.install(["package"])
if not result.success:
    handle_error(result)
```

---

### ❌ Assuming All-or-Nothing

```python
# Bad
result = pm.install(["pkg1", "pkg2"])
if result.success:
    # Assumes both installed
    use_pkg1()
    use_pkg2()
```

### ✅ Check Individual Packages

```python
# Good
result = pm.install(["pkg1", "pkg2"])
if "pkg1" in result.packages_installed:
    use_pkg1()
if "pkg2" in result.packages_installed:
    use_pkg2()
```

---

**Next:** [Examples](examples.md) | [Troubleshooting](troubleshooting.md)
