"""Characterization test: Partial install success behavior.

This test freezes the CURRENT behavior where install() returns success=True
if ANY package succeeds, even if some packages fail.

Evidence:
- pacman.py:78 - `success=len(successful_packages) > 0`
- apt.py:76 - `success=len(successful_packages) > 0`
- Used in production: package_management_steps.py:260-280

Current Behavior (FROZEN):
- install(["pkg1", "pkg2"]) where pkg1 succeeds and pkg2 fails
- Returns: InstallResult(success=True, packages_installed=["pkg1"], packages_failed=["pkg2"])

This is INTENTIONAL - the dotfiles-installer pipeline continues on partial failures
and tracks which packages succeeded/failed for reporting.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch
import subprocess

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
    "manager_class,expected_command_prefix",
    [
        (PacmanPackageManager, ["sudo", "/usr/bin/mock", "-S", "--noconfirm"]),
        (YayPackageManager, ["/usr/bin/mock", "-S", "--noconfirm"]),
        (ParuPackageManager, ["/usr/bin/mock", "-S", "--noconfirm"]),
        (AptPackageManager, ["sudo", "/usr/bin/mock", "install", "-y"]),
        (DnfPackageManager, ["sudo", "/usr/bin/mock", "install", "-y"]),
    ],
)
def test_partial_install_returns_success_true(
    manager_class, expected_command_prefix, mock_executable
):
    """CHARACTERIZATION: Partial install success returns success=True.

    This test freezes the current behavior where if SOME packages succeed,
    the result has success=True (not False).

    This is intentional behavior used in production.
    """
    # Create manager instance
    manager = create_manager(manager_class)

    # Mock subprocess to simulate partial failure
    # Package "vim" succeeds, "nonexistent-package" fails
    mock_result = MagicMock()
    mock_result.returncode = 1  # Non-zero indicates some failure
    mock_result.stdout = "Installing vim...\nInstalled vim"
    mock_result.stderr = "error: target not found: nonexistent-package"

    with patch("subprocess.run", return_value=mock_result):
        # Mock the parsing to return one failed package
        with patch.object(
            manager,
            "_parse_failed_packages",
            return_value=["nonexistent-package"],
        ):
            result = manager.install(["vim", "nonexistent-package"])

    # FROZEN BEHAVIOR: success=True when some packages succeed
    assert result.success is True
    assert "vim" in result.packages_installed
    assert "nonexistent-package" in result.packages_failed
    assert len(result.packages_installed) > 0
    assert len(result.packages_failed) > 0


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
def test_total_install_failure_returns_success_false(
    manager_class, mock_executable
):
    """CHARACTERIZATION: Total install failure returns success=False.

    When ALL packages fail, success=False.
    """
    manager = create_manager(manager_class)

    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stdout = ""
    mock_result.stderr = (
        "error: target not found: nonexistent1\n"
        "error: target not found: nonexistent2"
    )

    with patch("subprocess.run", return_value=mock_result):
        with patch.object(
            manager,
            "_parse_failed_packages",
            return_value=["nonexistent1", "nonexistent2"],
        ):
            result = manager.install(["nonexistent1", "nonexistent2"])

    # FROZEN BEHAVIOR: success=False when all packages fail
    assert result.success is False
    assert len(result.packages_installed) == 0
    assert len(result.packages_failed) == 2


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
def test_all_packages_succeed_returns_success_true(
    manager_class, mock_executable
):
    """CHARACTERIZATION: All packages succeed returns success=True."""
    manager = create_manager(manager_class)

    mock_result = MagicMock()
    mock_result.returncode = 0  # Success
    mock_result.stdout = "Installed vim\nInstalled git"
    mock_result.stderr = ""

    with patch("subprocess.run", return_value=mock_result):
        result = manager.install(["vim", "git"])

    # FROZEN BEHAVIOR: success=True when all packages succeed
    assert result.success is True
    assert len(result.packages_installed) == 2
    assert len(result.packages_failed) == 0

