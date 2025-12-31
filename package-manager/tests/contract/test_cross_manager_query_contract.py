"""Contract tests: All package managers must behave identically for query methods.

HIGHEST PRIORITY: Cross-manager consistency is CRITICAL (user requirement #5).

Query methods: search(), is_installed(), get_package_info()

Contract Guarantees:
1. search(query) returns SearchResult with packages list
2. is_installed(package) returns bool
3. get_package_info(package) returns PackageInfo or None

Evidence:
- base.py:111-149 - Abstract query methods
- pacman.py, apt.py, dnf.py - Implementations
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from dotfiles_package_manager.core.types import PackageInfo, SearchResult
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
def test_contract__search_returns_search_result_type(
    manager_class, mock_executable
):
    """CONTRACT: All managers return SearchResult type for search()."""
    manager = create_manager(manager_class)

    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "vim - Vi IMproved"
    mock_result.stderr = ""

    with patch("subprocess.run", return_value=mock_result):
        with patch.object(
            manager, "_parse_search_output", return_value=[]
        ):
            result = manager.search("vim")

    # CONTRACT: Return type is SearchResult
    assert isinstance(result, SearchResult)
    assert hasattr(result, "packages")
    assert hasattr(result, "query")
    assert isinstance(result.packages, list)


@pytest.mark.parametrize("manager_class", ALL_MANAGERS)
def test_contract__is_installed_returns_bool(manager_class, mock_executable):
    """CONTRACT: All managers return bool for is_installed()."""
    manager = create_manager(manager_class)

    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "vim 9.0"
    mock_result.stderr = ""

    with patch("subprocess.run", return_value=mock_result):
        result = manager.is_installed("vim")

    # CONTRACT: Return type is bool
    assert isinstance(result, bool)


@pytest.mark.parametrize("manager_class", ALL_MANAGERS)
def test_contract__is_installed_true_for_installed_package(
    manager_class, mock_executable
):
    """CONTRACT: All managers return True for installed packages."""
    manager = create_manager(manager_class)

    mock_result = MagicMock()
    mock_result.returncode = 0
    # AptPackageManager checks for "Status: install ok installed" in stdout
    mock_result.stdout = "Status: install ok installed\nvim 9.0"
    mock_result.stderr = ""

    with patch("subprocess.run", return_value=mock_result):
        result = manager.is_installed("vim")

    # CONTRACT: Returns True for installed package
    assert result is True


@pytest.mark.parametrize("manager_class", ALL_MANAGERS)
def test_contract__is_installed_false_for_not_installed_package(
    manager_class, mock_executable
):
    """CONTRACT: All managers return False for non-installed packages."""
    manager = create_manager(manager_class)

    mock_result = MagicMock()
    mock_result.returncode = 1  # Not installed
    mock_result.stdout = ""
    mock_result.stderr = "package not found"

    with patch("subprocess.run", return_value=mock_result):
        result = manager.is_installed("nonexistent")

    # CONTRACT: Returns False for non-installed package
    assert result is False


@pytest.mark.parametrize("manager_class", ALL_MANAGERS)
def test_contract__get_package_info_returns_package_info_or_none(
    manager_class, mock_executable
):
    """CONTRACT: All managers return PackageInfo or None for get_package_info()."""
    manager = create_manager(manager_class)

    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "Name: vim\nVersion: 9.0\nDescription: Vi IMproved"
    mock_result.stderr = ""

    with patch("subprocess.run", return_value=mock_result):
        with patch.object(
            manager,
            "_parse_package_info_output",
            return_value=PackageInfo(
                name="vim",
                version="9.0",
                description="Vi IMproved",
                repository="core",
                installed=True,
            ),
        ):
            result = manager.get_package_info("vim")

    # CONTRACT: Return type is PackageInfo or None
    assert result is None or isinstance(result, PackageInfo)


@pytest.mark.parametrize("manager_class", ALL_MANAGERS)
def test_contract__get_package_info_none_for_nonexistent(
    manager_class, mock_executable
):
    """CONTRACT: All managers return None for non-existent packages."""
    manager = create_manager(manager_class)

    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stdout = ""
    mock_result.stderr = "package not found"

    with patch("subprocess.run", return_value=mock_result):
        with patch.object(
            manager, "_parse_package_info_output", return_value=None
        ):
            result = manager.get_package_info("nonexistent")

    # CONTRACT: Returns None for non-existent package
    assert result is None

