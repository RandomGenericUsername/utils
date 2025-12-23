"""Characterization test: Empty package list behavior.

This test freezes the CURRENT behavior where install([]) and remove([])
return success=True without executing any commands.

Evidence:
- pacman.py:34-37 - Returns success immediately for empty list
- apt.py:34-37 - Returns success immediately for empty list
- Common edge case in automation

Current Behavior (FROZEN):
- install([]) returns InstallResult(success=True, packages_installed=[], packages_failed=[])
- remove([]) returns InstallResult(success=True, packages_installed=[], packages_failed=[])
- No subprocess commands are executed
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

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
def test_install_empty_list_returns_success(manager_class, mock_executable):
    """CHARACTERIZATION: install([]) returns success without executing
    commands.

    This is a common edge case - when there are no packages to install,
    the operation should succeed immediately without calling subprocess.
    """
    manager = create_manager(manager_class)

    # Mock subprocess to ensure it's NOT called
    with patch("subprocess.run") as mock_subprocess:
        result = manager.install([])

        # FROZEN BEHAVIOR: No subprocess call for empty list
        mock_subprocess.assert_not_called()

    # FROZEN BEHAVIOR: Returns success
    assert result.success is True
    assert result.packages_installed == []
    assert result.packages_failed == []


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
def test_remove_empty_list_returns_success(manager_class, mock_executable):
    """CHARACTERIZATION: remove([]) returns success without executing
    commands."""
    manager = create_manager(manager_class)

    with patch("subprocess.run") as mock_subprocess:
        result = manager.remove([])
        mock_subprocess.assert_not_called()

    # FROZEN BEHAVIOR: Returns success
    assert result.success is True
    # "installed" means "removed" for remove()
    assert result.packages_installed == []
    assert result.packages_failed == []


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
def test_install_empty_list_with_update_system_true(
    manager_class, mock_executable
):
    """CHARACTERIZATION: install([], update_system=True) still returns
    success.

    Even with update_system=True, an empty package list should succeed
    without attempting system update.
    """
    manager = create_manager(manager_class)

    # The current implementation checks for empty list BEFORE update_system
    # So update_system should not be called
    with patch("subprocess.run") as mock_subprocess:
        result = manager.install([], update_system=True)
        mock_subprocess.assert_not_called()

    # FROZEN BEHAVIOR: Returns success
    assert result.success is True
    assert result.packages_installed == []
    assert result.packages_failed == []


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
def test_remove_empty_list_with_remove_dependencies_true(
    manager_class, mock_executable
):
    """CHARACTERIZATION: remove([], remove_dependencies=True) returns
    success."""
    manager = create_manager(manager_class)

    with patch("subprocess.run") as mock_subprocess:
        result = manager.remove([], remove_dependencies=True)
        mock_subprocess.assert_not_called()

    # FROZEN BEHAVIOR: Returns success
    assert result.success is True
    assert result.packages_installed == []
    assert result.packages_failed == []
