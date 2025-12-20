"""APT package manager implementation."""

import shutil
from pathlib import Path

from dotfiles_package_manager.core.base import PackageManagerError
from dotfiles_package_manager.core.types import (
    InstallResult,
    PackageInfo,
    PackageManagerType,
    SearchResult,
)
from dotfiles_package_manager.implementations.debian.base import (
    DebianPackageManagerBase,
)


class AptPackageManager(DebianPackageManagerBase):
    """APT package manager implementation for Debian/Ubuntu."""

    @property
    def manager_type(self) -> PackageManagerType:
        return PackageManagerType.APT

    def _find_executable(self) -> Path | None:
        """Find apt executable in PATH."""
        executable = shutil.which("apt")
        return Path(executable) if executable else None

    def install(
        self, packages: list[str], update_system: bool = False
    ) -> InstallResult:
        """Install packages using apt."""
        if not packages:
            return InstallResult(
                success=True, packages_installed=[], packages_failed=[]
            )

        # Update package lists if requested
        if update_system:
            try:
                update_cmd = ["sudo", str(self.executable_path), "update"]
                self._run_command(update_cmd, check=True)
            except Exception as e:
                return InstallResult(
                    success=False,
                    packages_installed=[],
                    packages_failed=packages.copy(),
                    error_message=f"Failed to update package lists: {e}",
                )

        # Build install command
        command = ["sudo", str(self.executable_path), "install", "-y"]
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
                # Parse output to determine which packages failed
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
        """Remove packages using apt."""
        if not packages:
            return InstallResult(
                success=True, packages_installed=[], packages_failed=[]
            )

        # Build remove command
        if remove_dependencies:
            command = ["sudo", str(self.executable_path), "autoremove", "-y"]
        else:
            command = ["sudo", str(self.executable_path), "remove", "-y"]
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
        """Search for packages using apt."""
        command = [str(self.executable_path), "search", query]

        try:
            result = self._run_command(command, check=False)
            packages = self._parse_search_output(result.stdout)

            if limit and len(packages) > limit:
                packages = packages[:limit]

            return SearchResult(
                packages=packages, query=query, total_found=len(packages)
            )

        except PackageManagerError:
            return SearchResult(packages=[], query=query, total_found=0)

    def update_system(self, dry_run: bool = False) -> InstallResult:
        """Update system packages using apt."""
        if dry_run:
            # Check for upgradeable packages
            command = [str(self.executable_path), "list", "--upgradable"]
        else:
            # Update package lists
            command = ["sudo", str(self.executable_path), "update"]

        try:
            result = self._run_command(command, check=False)

            if dry_run:
                # Count upgradeable packages
                lines = result.stdout.strip().split("\n")
                # Filter out header
                upgradeable = [ln for ln in lines if "/" in ln]
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
        """Check if a package is installed using apt."""
        command = ["dpkg", "-s", package]

        try:
            result = self._run_command(command, check=False)
            return (
                result.returncode == 0
                and "Status: install ok installed" in result.stdout
            )
        except PackageManagerError:
            return False

    def get_package_info(self, package: str) -> PackageInfo | None:
        """Get detailed package information using apt."""
        command = [str(self.executable_path), "show", package]

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
                f"Unable to locate package {package}" in error_output
                or f"E: Package '{package}' has no installation candidate"
                in error_output
            ):
                failed.append(package)
        return failed
