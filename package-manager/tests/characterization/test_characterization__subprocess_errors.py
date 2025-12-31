"""Characterization test: Subprocess error handling.

This test freezes the CURRENT behavior when subprocess.run() raises exceptions
(e.g., FileNotFoundError, PermissionError, CalledProcessError).

Evidence:
- base.py:170-177 - _run_command wraps subprocess errors as PackageManagerError
- pacman.py:85-91 - Catches PackageManagerError and returns InstallResult with success=False
- Used in production: package_management_steps.py:282-286 catches PackageManagerError

Current Behavior (FROZEN):
- Subprocess exceptions are caught and converted to InstallResult(success=False)
- All packages are marked as failed
- Error message is preserved in error_message field
"""

from pathlib import Path
from unittest.mock import MagicMock, patch
import subprocess

import pytest

from dotfiles_package_manager.core.base import PackageManagerError
from dotfiles_package_manager.implementations.arch.pacman import (
    PacmanPackageManager,
)
from dotfiles_package_manager.implementations.arch.yay import YayPackageManager
from dotfiles_package_manager.implementations.arch.paru import (
    ParuPackageManager,
)
from dotfiles_package_manager.implementations.debian.apt import (
    AptPackageManager,
)
from dotfiles_package_manager.implementations.redhat.dnf import (
    DnfPackageManager,
)


@pytest.fixture
def mock_executable():
    """Mock finding the package manager executable."""
    with patch("shutil.which", return_value="/usr/bin/mock"):
        yield


def create_manager(manager_class):
    """Helper to create a manager instance with mocked executable."""
    mock_path = MagicMock(spec=Path)
    mock_path.exists.return_value = True

    with patch.object(
        manager_class, "_find_executable", return_value=mock_path
    ):
        return manager_class()


@pytest.mark.parametrize(
    "manager_class",
    [
        PacmanPackageManager,
        YayPackageManager,
        ParuPackageManager,
        AptPackageManager,
        DnfPackageManager,
    ],
)
def test_subprocess_file_not_found_returns_failure(
    manager_class, mock_executable
):
    """CHARACTERIZATION: FileNotFoundError propagates to caller.

    When the package manager executable is not found, the exception
    propagates. Only PackageManagerError is caught.
    """
    manager = create_manager(manager_class)

    # Simulate subprocess.run raising FileNotFoundError
    with patch(
        "subprocess.run", side_effect=FileNotFoundError("mock not found")
    ):
        # FROZEN BEHAVIOR: Exception propagates
        with pytest.raises(FileNotFoundError, match="mock not found"):
            manager.install(["vim"])


@pytest.mark.parametrize(
    "manager_class",
    [
        PacmanPackageManager,
        YayPackageManager,
        ParuPackageManager,
        AptPackageManager,
        DnfPackageManager,
    ],
)
def test_subprocess_permission_error_returns_failure(
    manager_class, mock_executable
):
    """CHARACTERIZATION: PermissionError propagates to caller.

    When sudo authentication fails or permissions are denied, the exception
    propagates. Only PackageManagerError is caught.
    """
    manager = create_manager(manager_class)

    with patch(
        "subprocess.run",
        side_effect=PermissionError("sudo authentication failed"),
    ):
        # FROZEN BEHAVIOR: Exception propagates
        with pytest.raises(
            PermissionError, match="sudo authentication failed"
        ):
            manager.install(["vim"])


@pytest.mark.parametrize(
    "manager_class",
    [
        PacmanPackageManager,
        YayPackageManager,
        ParuPackageManager,
        AptPackageManager,
        DnfPackageManager,
    ],
)
def test_subprocess_timeout_returns_failure(manager_class, mock_executable):
    """CHARACTERIZATION: TimeoutExpired is caught and returns InstallResult.

    When a command times out, it is caught and converted to InstallResult
    with success=False. The timeout information is preserved in the error message.
    """
    manager = create_manager(manager_class)

    timeout_error = subprocess.TimeoutExpired(
        cmd=["mock", "install", "vim"], timeout=30
    )
    with patch("subprocess.run", side_effect=timeout_error):
        # FROZEN BEHAVIOR: TimeoutExpired is caught and returns failure
        result = manager.install(["vim"])
        assert result.success is False
        assert result.packages_failed == ["vim"]
        assert "timeout" in result.error_message.lower()


@pytest.mark.parametrize(
    "manager_class",
    [
        PacmanPackageManager,
        YayPackageManager,
        ParuPackageManager,
        AptPackageManager,
        DnfPackageManager,
    ],
)
def test_package_manager_error_propagates_correctly(
    manager_class, mock_executable
):
    """CHARACTERIZATION: PackageManagerError is caught and converted to
    InstallResult.

    When _run_command raises PackageManagerError (wrapping subprocess errors),
    it's caught in install() and converted to InstallResult(success=False).
    """
    manager = create_manager(manager_class)

    # Simulate _run_command raising PackageManagerError
    with patch.object(
        manager,
        "_run_command",
        side_effect=PackageManagerError("Command execution failed"),
    ):
        result = manager.install(["vim"])

    # FROZEN BEHAVIOR: Returns InstallResult with success=False
    assert result.success is False
    assert result.packages_installed == []
    assert result.packages_failed == ["vim"]
    assert "Command execution failed" in result.error_message
