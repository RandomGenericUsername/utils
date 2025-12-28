"""Base class for RedHat/Fedora package managers."""

import os
import re
import subprocess
from abc import ABC

from dotfiles_package_manager.core.base import PackageManager
from dotfiles_package_manager.core.types import PackageInfo


class RedHatPackageManagerBase(PackageManager, ABC):
    """
    Base class for RedHat/Fedora package managers.

    Provides shared functionality for dnf and yum.
    """

    def _parse_search_output(self, output: str) -> list[PackageInfo]:
        """
        Parse dnf/yum-style search output.

        Format:
            ==================== Name Matched: query ====================
            package.arch : summary
                description

        Example:
            vim-enhanced.x86_64 : A version of the VIM editor
                VIM (Vi IMproved) is an updated and improved version...
        """
        packages = []
        lines = output.strip().split("\n")

        # Regex: package.arch : summary
        pattern = r"^([\w\-\.+]+)\.([\w\-]+)\s*:\s*(.+)$"

        i = 0
        while i < len(lines):
            # Skip header lines
            if lines[i].startswith("="):
                i += 1
                continue

            match = re.match(pattern, lines[i])
            if match:
                name = match.group(1)
                match.group(2)
                summary = match.group(3)

                # Next line might be description
                description = summary
                if (
                    i + 1 < len(lines)
                    and not re.match(pattern, lines[i + 1])
                    and not lines[i + 1].startswith("=")
                ):
                    description = lines[i + 1].strip()
                    i += 1

                packages.append(
                    PackageInfo(
                        name=name,
                        version=None,  # dnf search doesn't show version
                        description=description,
                        repository=None,
                        installed=False,
                    )
                )

            i += 1

        return packages

    def _parse_package_info_output(self, output: str) -> PackageInfo | None:
        """
        Parse dnf/yum-style package info output.

        Format:
            Name         : vim-enhanced
            Version      : 9.0.1234
            Release      : 1.fc38
            Architecture : x86_64
            Size         : 1.8 M
            Source       : vim-9.0.1234-1.fc38.src.rpm
            Repository   : fedora
            Summary      : A version of the VIM editor
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

        # Combine version and release
        version = info.get("version", "")
        if "release" in info:
            version = f"{version}-{info['release']}"

        # Parse dependencies (comma-separated list)
        dependencies = []
        if "requires" in info:
            deps_str = info["requires"]
            if deps_str:
                dependencies = [d.strip() for d in deps_str.split(",")]

        return PackageInfo(
            name=info.get("name", ""),
            version=version if version else None,
            description=info.get("summary") or info.get("description"),
            repository=info.get("repository") or info.get("repo"),
            installed="from repo" in info and info["from repo"] == "@System",
            size=info.get("size") or info.get("install size"),
            dependencies=dependencies,
        )

    def check_lock(self):
        """Check for DNF/YUM locks.

        Returns:
            LockCheckResult with lock status and details
        """
        from dotfiles_package_manager.core.lock import check_dnf_lock
        return check_dnf_lock()

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
            # Set TERM=dumb to prevent progress bars and TTY detection
            # that interfere with output capture
            env = os.environ.copy()
            env["TERM"] = "dumb"

            if capture_output:
                return subprocess.run(
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
                return subprocess.run(
                    command,
                    text=True,
                    check=check,
                    timeout=timeout,
                    env=env,
                )
        except subprocess.TimeoutExpired as e:
            from dotfiles_package_manager.core.base import PackageManagerTimeoutError
            raise PackageManagerTimeoutError(
                f"Command timed out after {timeout} seconds: {' '.join(command)}",
                command=" ".join(command),
                timeout=timeout,
            ) from e
