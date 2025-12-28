"""Characterization tests for timeout handling.

This test freezes the CURRENT behavior when install() times out.

Evidence:
- base.py: _run_command catches TimeoutExpired and raises PackageManagerTimeoutError
- yay.py: install() catches PackageManagerTimeoutError and returns InstallResult(success=False)

Current Behavior (FROZEN):
- TimeoutExpired from subprocess is caught
- Converted to InstallResult with success=False
- error_message contains timeout information
- All packages are marked as failed
"""

import subprocess
from unittest.mock import patch, MagicMock

import pytest

from dotfiles_package_manager.implementations.arch.yay import YayPackageManager
from dotfiles_package_manager.implementations.arch.pacman import PacmanPackageManager
from dotfiles_package_manager.implementations.arch.paru import ParuPackageManager
from dotfiles_package_manager.implementations.debian.apt import AptPackageManager
from dotfiles_package_manager.implementations.redhat.dnf import DnfPackageManager


def create_manager(manager_class):
    """Create a manager with mocked executable check."""
    from pathlib import Path
    mock_path = MagicMock(spec=Path)
    mock_path.exists.return_value = True
    with patch.object(manager_class, "_find_executable", return_value=mock_path):
        return manager_class()


@pytest.mark.parametrize(
    "manager_class",
    [
        YayPackageManager,
        PacmanPackageManager,
        ParuPackageManager,
        AptPackageManager,
        DnfPackageManager,
    ],
)
def test_timeout_returns_install_result_failure(manager_class):
    """CHARACTERIZATION: Timeout returns InstallResult(success=False).

    When a command times out, it returns a failure result instead of
    propagating the exception. This allows the pipeline to handle
    the failure gracefully.
    """
    manager = create_manager(manager_class)

    timeout_error = subprocess.TimeoutExpired(
        cmd=["mock", "-S", "--noconfirm", "vim"],
        timeout=60,
    )

    with patch("subprocess.run", side_effect=timeout_error):
        result = manager.install(["vim"], timeout=60)

    # FROZEN BEHAVIOR: Returns failure instead of raising
    assert result.success is False
    assert result.packages_installed == []
    assert result.packages_failed == ["vim"]
    assert "timeout" in result.error_message.lower()
    assert "60" in result.error_message


@pytest.mark.parametrize(
    "manager_class",
    [
        YayPackageManager,
        PacmanPackageManager,
        ParuPackageManager,
        AptPackageManager,
        DnfPackageManager,
    ],
)
def test_timeout_parameter_passed_to_subprocess(manager_class):
    """CHARACTERIZATION: Timeout parameter is passed to subprocess.run.

    When a custom timeout is specified, it should be passed down to
    the subprocess.run call.
    """
    manager = create_manager(manager_class)

    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = ""
    mock_result.stderr = ""

    with patch("subprocess.run", return_value=mock_result) as mock_run:
        manager.install(["vim"], timeout=120)

    # FROZEN BEHAVIOR: timeout parameter is passed
    call_kwargs = mock_run.call_args.kwargs
    assert call_kwargs.get("timeout") == 120


@pytest.mark.parametrize(
    "manager_class",
    [
        YayPackageManager,
        PacmanPackageManager,
        ParuPackageManager,
        AptPackageManager,
        DnfPackageManager,
    ],
)
def test_none_timeout_allows_unlimited(manager_class):
    """CHARACTERIZATION: None timeout means no timeout limit.

    When timeout is None, subprocess.run is called without a timeout,
    allowing commands to run indefinitely.
    """
    manager = create_manager(manager_class)

    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = ""
    mock_result.stderr = ""

    with patch("subprocess.run", return_value=mock_result) as mock_run:
        manager.install(["vim"], timeout=None)

    # FROZEN BEHAVIOR: None timeout is passed
    call_kwargs = mock_run.call_args.kwargs
    assert call_kwargs.get("timeout") is None
