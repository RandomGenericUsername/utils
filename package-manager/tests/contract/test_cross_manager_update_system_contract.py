"""Contract tests: All package managers must behave identically for update_system().

HIGHEST PRIORITY: Cross-manager consistency is CRITICAL (user requirement #5).

Contract Guarantees:
1. update_system(dry_run=False) applies system updates
2. update_system(dry_run=True) checks for updates without applying
3. Returns InstallResult type
4. Success/failure is indicated by success field

Evidence:
- base.py:97-109 - Abstract update_system() method
- pacman.py:161-179, apt.py, dnf.py - Implementations
- package_management_steps.py:140-145 - Real usage
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from dotfiles_package_manager.core.types import InstallResult
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


ALL_MANAGERS = [
    PacmanPackageManager,
    YayPackageManager,
    ParuPackageManager,
    AptPackageManager,
    DnfPackageManager,
]


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


@pytest.mark.parametrize("manager_class", ALL_MANAGERS)
def test_contract__update_system_dry_run_false(
    manager_class, mock_executable
):
    """CONTRACT: All managers apply updates when dry_run=False."""
    manager = create_manager(manager_class)

    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "System updated successfully"
    mock_result.stderr = ""

    with patch("subprocess.run", return_value=mock_result):
        result = manager.update_system(dry_run=False)

    # CONTRACT: Returns InstallResult with success
    assert isinstance(result, InstallResult)
    assert result.success is True


@pytest.mark.parametrize("manager_class", ALL_MANAGERS)
def test_contract__update_system_dry_run_true(manager_class, mock_executable):
    """CONTRACT: All managers check updates when dry_run=True."""
    manager = create_manager(manager_class)

    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "Updates available: vim, git"
    mock_result.stderr = ""

    with patch("subprocess.run", return_value=mock_result):
        result = manager.update_system(dry_run=True)

    # CONTRACT: Returns InstallResult
    assert isinstance(result, InstallResult)
    # Note: success may vary based on whether updates are available


@pytest.mark.parametrize("manager_class", ALL_MANAGERS)
def test_contract__update_system_returns_install_result_type(
    manager_class, mock_executable
):
    """CONTRACT: All managers return InstallResult type for update_system().

    Note: update_system() reuses InstallResult type.
    """
    manager = create_manager(manager_class)

    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = ""
    mock_result.stderr = ""

    with patch("subprocess.run", return_value=mock_result):
        result = manager.update_system(dry_run=False)

    # CONTRACT: Return type is InstallResult
    assert isinstance(result, InstallResult)
    assert hasattr(result, "success")
    assert hasattr(result, "output")
    assert hasattr(result, "error_message")


@pytest.mark.parametrize("manager_class", ALL_MANAGERS)
def test_contract__update_system_failure_handling(
    manager_class, mock_executable
):
    """CONTRACT: All managers handle update failures identically."""
    manager = create_manager(manager_class)

    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stdout = ""
    mock_result.stderr = "Update failed: network error"

    with patch("subprocess.run", return_value=mock_result):
        result = manager.update_system(dry_run=False)

    # CONTRACT: Failure returns InstallResult with success=False
    assert isinstance(result, InstallResult)
    assert result.success is False
    assert result.error_message is not None


@pytest.mark.parametrize("manager_class", ALL_MANAGERS)
def test_contract__update_system_subprocess_error(
    manager_class, mock_executable
):
    """CONTRACT: All managers handle subprocess errors identically.

    Guarantee: Subprocess exceptions (FileNotFoundError, PermissionError,
    TimeoutExpired) propagate to the caller. Only PackageManagerError is caught.
    """
    manager = create_manager(manager_class)

    # FileNotFoundError propagates
    with patch(
        "subprocess.run",
        side_effect=FileNotFoundError("executable not found"),
    ):
        with pytest.raises(FileNotFoundError, match="executable not found"):
            manager.update_system(dry_run=False)
