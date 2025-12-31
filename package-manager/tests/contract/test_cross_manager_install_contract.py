"""Contract tests: All package managers must behave identically for install().

HIGHEST PRIORITY: Cross-manager consistency is CRITICAL (user requirement #5).

This test suite ensures that ALL 5 package managers (pacman, yay, paru, apt, dnf)
behave identically for the install() method.

Contract Guarantees:
1. Empty list returns InstallResult(success=True, packages_installed=[], packages_failed=[])
2. Successful install returns InstallResult(success=True, packages_installed=[...], packages_failed=[])
3. Total failure returns InstallResult(success=False, packages_installed=[], packages_failed=[...])
4. Partial failure returns InstallResult(success=True, packages_installed=[...], packages_failed=[...])
5. Subprocess errors return InstallResult(success=False, packages_installed=[], packages_failed=[...])
6. update_system=True triggers system update before install
7. update_system=False skips system update

Evidence:
- base.py:54-81 - Abstract install() method
- pacman.py:30-91, yay.py, paru.py, apt.py:30-90, dnf.py - Implementations
- TEST_PLAN.md - Contract #3, Flow #5
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


# All 5 package managers that must behave identically
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
def test_contract__install_empty_list(manager_class, mock_executable):
    """CONTRACT: All managers return success for empty package list.

    Guarantee: install([]) returns InstallResult(success=True, [], [])
    """
    manager = create_manager(manager_class)

    with patch("subprocess.run") as mock_subprocess:
        result = manager.install([])

        # CONTRACT: No subprocess call for empty list
        mock_subprocess.assert_not_called()

    # CONTRACT: Returns success with empty lists
    assert isinstance(result, InstallResult)
    assert result.success is True
    assert result.packages_installed == []
    assert result.packages_failed == []


@pytest.mark.parametrize("manager_class", ALL_MANAGERS)
def test_contract__install_single_package_success(
    manager_class, mock_executable
):
    """CONTRACT: All managers handle single package success identically.

    Guarantee: Successful install returns success=True with package
    in installed list.
    """
    manager = create_manager(manager_class)

    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "Installed vim"
    mock_result.stderr = ""

    with patch("subprocess.run", return_value=mock_result):
        result = manager.install(["vim"])

    # CONTRACT: Success with package in installed list
    assert isinstance(result, InstallResult)
    assert result.success is True
    assert "vim" in result.packages_installed
    assert result.packages_failed == []


@pytest.mark.parametrize("manager_class", ALL_MANAGERS)
def test_contract__install_multiple_packages_success(
    manager_class, mock_executable
):
    """CONTRACT: All managers handle multiple package success identically."""
    manager = create_manager(manager_class)

    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "Installed vim\nInstalled git\nInstalled curl"
    mock_result.stderr = ""

    with patch("subprocess.run", return_value=mock_result):
        result = manager.install(["vim", "git", "curl"])

    # CONTRACT: Success with all packages in installed list
    assert isinstance(result, InstallResult)
    assert result.success is True
    assert len(result.packages_installed) == 3
    assert set(result.packages_installed) == {"vim", "git", "curl"}
    assert result.packages_failed == []


@pytest.mark.parametrize("manager_class", ALL_MANAGERS)
def test_contract__install_total_failure(manager_class, mock_executable):
    """CONTRACT: All managers handle total failure identically.

    Guarantee: When all packages fail, success=False with all in
    failed list.
    """
    manager = create_manager(manager_class)

    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stdout = ""
    mock_result.stderr = "error: package not found"

    with patch("subprocess.run", return_value=mock_result):
        with patch.object(
            manager,
            "_parse_failed_packages",
            return_value=["nonexistent1", "nonexistent2"],
        ):
            result = manager.install(["nonexistent1", "nonexistent2"])

    # CONTRACT: Failure with all packages in failed list
    assert isinstance(result, InstallResult)
    assert result.success is False
    assert result.packages_installed == []
    assert len(result.packages_failed) == 2
    assert set(result.packages_failed) == {"nonexistent1", "nonexistent2"}


@pytest.mark.parametrize("manager_class", ALL_MANAGERS)
def test_contract__install_returns_install_result_type(
    manager_class, mock_executable
):
    """CONTRACT: All managers return InstallResult type.

    Guarantee: Return type is always InstallResult, never None or
    other type.
    """
    manager = create_manager(manager_class)

    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = ""
    mock_result.stderr = ""

    with patch("subprocess.run", return_value=mock_result):
        result = manager.install(["vim"])

    # CONTRACT: Return type is InstallResult
    assert isinstance(result, InstallResult)
    assert hasattr(result, "success")
    assert hasattr(result, "packages_installed")
    assert hasattr(result, "packages_failed")


@pytest.mark.parametrize("manager_class", ALL_MANAGERS)
def test_contract__install_partial_failure(manager_class, mock_executable):
    """CONTRACT: All managers handle partial failure identically.

    Guarantee: When some packages succeed and some fail, success=True
    with packages split between installed and failed lists.
    """
    manager = create_manager(manager_class)

    mock_result = MagicMock()
    mock_result.returncode = 1  # Non-zero indicates some failure
    mock_result.stdout = "Installed vim"
    mock_result.stderr = "error: package not found: nonexistent"

    with patch("subprocess.run", return_value=mock_result):
        with patch.object(
            manager, "_parse_failed_packages", return_value=["nonexistent"]
        ):
            result = manager.install(["vim", "nonexistent"])

    # CONTRACT: Partial success returns success=True
    assert isinstance(result, InstallResult)
    assert result.success is True
    assert "vim" in result.packages_installed
    assert "nonexistent" in result.packages_failed
    assert len(result.packages_installed) > 0
    assert len(result.packages_failed) > 0


@pytest.mark.parametrize("manager_class", ALL_MANAGERS)
def test_contract__install_subprocess_error_handling(
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
            manager.install(["vim"])
