"""DNF package manager implementation."""

import shutil
from pathlib import Path

from dotfiles_package_manager.core.base import (
    PackageManagerError,
    PackageManagerTimeoutError,
    PackageManagerLockError,
)
from dotfiles_package_manager.core.types import (
    InstallResult,
    PackageInfo,
    PackageManagerType,
    SearchResult,
)
from dotfiles_package_manager.implementations.redhat.base import (
    RedHatPackageManagerBase,
)


class DnfPackageManager(RedHatPackageManagerBase):
    """DNF package manager implementation for Fedora/RHEL."""

    @property
    def manager_type(self) -> PackageManagerType:
        return PackageManagerType.DNF

    def _find_executable(self) -> Path | None:
        """Find dnf executable in PATH."""
        executable = shutil.which("dnf")
        return Path(executable) if executable else None

    def install(
        self,
        packages: list[str],
        update_system: bool = False,
        timeout: int | None = None,
    ) -> InstallResult:
        """Install packages using dnf.

        Args:
            packages: List of package names to install
            update_system: Whether to perform system upgrade first
            timeout: Command timeout in seconds (None for no timeout)

        Returns:
            InstallResult with success status and package lists
        """
        if not packages:
            return InstallResult(
                success=True, packages_installed=[], packages_failed=[]
            )

        # Check for lock file before attempting installation
        lock_result = self.check_lock()
        if lock_result.is_locked:
            raise PackageManagerLockError(
                lock_result.message,
                lock_file=str(lock_result.lock_file) if lock_result.lock_file else None,
                is_stale=lock_result.is_stale,
            )

        # Update package metadata if requested
        if update_system:
            try:
                update_cmd = [
                    "sudo",
                    str(self.executable_path),
                    "check-update",
                ]
                self._run_command(
                    update_cmd, check=False, timeout=timeout
                )  # check-update returns 100 if updates available
            except Exception:
                pass  # Continue even if check-update fails

        # Build install command
        command = ["sudo", str(self.executable_path), "install", "-y"]
        command.extend(packages)

        try:
            result = self._run_command(command, check=False, timeout=timeout)

            # Combine stdout and stderr for parsing - dnf may output
            # errors to either stream
            combined_output = (result.stdout or "") + (result.stderr or "")

            # Always check for failed packages, even on returncode 0
            # dnf may succeed installing some packages while others fail
            failed_packages = self._parse_failed_packages(
                combined_output, packages
            )
            successful_packages = [
                pkg for pkg in packages if pkg not in failed_packages
            ]

            if result.returncode == 0 and not failed_packages:
                return InstallResult(
                    success=True,
                    packages_installed=packages.copy(),
                    packages_failed=[],
                    output=result.stdout,
                )
            else:
                return InstallResult(
                    success=len(successful_packages) > 0,
                    packages_installed=successful_packages,
                    packages_failed=failed_packages,
                    output=result.stdout,
                    error_message=result.stderr or combined_output,
                )

        except PackageManagerTimeoutError as e:
            return InstallResult(
                success=False,
                packages_installed=[],
                packages_failed=packages.copy(),
                error_message=f"Installation timed out after {e.timeout} seconds. "
                              f"Consider increasing install_timeout in dotfiles.toml",
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
        """Remove packages using dnf."""
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

            # Combine stdout and stderr for parsing
            combined_output = (result.stdout or "") + (result.stderr or "")

            # Always check for failed packages
            failed_packages = self._parse_failed_packages(
                combined_output, packages
            )
            successful_packages = [
                pkg for pkg in packages if pkg not in failed_packages
            ]

            if result.returncode == 0 and not failed_packages:
                return InstallResult(
                    success=True,
                    packages_installed=packages.copy(),
                    packages_failed=[],
                    output=result.stdout,
                )
            else:
                return InstallResult(
                    success=len(successful_packages) > 0,
                    packages_installed=successful_packages,
                    packages_failed=failed_packages,
                    output=result.stdout,
                    error_message=result.stderr or combined_output,
                )

        except PackageManagerError as e:
            return InstallResult(
                success=False,
                packages_installed=[],
                packages_failed=packages.copy(),
                error_message=str(e),
            )

    def search(self, query: str, limit: int | None = None) -> SearchResult:
        """Search for packages using dnf."""
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
        """Update system packages using dnf."""
        if dry_run:
            # Check for updates
            command = [str(self.executable_path), "check-update"]
        else:
            # Update package metadata
            command = ["sudo", str(self.executable_path), "check-update"]

        try:
            result = self._run_command(command, check=False)

            if dry_run:
                # dnf check-update returns 100 if updates are available
                if result.returncode == 100:
                    lines = result.stdout.strip().split("\n")
                    upgradeable = [
                        ln
                        for ln in lines
                        if ln and not ln.startswith(("Last", "Obsoleting"))
                    ]
                    return InstallResult(
                        success=True,
                        packages_installed=[],
                        packages_failed=[],
                        output=(
                            f"Found {len(upgradeable)} upgradeable packages"
                        ),
                    )
                else:
                    return InstallResult(
                        success=True,
                        packages_installed=[],
                        packages_failed=[],
                        output="System is up to date",
                    )
            else:
                return InstallResult(
                    success=result.returncode
                    in (0, 100),  # 100 means updates available
                    packages_installed=[],
                    packages_failed=[],
                    output=result.stdout,
                    error_message=(
                        result.stderr
                        if result.returncode not in (0, 100)
                        else None
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
        """Check if a package is installed using dnf."""
        command = [str(self.executable_path), "list", "installed", package]

        try:
            result = self._run_command(command, check=False)
            return result.returncode == 0
        except PackageManagerError:
            return False

    def get_package_info(self, package: str) -> PackageInfo | None:
        """Get detailed package information using dnf."""
        command = [str(self.executable_path), "info", package]

        try:
            result = self._run_command(command, check=False)
            if result.returncode == 0:
                return self._parse_package_info_output(result.stdout)
        except PackageManagerError:
            pass

        return None

    def _parse_failed_packages(
        self, error_output: str | None, packages: list[str]
    ) -> list[str]:
        """Parse error output to identify failed packages.

        Handles multiple dnf error formats:
        - "No match for argument: package_name"
        - "Unable to find a match: pkg1 pkg2 pkg3" (multiple on one line)
        """
        failed: list[str] = []
        if not error_output:
            return failed

        for package in packages:
            # Check for single package error format
            if f"No match for argument: {package}" in error_output:
                failed.append(package)
                continue

            # Check for multi-package format: "Unable to find a match: p1 p2"
            for line in error_output.splitlines():
                if "Unable to find a match:" in line:
                    # Extract packages after the colon
                    failed_part = line.split("Unable to find a match:")[-1]
                    failed_pkgs = failed_part.split()
                    if package in failed_pkgs:
                        failed.append(package)
                        break

        return failed
