"""Yay AUR helper implementation."""

import shutil
from pathlib import Path

from dotfiles_package_manager.core.base import PackageManagerError
from dotfiles_package_manager.core.types import (
    InstallResult,
    PackageInfo,
    PackageManagerType,
    SearchResult,
)
from dotfiles_package_manager.implementations.arch.base import (
    ArchPackageManagerBase,
)


class YayPackageManager(ArchPackageManagerBase):
    """Yay AUR helper implementation for Arch Linux."""

    @property
    def manager_type(self) -> PackageManagerType:
        return PackageManagerType.YAY

    def _find_executable(self) -> Path | None:
        """Find yay executable in PATH."""
        executable = shutil.which("yay")
        return Path(executable) if executable else None

    def install(
        self, packages: list[str], update_system: bool = False
    ) -> InstallResult:
        """Install packages using yay."""
        if not packages:
            return InstallResult(
                success=True, packages_installed=[], packages_failed=[]
            )

        # Perform full system upgrade first if requested
        # This prevents partial upgrades which can break dependencies on Arch
        if update_system:
            upgrade_result = self.update_system(dry_run=False)
            if not upgrade_result.success:
                error_msg = (
                    f"System upgrade failed: {upgrade_result.error_message}"
                )
                return InstallResult(
                    success=False,
                    packages_installed=[],
                    packages_failed=packages.copy(),
                    error_message=error_msg,
                )

        # Build command (no sudo - yay handles it internally)
        command = [str(self.executable_path), "-S", "--noconfirm"]
        command.extend(packages)

        try:
            result = self._run_command(command, check=False)

            if result.returncode == 0:
                return InstallResult(
                    success=True,
                    packages_installed=packages.copy(),
                    packages_failed=[],
                    output=result.stdout,
                )
            else:
                failed_packages = self._parse_failed_packages(
                    result.stderr, packages
                )
                successful_packages = [
                    pkg for pkg in packages if pkg not in failed_packages
                ]

                return InstallResult(
                    success=len(successful_packages) > 0,
                    packages_installed=successful_packages,
                    packages_failed=failed_packages,
                    output=result.stdout,
                    error_message=result.stderr,
                )

        except PackageManagerError as e:
            return InstallResult(
                success=False,
                packages_installed=[],
                packages_failed=packages.copy(),
                error_message=str(e),
            )

    def remove(
        self, packages: list[str], remove_dependencies: bool = False
    ) -> InstallResult:
        """Remove packages using yay."""
        if not packages:
            return InstallResult(
                success=True, packages_installed=[], packages_failed=[]
            )

        # Build command (no sudo - yay handles it internally)
        command = [str(self.executable_path), "-R", "--noconfirm"]
        if remove_dependencies:
            command.append("-s")
        command.extend(packages)

        try:
            result = self._run_command(command, check=False)

            if result.returncode == 0:
                return InstallResult(
                    success=True,
                    packages_installed=packages.copy(),
                    packages_failed=[],
                    output=result.stdout,
                )
            else:
                failed_packages = self._parse_failed_packages(
                    result.stderr, packages
                )
                successful_packages = [
                    pkg for pkg in packages if pkg not in failed_packages
                ]

                return InstallResult(
                    success=len(successful_packages) > 0,
                    packages_installed=successful_packages,
                    packages_failed=failed_packages,
                    output=result.stdout,
                    error_message=result.stderr,
                )

        except PackageManagerError as e:
            return InstallResult(
                success=False,
                packages_installed=[],
                packages_failed=packages.copy(),
                error_message=str(e),
            )

    def search(self, query: str, limit: int | None = None) -> SearchResult:
        """Search for packages using yay."""
        command = [str(self.executable_path), "-Ss", query]

        try:
            result = self._run_command(command, check=True)
            packages = self._parse_search_output(result.stdout)

            if limit and len(packages) > limit:
                packages = packages[:limit]

            return SearchResult(
                packages=packages, query=query, total_found=len(packages)
            )

        except PackageManagerError:
            return SearchResult(packages=[], query=query, total_found=0)

    def update_system(self, dry_run: bool = False) -> InstallResult:
        """Update system packages using yay.

        Performs a full system upgrade (-Syu) to prevent partial upgrades.
        Partial upgrades (-Sy) are not supported on Arch Linux and can cause
        dependency breakage.
        """
        if dry_run:
            command = [str(self.executable_path), "-Qu"]
        else:
            # Use -Syu for full system upgrade (sync + upgrade)
            # Never use -Sy alone as it causes partial upgrades
            command = [str(self.executable_path), "-Syu", "--noconfirm"]

        try:
            result = self._run_command(command, check=False)

            if dry_run:
                upgradeable = (
                    result.stdout.strip().split("\n")
                    if result.stdout.strip()
                    else []
                )
                return InstallResult(
                    success=result.returncode == 0,
                    packages_installed=[],
                    packages_failed=[],
                    output=(
                        f"Found {len(upgradeable)} upgradeable packages"
                        if upgradeable
                        else "System is up to date"
                    ),
                    error_message=(
                        result.stderr if result.returncode != 0 else None
                    ),
                )
            else:
                return InstallResult(
                    success=result.returncode == 0,
                    packages_installed=[],
                    packages_failed=[],
                    output=result.stdout,
                    error_message=(
                        result.stderr if result.returncode != 0 else None
                    ),
                )

        except PackageManagerError as e:
            return InstallResult(
                success=False,
                packages_installed=[],
                packages_failed=[],
                error_message=str(e),
            )

    def is_installed(self, package: str) -> bool:
        """Check if a package is installed using yay."""
        command = [str(self.executable_path), "-Q", package]

        try:
            result = self._run_command(command, check=False)
            return result.returncode == 0
        except PackageManagerError:
            return False

    def get_package_info(self, package: str) -> PackageInfo | None:
        """Get detailed package information using yay."""
        # Try installed packages first
        command = [str(self.executable_path), "-Qi", package]

        try:
            result = self._run_command(command, check=False)
            if result.returncode == 0:
                return self._parse_package_info_output(result.stdout)
        except PackageManagerError:
            pass

        # Try repository packages
        command = [str(self.executable_path), "-Si", package]

        try:
            result = self._run_command(command, check=False)
            if result.returncode == 0:
                return self._parse_package_info_output(result.stdout)
        except PackageManagerError:
            pass

        return None

    def _parse_failed_packages(
        self, error_output: str, packages: list[str]
    ) -> list[str]:
        """Parse error output to identify failed packages."""
        failed = []
        for package in packages:
            if (
                f"error: target not found: {package}" in error_output
                or f"could not find package {package}" in error_output
            ):
                failed.append(package)
        return failed
