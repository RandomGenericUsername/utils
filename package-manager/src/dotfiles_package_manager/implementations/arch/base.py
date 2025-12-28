"""Base class for Arch Linux package managers."""

import re
import subprocess
from abc import ABC

from dotfiles_package_manager.core.base import PackageManager
from dotfiles_package_manager.core.types import PackageInfo


class ArchPackageManagerBase(PackageManager, ABC):
    """
    Base class for Arch Linux package managers.

    Provides shared functionality for pacman, yay, and paru:
    - Output parsing (same format for all)
    - Common command patterns
    - Shared error handling
    """

    def _parse_search_output(self, output: str) -> list[PackageInfo]:
        """
        Parse pacman-style search output.

        Format:
            repository/package version [installed]
                description

        Example:
            core/vim 9.0.1234-1
                Vi Improved, a highly configurable text editor
            aur/google-chrome 114.0-1 [installed]
                The popular web browser by Google
        """
        packages = []
        lines = output.strip().split("\n")

        # Regex: repository/package version [installed]?
        pattern = r"^([\w-]+)/([\w\-\.]+)\s+([\w\.\-:]+)(?:\s+\[installed\])?"

        i = 0
        while i < len(lines):
            match = re.match(pattern, lines[i])
            if match:
                repository = match.group(1)
                name = match.group(2)
                version = match.group(3)
                installed = "[installed]" in lines[i]

                # Next line is description (if exists)
                description = None
                if i + 1 < len(lines) and not re.match(pattern, lines[i + 1]):
                    description = lines[i + 1].strip()
                    i += 1

                packages.append(
                    PackageInfo(
                        name=name,
                        version=version,
                        description=description,
                        repository=repository,
                        installed=installed,
                    )
                )

            i += 1

        return packages

    def _parse_package_info_output(self, output: str) -> PackageInfo | None:
        """
        Parse pacman-style package info output.

        Format:
            Name            : vim
            Version         : 9.0.1234-1
            Description     : Vi Improved...
            Repository      : core
            ...
        """
        if not output.strip():
            return None

        info = {}
        for line in output.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                info[key.strip().lower()] = value.strip()

        if "name" not in info:
            return None

        # Parse dependencies (space-separated list)
        dependencies = []
        if "depends on" in info:
            deps_str = info["depends on"]
            if deps_str and deps_str.lower() != "none":
                dependencies = [d.strip() for d in deps_str.split()]

        return PackageInfo(
            name=info.get("name", ""),
            version=info.get("version"),
            description=info.get("description"),
            repository=info.get("repository"),
            installed="installed size" in info,
            size=info.get("installed size"),
            dependencies=dependencies,
        )

    def check_lock(self):
        """Check for pacman database lock.

        Returns:
            LockCheckResult with lock status and details
        """
        from dotfiles_package_manager.core.lock import check_pacman_lock
        return check_pacman_lock()

    def _run_command(
        self,
        command: list[str],
        capture_output: bool = True,
        check: bool = True,
        timeout: int | None = None,
    ) -> subprocess.CompletedProcess:
        """
        Run a command and return the result.

        Args:
            command: Command and arguments to run
            capture_output: Whether to capture stdout/stderr
            check: Whether to raise on non-zero exit
            timeout: Command timeout in seconds (None for no timeout)

        Returns:
            CompletedProcess instance

        Raises:
            PackageManagerTimeoutError: If command times out
        """
        try:
            # If command starts with sudo, don't capture to allow password input
            if command and command[0] == "sudo":
                return subprocess.run(
                    command,
                    text=True,
                    check=check,
                    timeout=timeout,
                )
            else:
                return subprocess.run(
                    command,
                    capture_output=capture_output,
                    text=True,
                    check=check,
                    timeout=timeout,
                )
        except subprocess.TimeoutExpired as e:
            from dotfiles_package_manager.core.base import PackageManagerTimeoutError
            raise PackageManagerTimeoutError(
                f"Command timed out after {timeout} seconds: {' '.join(command)}",
                command=" ".join(command),
                timeout=timeout,
            ) from e
