"""Shared fixtures and utilities for package manager tests."""

import subprocess
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from dotfiles_package_manager.core.types import (
    DistributionFamily,
    InstallResult,
    PackageInfo,
    PackageManagerType,
    SearchResult,
)


@pytest.fixture
def mock_subprocess_run():
    """Mock subprocess.run for command execution tests."""
    with patch("subprocess.run") as mock_run:
        # Default successful result
        mock_run.return_value = subprocess.CompletedProcess(
            args=["test"],
            returncode=0,
            stdout="Success",
            stderr="",
        )
        yield mock_run


@pytest.fixture
def mock_shutil_which():
    """Mock shutil.which for executable detection tests."""
    with patch("shutil.which") as mock_which:
        yield mock_which


@pytest.fixture
def mock_os_release_arch(tmp_path):
    """Mock /etc/os-release for Arch Linux."""
    os_release = tmp_path / "os-release"
    os_release.write_text(
        """NAME="Arch Linux"
ID=arch
ID_LIKE=archlinux
PRETTY_NAME="Arch Linux"
"""
    )
    with patch("pathlib.Path.open", os_release.open):
        yield os_release


@pytest.fixture
def mock_os_release_debian(tmp_path):
    """Mock /etc/os-release for Debian/Ubuntu."""
    os_release = tmp_path / "os-release"
    os_release.write_text(
        """NAME="Ubuntu"
ID=ubuntu
ID_LIKE=debian
PRETTY_NAME="Ubuntu 22.04 LTS"
"""
    )
    with patch("pathlib.Path.open", os_release.open):
        yield os_release


@pytest.fixture
def mock_os_release_redhat(tmp_path):
    """Mock /etc/os-release for RedHat/Fedora."""
    os_release = tmp_path / "os-release"
    os_release.write_text(
        """NAME="Fedora Linux"
ID=fedora
ID_LIKE=rhel
PRETTY_NAME="Fedora Linux 38"
"""
    )
    with patch("pathlib.Path.open", os_release.open):
        yield os_release


@pytest.fixture
def sample_package_info():
    """Create a sample PackageInfo object."""
    return PackageInfo(
        name="test-package",
        version="1.0.0",
        description="A test package",
        repository="core",
        installed=True,
        size="1.5 MB",
        dependencies=["dep1", "dep2"],
    )


@pytest.fixture
def sample_install_result_success():
    """Create a successful InstallResult."""
    return InstallResult(
        success=True,
        packages_installed=["package1", "package2"],
        packages_failed=[],
        output="Successfully installed packages",
    )


@pytest.fixture
def sample_install_result_failure():
    """Create a failed InstallResult."""
    return InstallResult(
        success=False,
        packages_installed=[],
        packages_failed=["package1", "package2"],
        error_message="Failed to install packages",
    )


@pytest.fixture
def sample_search_result():
    """Create a sample SearchResult."""
    packages = [
        PackageInfo(
            name="package1",
            version="1.0.0",
            description="First package",
            repository="core",
        ),
        PackageInfo(
            name="package2",
            version="2.0.0",
            description="Second package",
            repository="extra",
        ),
    ]
    return SearchResult(
        packages=packages,
        query="test",
        total_found=2,
    )


@pytest.fixture
def mock_pacman_executable(tmp_path):
    """Create a mock pacman executable."""
    executable = tmp_path / "pacman"
    executable.write_text("#!/bin/bash\necho 'mock pacman'")
    executable.chmod(0o755)
    return executable


@pytest.fixture
def mock_apt_executable(tmp_path):
    """Create a mock apt executable."""
    executable = tmp_path / "apt"
    executable.write_text("#!/bin/bash\necho 'mock apt'")
    executable.chmod(0o755)
    return executable


@pytest.fixture
def mock_dnf_executable(tmp_path):
    """Create a mock dnf executable."""
    executable = tmp_path / "dnf"
    executable.write_text("#!/bin/bash\necho 'mock dnf'")
    executable.chmod(0o755)
    return executable


@pytest.fixture
def mock_yay_executable(tmp_path):
    """Create a mock yay executable."""
    executable = tmp_path / "yay"
    executable.write_text("#!/bin/bash\necho 'mock yay'")
    executable.chmod(0o755)
    return executable


@pytest.fixture
def mock_paru_executable(tmp_path):
    """Create a mock paru executable."""
    executable = tmp_path / "paru"
    executable.write_text("#!/bin/bash\necho 'mock paru'")
    executable.chmod(0o755)
    return executable


def create_mock_completed_process(
    returncode: int = 0,
    stdout: str = "",
    stderr: str = "",
    args: list[str] | None = None,
) -> subprocess.CompletedProcess:
    """
    Helper function to create a mock CompletedProcess.

    Args:
        returncode: Exit code
        stdout: Standard output
        stderr: Standard error
        args: Command arguments

    Returns:
        CompletedProcess instance
    """
    return subprocess.CompletedProcess(
        args=args or ["test"],
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
    )


def mock_package_manager_command(
    mock_run: Mock,
    returncode: int = 0,
    stdout: str = "",
    stderr: str = "",
) -> None:
    """
    Configure a mock subprocess.run for package manager commands.

    Args:
        mock_run: The mocked subprocess.run
        returncode: Exit code to return
        stdout: Standard output to return
        stderr: Standard error to return
    """
    mock_run.return_value = create_mock_completed_process(
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
    )


@pytest.fixture
def mock_detect_distribution():
    """Mock distribution detection."""
    with patch(
        "dotfiles_package_manager.core.factory.detect_distribution_family"
    ) as mock_detect:
        mock_detect.return_value = DistributionFamily.ARCH
        yield mock_detect


# Helper classes for testing


class MockPackageManager:
    """Mock package manager for testing."""

    def __init__(self, manager_type: PackageManagerType):
        self.manager_type = manager_type
        self.executable_path = Path(f"/usr/bin/{manager_type.value}")

    def install(
        self, packages: list[str], update_system: bool = False
    ) -> InstallResult:
        return InstallResult(
            success=True,
            packages_installed=packages,
            packages_failed=[],
        )

    def remove(
        self, packages: list[str], remove_dependencies: bool = False
    ) -> InstallResult:
        return InstallResult(
            success=True,
            packages_installed=packages,
            packages_failed=[],
        )

    def search(self, query: str, limit: int | None = None) -> SearchResult:
        return SearchResult(
            packages=[],
            query=query,
            total_found=0,
        )

    def update_system(self, dry_run: bool = False) -> InstallResult:
        return InstallResult(success=True)

    def is_installed(self, package: str) -> bool:
        return True

    def get_package_info(self, package: str) -> PackageInfo | None:
        return PackageInfo(name=package, version="1.0.0")
