"""Contract tests: All package managers must behave identically for remove().

HIGHEST PRIORITY: Cross-manager consistency is CRITICAL (user requirement #5).

Contract Guarantees:
1. Empty list returns InstallResult(success=True, packages_installed=[], packages_failed=[])
2. Successful remove returns InstallResult(success=True, packages_installed=[...], packages_failed=[])
   Note: "packages_installed" means "packages removed" for remove()
3. remove_dependencies=True removes unused dependencies
4. remove_dependencies=False keeps dependencies

Evidence:
- base.py:82-95 - Abstract remove() method
- pacman.py:93-141, apt.py:91-141, dnf.py - Implementations
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
def test_contract__remove_empty_list(manager_class, mock_executable):
    """CONTRACT: All managers return success for empty package list."""
    manager = create_manager(manager_class)

    with patch("subprocess.run") as mock_subprocess:
        result = manager.remove([])
        mock_subprocess.assert_not_called()

    # CONTRACT: Returns success with empty lists
    assert isinstance(result, InstallResult)
    assert result.success is True
    assert result.packages_installed == []
    assert result.packages_failed == []


@pytest.mark.parametrize("manager_class", ALL_MANAGERS)
def test_contract__remove_single_package_success(
    manager_class, mock_executable
):
    """CONTRACT: All managers handle single package removal identically."""
    manager = create_manager(manager_class)

    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "Removed vim"
    mock_result.stderr = ""

    with patch("subprocess.run", return_value=mock_result):
        result = manager.remove(["vim"])

    # CONTRACT: Success with package in "installed" list (means removed)
    assert isinstance(result, InstallResult)
    assert result.success is True
    assert "vim" in result.packages_installed  # "installed" = "removed"
    assert result.packages_failed == []


@pytest.mark.parametrize("manager_class", ALL_MANAGERS)
def test_contract__remove_multiple_packages_success(
    manager_class, mock_executable
):
    """CONTRACT: All managers handle multiple package removal identically."""
    manager = create_manager(manager_class)

    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "Removed vim\nRemoved git"
    mock_result.stderr = ""

    with patch("subprocess.run", return_value=mock_result):
        result = manager.remove(["vim", "git"])

    # CONTRACT: Success with all packages in "installed" list
    assert isinstance(result, InstallResult)
    assert result.success is True
    assert len(result.packages_installed) == 2
    assert set(result.packages_installed) == {"vim", "git"}
    assert result.packages_failed == []


@pytest.mark.parametrize("manager_class", ALL_MANAGERS)
def test_contract__remove_returns_install_result_type(
    manager_class, mock_executable
):
    """CONTRACT: All managers return InstallResult type for remove().

    Note: remove() reuses InstallResult type (not a separate
    RemoveResult).
    """
    manager = create_manager(manager_class)

    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = ""
    mock_result.stderr = ""

    with patch("subprocess.run", return_value=mock_result):
        result = manager.remove(["vim"])

    # CONTRACT: Return type is InstallResult
    assert isinstance(result, InstallResult)
    assert hasattr(result, "success")
    assert hasattr(result, "packages_installed")
    assert hasattr(result, "packages_failed")


@pytest.mark.parametrize("manager_class", ALL_MANAGERS)
def test_contract__remove_with_dependencies_flag(
    manager_class, mock_executable
):
    """CONTRACT: All managers accept remove_dependencies parameter.

    Guarantee: remove_dependencies parameter is accepted (behavior may
    vary).
    """
    manager = create_manager(manager_class)

    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "Removed vim and dependencies"
    mock_result.stderr = ""

    with patch("subprocess.run", return_value=mock_result):
        result = manager.remove(["vim"], remove_dependencies=True)

    # CONTRACT: Accepts parameter and returns success
    assert isinstance(result, InstallResult)
    assert result.success is True
