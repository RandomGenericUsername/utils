"""Base class for Debian/Ubuntu package managers."""

import re
import subprocess
from abc import ABC

from dotfiles_package_manager.core.base import PackageManager
from dotfiles_package_manager.core.types import PackageInfo


class DebianPackageManagerBase(PackageManager, ABC):
    """
    Base class for Debian/Ubuntu package managers.

    Provides shared functionality for apt and apt-get.
    """

    def _parse_search_output(self, output: str) -> list[PackageInfo]:
        """
        Parse apt-style search output.

        Format:
            package/suite version arch
              description

        Example:
            vim/stable 2:9.0.1234-1 amd64
              Vi IMproved - enhanced vi editor
        """
        packages = []
        lines = output.strip().split("\n")

        # Regex: package/suite version arch
        pattern = r"^([\w\-\.+]+)/([\w\-]+)\s+([\w\.\-:+~]+)\s+([\w\-]+)"

        i = 0
        while i < len(lines):
            match = re.match(pattern, lines[i])
            if match:
                name = match.group(1)
                repository = match.group(2)  # suite (stable, testing, etc.)
                version = match.group(3)

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
                        # apt search doesn't show installed status
                        installed=False,
                    )
                )

            i += 1

        return packages

    def _parse_package_info_output(self, output: str) -> PackageInfo | None:
        """
        Parse apt-style package info output.

        Format:
            Package: vim
            Version: 2:9.0.1234-1
            Priority: optional
            Section: editors
            ...
        """
        if not output.strip():
            return None

        info = {}
        for line in output.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                info[key.strip().lower()] = value.strip()

        if "package" not in info:
            return None

        # Parse dependencies (comma-separated list)
        dependencies = []
        if "depends" in info:
            deps_str = info["depends"]
            if deps_str:
                # Split by comma and clean up
                dependencies = [
                    d.strip().split()[0] for d in deps_str.split(",")
                ]

        return PackageInfo(
            name=info.get("package", ""),
            version=info.get("version"),
            description=info.get("description"),
            repository=info.get("section"),  # Use section as repository
            installed="status" in info and "installed" in info["status"],
            size=info.get("installed-size"),
            dependencies=dependencies,
        )

    def _run_command(
        self,
        command: list[str],
        check: bool = True,
        timeout: int = 300,
        capture_output: bool = True,
    ) -> subprocess.CompletedProcess:
        """
        Run a command and return the result.

        Args:
            command: Command and arguments to run
            check: Whether to raise on non-zero exit
            timeout: Command timeout in seconds
            capture_output: Whether to capture stdout/stderr

        Returns:
            CompletedProcess instance
        """
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
