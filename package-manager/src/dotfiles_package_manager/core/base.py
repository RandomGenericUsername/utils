"""Base package manager interface and exceptions."""

import os
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path

from .types import InstallResult, PackageInfo, PackageManagerType, SearchResult


class PackageManagerError(Exception):
    """Base exception for package manager operations."""

    def __init__(
        self,
        message: str,
        command: str | None = None,
        exit_code: int | None = None,
    ):
        super().__init__(message)
        self.command = command
        self.exit_code = exit_code


class PackageNotFoundError(PackageManagerError):
    """Raised when a package is not found."""

    pass


class PackageInstallationError(PackageManagerError):
    """Raised when package installation fails."""

    pass


class PackageManagerTimeoutError(PackageManagerError):
    """Raised when a package manager command times out."""

    def __init__(
        self,
        message: str,
        command: str | None = None,
        timeout: int | None = None,
    ):
        super().__init__(message, command)
        self.timeout = timeout


class PackageManagerLockError(PackageManagerError):
    """Raised when the package manager database is locked."""

    def __init__(
        self,
        message: str,
        lock_file: str | None = None,
        is_stale: bool = False,
    ):
        super().__init__(message)
        self.lock_file = lock_file
        self.is_stale = is_stale


class PackageManager(ABC):
    """Abstract base class for package managers."""

    def __init__(self, executable_path: Path | None = None):
        """
        Initialize package manager.

        Args:
            executable_path: Path to the package manager executable
        """
        self.executable_path = executable_path or self._find_executable()
        if not self.executable_path or not self.executable_path.exists():
            raise PackageManagerError(
                "Package manager executable not found: "
                f"{self.manager_type.value}"
            )

    @property
    @abstractmethod
    def manager_type(self) -> PackageManagerType:
        """Get the package manager type."""
        pass

    @abstractmethod
    def _find_executable(self) -> Path | None:
        """Find the package manager executable in PATH."""
        pass

    @abstractmethod
    def install(
        self,
        packages: list[str],
        update_system: bool = False,
        timeout: int | None = None,
    ) -> InstallResult:
        """
        Install packages.

        Args:
            packages: List of package names to install
            update_system: Whether to update system before installing
            timeout: Command timeout in seconds (None uses implementation default)

        Returns:
            InstallResult with installation details
        """
        pass

    @abstractmethod
    def remove(
        self, packages: list[str], remove_dependencies: bool = False
    ) -> InstallResult:
        """
        Remove packages.

        Args:
            packages: List of package names to remove
            remove_dependencies: Whether to remove unused dependencies

        Returns:
            InstallResult with removal details
        """
        pass

    @abstractmethod
    def search(self, query: str, limit: int | None = None) -> SearchResult:
        """
        Search for packages.

        Args:
            query: Search query
            limit: Maximum number of results to return

        Returns:
            SearchResult with found packages
        """
        pass

    @abstractmethod
    def update_system(self, dry_run: bool = False) -> InstallResult:
        """
        Update the system packages.

        Args:
            dry_run: If True, only check for updates without applying them

        Returns:
            InstallResult with update details
        """
        pass

    @abstractmethod
    def is_installed(self, package: str) -> bool:
        """
        Check if a package is installed.

        Args:
            package: Package name to check

        Returns:
            True if package is installed, False otherwise
        """
        pass

    @abstractmethod
    def get_package_info(self, package: str) -> PackageInfo | None:
        """
        Get detailed information about a package.

        Args:
            package: Package name

        Returns:
            PackageInfo if found, None otherwise
        """
        pass

    def _run_command(
        self,
        command: list[str],
        capture_output: bool = True,
        check: bool = True,
        timeout: int | None = None,
    ) -> subprocess.CompletedProcess:
        """
        Run a command with proper error handling.

        Args:
            command: Command and arguments to run
            capture_output: Whether to capture stdout/stderr
            check: Whether to raise exception on non-zero exit code
            timeout: Timeout in seconds (None for no timeout)

        Returns:
            CompletedProcess result

        Raises:
            PackageManagerError: If command fails and check=True
        """
        try:
            # Use explicit PIPE instead of capture_output to ensure
            # output is captured even with sudo/TTY scenarios.
            # Set TERM=dumb to prevent progress bars and TTY detection
            # that interfere with output capture.
            env = os.environ.copy()
            env["TERM"] = "dumb"

            if capture_output:
                result = subprocess.run(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.DEVNULL,
                    text=True,
                    check=check,
                    timeout=timeout,
                    env=env,
                )
            else:
                result = subprocess.run(
                    command,
                    text=True,
                    check=check,
                    timeout=timeout,
                    env=env,
                )
            return result
        except subprocess.TimeoutExpired as e:
            raise PackageManagerTimeoutError(
                f"Command timed out after {timeout}s: {' '.join(command)}",
                command=" ".join(command),
                timeout=timeout,
            ) from e
        except subprocess.CalledProcessError as e:
            raise PackageManagerError(
                f"Command failed: {' '.join(command)}",
                command=" ".join(command),
                exit_code=e.returncode,
            ) from e
        except FileNotFoundError as e:
            raise PackageManagerError(
                f"Executable not found: {command[0]}",
                command=" ".join(command),
            ) from e
