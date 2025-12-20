# Examples

Complete, runnable code examples for the `dotfiles_package_manager` module.

---

## Table of Contents

1. [Basic Examples](#basic-examples)
2. [Complete Scripts](#complete-scripts)
3. [Integration Examples](#integration-examples)
4. [Advanced Examples](#advanced-examples)

---

## Basic Examples

### Example 1: Simple Package Installation

```python
from dotfiles_package_manager import PackageManagerFactory

# Create package manager
pm = PackageManagerFactory.create_auto()

# Install a package
result = pm.install(["vim"])

if result.success:
    print(f"✓ Successfully installed: {', '.join(result.packages_installed)}")
else:
    print(f"✗ Installation failed")
    if result.packages_failed:
        print(f"  Failed packages: {', '.join(result.packages_failed)}")
    if result.error_message:
        print(f"  Error: {result.error_message}")
```

---

### Example 2: Search and Display Results

```python
from dotfiles_package_manager import PackageManagerFactory

pm = PackageManagerFactory.create_auto()

# Search for Python packages
result = pm.search("python", limit=10)

print(f"Found {result.total_found} packages matching '{result.query}':\n")

for pkg in result.packages:
    installed = "[installed]" if pkg.installed else ""
    print(f"{pkg.repository}/{pkg.name} {pkg.version} {installed}")
    if pkg.description:
        print(f"  {pkg.description}")
    print()
```

---

### Example 3: Check Package Status

```python
from dotfiles_package_manager import PackageManagerFactory

pm = PackageManagerFactory.create_auto()

packages_to_check = ["vim", "git", "tmux", "neovim"]

print("Package Status:")
print("-" * 50)

for pkg_name in packages_to_check:
    if pm.is_installed(pkg_name):
        info = pm.get_package_info(pkg_name)
        print(f"✓ {pkg_name:15} {info.version:15} [installed]")
    else:
        print(f"✗ {pkg_name:15} {'':15} [not installed]")
```

---

## Complete Scripts

### Example 4: Development Environment Installer

```python
#!/usr/bin/env python3
"""Install development environment."""

from dotfiles_package_manager import PackageManagerFactory, PackageManagerError
import sys


def install_dev_tools():
    """Install common development tools."""

    dev_packages = [
        "git",
        "base-devel",
        "python",
        "python-pip",
        "nodejs",
        "npm",
        "docker",
        "docker-compose",
    ]

    try:
        pm = PackageManagerFactory.create_auto()
        print(f"Using package manager: {pm.manager_type.value}\n")

        # Check what's already installed
        to_install = []
        already_installed = []

        for pkg in dev_packages:
            if pm.is_installed(pkg):
                already_installed.append(pkg)
            else:
                to_install.append(pkg)

        if already_installed:
            print(f"Already installed: {', '.join(already_installed)}\n")

        if not to_install:
            print("All packages already installed!")
            return 0

        # Install missing packages
        print(f"Installing: {', '.join(to_install)}\n")
        result = pm.install(to_install, update_system=True)

        if result.success:
            print(f"\n✓ Successfully installed all packages!")
            return 0
        elif result.packages_installed:
            print(f"\n⚠ Partial success:")
            print(f"  Installed: {', '.join(result.packages_installed)}")
            print(f"  Failed: {', '.join(result.packages_failed)}")
            return 1
        else:
            print(f"\n✗ Installation failed: {result.error_message}")
            return 1

    except PackageManagerError as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(install_dev_tools())
```

---

### Example 5: Interactive Package Manager CLI

```python
#!/usr/bin/env python3
"""Interactive package manager CLI."""

from dotfiles_package_manager import PackageManagerFactory, PackageManagerError
import sys


def main():
    """Interactive package manager CLI."""

    try:
        pm = PackageManagerFactory.create_auto()
    except PackageManagerError:
        print("No package manager available!")
        return 1

    print(f"Package Manager: {pm.manager_type.value}")
    print("=" * 50)

    while True:
        print("\nOptions:")
        print("1. Search packages")
        print("2. Install package")
        print("3. Remove package")
        print("4. Check package info")
        print("5. Update system")
        print("6. Quit")

        choice = input("\nEnter choice: ").strip()

        if choice == "1":
            query = input("Search query: ")
            result = pm.search(query, limit=20)

            if result.packages:
                print(f"\nFound {result.total_found} packages:\n")
                for pkg in result.packages:
                    status = "[installed]" if pkg.installed else ""
                    print(f"{pkg.name} {pkg.version} {status}")
                    print(f"  {pkg.description}\n")
            else:
                print("No packages found")

        elif choice == "2":
            packages = input("Package names (space-separated): ").split()
            result = pm.install(packages)

            if result.success:
                print(f"✓ Installed: {', '.join(result.packages_installed)}")
            else:
                print(f"✗ Failed: {result.error_message}")

        elif choice == "3":
            packages = input("Package names (space-separated): ").split()
            result = pm.remove(packages)

            if result.success:
                print(f"✓ Removed: {', '.join(result.packages_installed)}")
            else:
                print(f"✗ Failed: {result.error_message}")

        elif choice == "4":
            package = input("Package name: ")
            info = pm.get_package_info(package)

            if info:
                print(f"\nName: {info.name}")
                print(f"Version: {info.version}")
                print(f"Description: {info.description}")
                print(f"Repository: {info.repository}")
                print(f"Installed: {info.installed}")
                print(f"Size: {info.size}")
                print(f"Dependencies: {', '.join(info.dependencies)}")
            else:
                print("Package not found")

        elif choice == "5":
            result = pm.update_system(dry_run=True)
            print(result.output)

            if input("\nProceed with update? (y/n): ").lower() == 'y':
                result = pm.update_system(dry_run=False)
                if result.success:
                    print("✓ System updated")
                else:
                    print(f"✗ Update failed: {result.error_message}")

        elif choice == "6":
            break

        else:
            print("Invalid choice")

    return 0


if __name__ == "__main__":
    sys.exit(main())
```

---

### Example 6: Package Manager Wrapper Class

```python
"""High-level package manager wrapper."""

from dotfiles_package_manager import PackageManagerFactory, PackageManagerError
from typing import List, Optional
import logging


class PackageManagerWrapper:
    """High-level wrapper around package manager."""

    def __init__(self, prefer_aur: bool = True):
        """Initialize wrapper.

        Args:
            prefer_aur: Whether to prefer AUR helpers
        """
        self.logger = logging.getLogger(__name__)
        try:
            self.pm = PackageManagerFactory.create_auto(prefer_aur_helper=prefer_aur)
            self.logger.info(f"Using package manager: {self.pm.manager_type.value}")
        except PackageManagerError as e:
            self.logger.error(f"Failed to create package manager: {e}")
            raise

    def ensure_installed(self, packages: List[str]) -> bool:
        """Ensure packages are installed.

        Args:
            packages: List of package names

        Returns:
            True if all packages installed, False otherwise
        """
        to_install = [pkg for pkg in packages if not self.pm.is_installed(pkg)]

        if not to_install:
            self.logger.info("All packages already installed")
            return True

        self.logger.info(f"Installing: {', '.join(to_install)}")
        result = self.pm.install(to_install)

        if result.success:
            self.logger.info(f"Successfully installed: {', '.join(result.packages_installed)}")
            return True
        else:
            self.logger.error(f"Installation failed: {result.error_message}")
            if result.packages_failed:
                self.logger.error(f"Failed packages: {', '.join(result.packages_failed)}")
            return False

    def safe_remove(self, packages: List[str], remove_deps: bool = False) -> bool:
        """Safely remove packages.

        Args:
            packages: List of package names
            remove_deps: Whether to remove dependencies

        Returns:
            True if all packages removed, False otherwise
        """
        installed = [pkg for pkg in packages if self.pm.is_installed(pkg)]

        if not installed:
            self.logger.info("No packages to remove")
            return True

        self.logger.info(f"Removing: {', '.join(installed)}")
        result = self.pm.remove(installed, remove_dependencies=remove_deps)

        if result.success:
            self.logger.info(f"Successfully removed: {', '.join(result.packages_installed)}")
            return True
        else:
            self.logger.error(f"Removal failed: {result.error_message}")
            return False

    def find_package(self, query: str) -> Optional[str]:
        """Find exact package name from query.

        Args:
            query: Search query

        Returns:
            Package name if found, None otherwise
        """
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


# Usage example
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    wrapper = PackageManagerWrapper()

    # Ensure packages installed
    wrapper.ensure_installed(["vim", "git", "tmux"])

    # Find and install
    pkg_name = wrapper.find_package("neovim")
    if pkg_name:
        wrapper.ensure_installed([pkg_name])
```

---

## Integration Examples

### Example 7: Dotfiles Installer Integration

```python
"""Dotfiles installer with package management."""

from dotfiles_package_manager import PackageManagerFactory, PackageManagerError
import logging


class DotfilesInstaller:
    """Install dotfiles and dependencies."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        try:
            self.pm = PackageManagerFactory.create_auto()
        except PackageManagerError as e:
            self.logger.error(f"No package manager available: {e}")
            raise

    def install_dependencies(self):
        """Install required packages."""
        required_packages = [
            "git",
            "stow",
            "tmux",
            "zsh",
            "neovim",
        ]

        self.logger.info("Installing dependencies...")
        result = self.pm.install(required_packages, update_system=True)

        if result.success:
            self.logger.info("✓ All dependencies installed")
            return True
        else:
            self.logger.error(f"Failed to install dependencies: {result.error_message}")
            return False

    def install(self):
        """Run full installation."""
        # Install dependencies
        if not self.install_dependencies():
            return False

        # Install dotfiles (stow, etc.)
        # ...

        return True


# Usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    installer = DotfilesInstaller()
    installer.install()
```

---

## Advanced Examples

### Example 8: Conditional Package Installation

```python
"""Install preferred package from list."""

from dotfiles_package_manager import PackageManagerFactory


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


# Usage
pm = PackageManagerFactory.create_auto()

# Install preferred editor
editor = install_preferred(pm, ["neovim", "vim", "vi"])

# Install preferred shell
shell = install_preferred(pm, ["zsh", "fish", "bash"])
```

---

### Example 9: Batch Installation with Progress

```python
"""Install packages with progress reporting."""

from dotfiles_package_manager import PackageManagerFactory


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
pm = PackageManagerFactory.create_auto()
packages = ["vim", "git", "tmux", "neovim", "zsh"]
install_with_progress(pm, packages)
```

---

**Next:** [Troubleshooting](troubleshooting.md) | [API Reference](api_reference.md)
