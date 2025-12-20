"""Tests for APT package manager implementation."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from dotfiles_package_manager.core.base import PackageManagerError
from dotfiles_package_manager.core.types import PackageManagerType
from dotfiles_package_manager.implementations.debian.apt import (
    AptPackageManager,
)


@pytest.fixture
def apt_manager(tmp_path):
    """Create an AptPackageManager instance for testing."""
    executable = tmp_path / "apt"
    executable.touch()
    with patch.object(
        AptPackageManager, "_find_executable", return_value=executable
    ):
        manager = AptPackageManager()
        return manager


class TestAptPackageManagerInit:
    """Tests for AptPackageManager initialization."""

    def test_init_with_executable_path(self, tmp_path):
        """Test initialization with explicit executable path."""
        executable = tmp_path / "apt"
        executable.touch()
        manager = AptPackageManager(executable_path=executable)
        assert manager.executable_path == executable
        assert manager.manager_type == PackageManagerType.APT

    def test_init_without_executable_path(self):
        """Test initialization without explicit executable path."""
        with (
            patch.object(
                AptPackageManager,
                "_find_executable",
                return_value=Path("/usr/bin/apt"),
            ),
            patch("pathlib.Path.exists", return_value=True),
        ):
            manager = AptPackageManager()
            assert manager.executable_path == Path("/usr/bin/apt")
            assert manager.manager_type == PackageManagerType.APT


class TestAptPackageManagerInstall:
    """Tests for AptPackageManager install method."""

    def test_install_single_package_success(self, apt_manager):
        """Test installing a single package successfully."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Installing package..."
        mock_result.stderr = ""

        with patch.object(
            apt_manager, "_run_command", return_value=mock_result
        ):
            result = apt_manager.install(["vim"])

        assert result.success is True
        assert result.packages_installed == ["vim"]
        assert result.packages_failed == []

    def test_install_multiple_packages_success(self, apt_manager):
        """Test installing multiple packages successfully."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Installing packages..."
        mock_result.stderr = ""

        with patch.object(
            apt_manager, "_run_command", return_value=mock_result
        ):
            result = apt_manager.install(["vim", "git", "htop"])

        assert result.success is True
        assert result.packages_installed == ["vim", "git", "htop"]
        assert result.packages_failed == []

    def test_install_with_update_system(self, apt_manager):
        """Test installing with system update."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Installing with update..."
        mock_result.stderr = ""

        with patch.object(
            apt_manager, "_run_command", return_value=mock_result
        ) as mock_run:
            result = apt_manager.install(["vim"], update_system=True)

        assert result.success is True
        # Verify update was called first
        assert mock_run.call_count == 2  # update + install

    def test_install_empty_list(self, apt_manager):
        """Test installing empty package list."""
        result = apt_manager.install([])
        assert result.success is True
        assert result.packages_installed == []
        assert result.packages_failed == []

    def test_install_package_not_found(self, apt_manager):
        """Test installing non-existent package."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "E: Unable to locate package nonexistent"

        with patch.object(
            apt_manager, "_run_command", return_value=mock_result
        ):
            result = apt_manager.install(["nonexistent"])

        assert result.success is False
        assert result.packages_installed == []
        assert result.packages_failed == ["nonexistent"]

    def test_install_partial_failure(self, apt_manager):
        """Test installing with some packages failing."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = "Installed vim"
        mock_result.stderr = "E: Unable to locate package nonexistent"

        with patch.object(
            apt_manager, "_run_command", return_value=mock_result
        ):
            result = apt_manager.install(["vim", "nonexistent"])

        assert result.success is True  # At least one succeeded
        assert "vim" in result.packages_installed
        assert "nonexistent" in result.packages_failed


class TestAptPackageManagerRemove:
    """Tests for AptPackageManager remove method."""

    def test_remove_single_package(self, apt_manager):
        """Test removing a single package."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Removing package..."
        mock_result.stderr = ""

        with patch.object(
            apt_manager, "_run_command", return_value=mock_result
        ):
            result = apt_manager.remove(["vim"])

        assert result.success is True
        assert result.packages_installed == ["vim"]
        assert result.packages_failed == []

    def test_remove_with_dependencies(self, apt_manager):
        """Test removing package with dependencies."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Removing with dependencies..."
        mock_result.stderr = ""

        with patch.object(
            apt_manager, "_run_command", return_value=mock_result
        ) as mock_run:
            result = apt_manager.remove(["vim"], remove_dependencies=True)

        assert result.success is True
        # Verify autoremove was used
        call_args = mock_run.call_args[0][0]
        assert "autoremove" in call_args

    def test_remove_empty_list(self, apt_manager):
        """Test removing empty package list."""
        result = apt_manager.remove([])
        assert result.success is True
        assert result.packages_installed == []
        assert result.packages_failed == []


class TestAptPackageManagerSearch:
    """Tests for AptPackageManager search method."""

    def test_search_packages(self, apt_manager):
        """Test searching for packages."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = """vim/stable 2:9.0.1000-1 amd64
  Vi Improved, a highly configurable, improved version of the vi text editor

neovim/stable 0.9.0-1 amd64
  Fork of Vim aiming to improve user experience"""
        mock_result.stderr = ""

        with patch.object(
            apt_manager, "_run_command", return_value=mock_result
        ):
            result = apt_manager.search("vim")

        assert result.query == "vim"
        assert result.total_found >= 1
        assert len(result.packages) >= 1

    def test_search_with_limit(self, apt_manager):
        """Test searching with result limit."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = """vim/stable 2:9.0.1000-1 amd64
  Vi Improved

neovim/stable 0.9.0-1 amd64
  Fork of Vim

gvim/stable 2:9.0.1000-1 amd64
  Graphical Vim"""
        mock_result.stderr = ""

        with patch.object(
            apt_manager, "_run_command", return_value=mock_result
        ):
            result = apt_manager.search("vim", limit=2)

        assert len(result.packages) <= 2

    def test_search_no_results(self, apt_manager):
        """Test searching with no results."""
        with patch.object(
            apt_manager,
            "_run_command",
            side_effect=PackageManagerError("No results"),
        ):
            result = apt_manager.search("nonexistentpackage12345")

        assert result.total_found == 0
        assert len(result.packages) == 0


class TestAptPackageManagerUpdateSystem:
    """Tests for AptPackageManager update_system method."""

    def test_update_system_success(self, apt_manager):
        """Test updating system successfully."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Updating system..."
        mock_result.stderr = ""

        with patch.object(
            apt_manager, "_run_command", return_value=mock_result
        ):
            result = apt_manager.update_system()

        assert result.success is True

    def test_update_system_dry_run(self, apt_manager):
        """Test dry run system update."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = """Listing...
vim/stable 2:9.0.1000-1 amd64 [upgradable from: 2:9.0.999-1]
git/stable 1:2.40.1-1 amd64 [upgradable from: 1:2.40.0-1]"""
        mock_result.stderr = ""

        with patch.object(
            apt_manager, "_run_command", return_value=mock_result
        ):
            result = apt_manager.update_system(dry_run=True)

        assert result.success is True
        assert "upgradeable packages" in result.output.lower()

    def test_update_system_failure(self, apt_manager):
        """Test system update failure."""
        with patch.object(
            apt_manager,
            "_run_command",
            side_effect=PackageManagerError("Update failed"),
        ):
            result = apt_manager.update_system()

        assert result.success is False
        assert result.error_message is not None


class TestAptPackageManagerIsInstalled:
    """Tests for AptPackageManager is_installed method."""

    def test_is_installed_true(self, apt_manager):
        """Test checking if installed package exists."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Status: install ok installed"

        with patch.object(
            apt_manager, "_run_command", return_value=mock_result
        ):
            result = apt_manager.is_installed("vim")

        assert result is True

    def test_is_installed_false(self, apt_manager):
        """Test checking if non-installed package exists."""
        mock_result = MagicMock()
        mock_result.returncode = 1

        with patch.object(
            apt_manager, "_run_command", return_value=mock_result
        ):
            result = apt_manager.is_installed("nonexistent")

        assert result is False


class TestAptPackageManagerGetPackageInfo:
    """Tests for AptPackageManager get_package_info method."""

    def test_get_package_info_installed(self, apt_manager):
        """Test getting info for installed package."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = """Package: vim
Version: 2:9.0.1000-1
Description: Vi Improved
Installed-Size: 10752"""

        with patch.object(
            apt_manager, "_run_command", return_value=mock_result
        ):
            info = apt_manager.get_package_info("vim")

        assert info is not None
        assert info.name == "vim"

    def test_get_package_info_not_found(self, apt_manager):
        """Test getting info for non-existent package."""
        mock_result = MagicMock()
        mock_result.returncode = 1

        with patch.object(
            apt_manager, "_run_command", return_value=mock_result
        ):
            info = apt_manager.get_package_info("nonexistent")

        assert info is None
