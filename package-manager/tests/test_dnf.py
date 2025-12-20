"""Tests for DNF package manager implementation."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from dotfiles_package_manager.core.base import PackageManagerError
from dotfiles_package_manager.core.types import PackageManagerType
from dotfiles_package_manager.implementations.redhat.dnf import (
    DnfPackageManager,
)


@pytest.fixture
def dnf_manager(tmp_path):
    """Create an DnfPackageManager instance for testing."""
    executable = tmp_path / "dnf"
    executable.touch()
    with patch.object(
        DnfPackageManager, "_find_executable", return_value=executable
    ):
        manager = DnfPackageManager()
        return manager


class TestDnfPackageManagerInit:
    """Tests for DnfPackageManager initialization."""

    def test_init_with_executable_path(self, tmp_path):
        """Test initialization with explicit executable path."""
        executable = tmp_path / "dnf"
        executable.touch()
        manager = DnfPackageManager(executable_path=executable)
        assert manager.executable_path == executable
        assert manager.manager_type == PackageManagerType.DNF

    def test_init_without_executable_path(self):
        """Test initialization without explicit executable path."""
        with (
            patch.object(
                DnfPackageManager,
                "_find_executable",
                return_value=Path("/usr/bin/dnf"),
            ),
            patch("pathlib.Path.exists", return_value=True),
        ):
            manager = DnfPackageManager()
            assert manager.executable_path == Path("/usr/bin/dnf")
            assert manager.manager_type == PackageManagerType.DNF


class TestDnfPackageManagerInstall:
    """Tests for DnfPackageManager install method."""

    def test_install_single_package_success(self, dnf_manager):
        """Test installing a single package successfully."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Installing package..."
        mock_result.stderr = ""

        with patch.object(
            dnf_manager, "_run_command", return_value=mock_result
        ):
            result = dnf_manager.install(["vim"])

        assert result.success is True
        assert result.packages_installed == ["vim"]
        assert result.packages_failed == []

    def test_install_multiple_packages_success(self, dnf_manager):
        """Test installing multiple packages successfully."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Installing packages..."
        mock_result.stderr = ""

        with patch.object(
            dnf_manager, "_run_command", return_value=mock_result
        ):
            result = dnf_manager.install(["vim", "git", "htop"])

        assert result.success is True
        assert result.packages_installed == ["vim", "git", "htop"]
        assert result.packages_failed == []

    def test_install_with_update_system(self, dnf_manager):
        """Test installing with system update."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Installing with update..."
        mock_result.stderr = ""

        with patch.object(
            dnf_manager, "_run_command", return_value=mock_result
        ) as mock_run:
            result = dnf_manager.install(["vim"], update_system=True)

        assert result.success is True
        # Verify update was called first
        assert mock_run.call_count == 2  # update + install

    def test_install_empty_list(self, dnf_manager):
        """Test installing empty package list."""
        result = dnf_manager.install([])
        assert result.success is True
        assert result.packages_installed == []
        assert result.packages_failed == []

    def test_install_package_not_found(self, dnf_manager):
        """Test installing non-existent package."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "No match for argument: nonexistent"

        with patch.object(
            dnf_manager, "_run_command", return_value=mock_result
        ):
            result = dnf_manager.install(["nonexistent"])

        assert result.success is False
        assert result.packages_installed == []
        assert result.packages_failed == ["nonexistent"]

    def test_install_partial_failure(self, dnf_manager):
        """Test installing with some packages failing."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = "Installed vim"
        mock_result.stderr = "No match for argument: nonexistent"

        with patch.object(
            dnf_manager, "_run_command", return_value=mock_result
        ):
            result = dnf_manager.install(["vim", "nonexistent"])

        assert result.success is True  # At least one succeeded
        assert "vim" in result.packages_installed
        assert "nonexistent" in result.packages_failed


class TestDnfPackageManagerRemove:
    """Tests for DnfPackageManager remove method."""

    def test_remove_single_package(self, dnf_manager):
        """Test removing a single package."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Removing package..."
        mock_result.stderr = ""

        with patch.object(
            dnf_manager, "_run_command", return_value=mock_result
        ):
            result = dnf_manager.remove(["vim"])

        assert result.success is True
        assert result.packages_installed == ["vim"]
        assert result.packages_failed == []

    def test_remove_with_dependencies(self, dnf_manager):
        """Test removing package with dependencies."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Removing with dependencies..."
        mock_result.stderr = ""

        with patch.object(
            dnf_manager, "_run_command", return_value=mock_result
        ) as mock_run:
            result = dnf_manager.remove(["vim"], remove_dependencies=True)

        assert result.success is True
        # Verify autoremove was used
        call_args = mock_run.call_args[0][0]
        assert "autoremove" in call_args

    def test_remove_empty_list(self, dnf_manager):
        """Test removing empty package list."""
        result = dnf_manager.remove([])
        assert result.success is True
        assert result.packages_installed == []
        assert result.packages_failed == []


class TestDnfPackageManagerSearch:
    """Tests for DnfPackageManager search method."""

    def test_search_packages(self, dnf_manager):
        """Test searching for packages."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = (
            "==================== Name Matched: vim ====================\n"
            "vim-enhanced.x86_64 : A version of the VIM editor\n"
            "    VIM (Vi IMproved) is an updated and improved version "
            "of the vi text editor\n"
            "neovim.x86_64 : Fork of Vim aiming to improve user "
            "experience\n"
            "    Neovim is a refactor of Vim"
        )
        mock_result.stderr = ""

        with patch.object(
            dnf_manager, "_run_command", return_value=mock_result
        ):
            result = dnf_manager.search("vim")

        assert result.query == "vim"
        assert result.total_found >= 1
        assert len(result.packages) >= 1

    def test_search_with_limit(self, dnf_manager):
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
            dnf_manager, "_run_command", return_value=mock_result
        ):
            result = dnf_manager.search("vim", limit=2)

        assert len(result.packages) <= 2

    def test_search_no_results(self, dnf_manager):
        """Test searching with no results."""
        with patch.object(
            dnf_manager,
            "_run_command",
            side_effect=PackageManagerError("No results"),
        ):
            result = dnf_manager.search("nonexistentpackage12345")

        assert result.total_found == 0
        assert len(result.packages) == 0


class TestDnfPackageManagerUpdateSystem:
    """Tests for DnfPackageManager update_system method."""

    def test_update_system_success(self, dnf_manager):
        """Test updating system successfully."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Updating system..."
        mock_result.stderr = ""

        with patch.object(
            dnf_manager, "_run_command", return_value=mock_result
        ):
            result = dnf_manager.update_system()

        assert result.success is True

    def test_update_system_dry_run(self, dnf_manager):
        """Test dry run system update."""
        mock_result = MagicMock()
        mock_result.returncode = (
            100  # DNF returns 100 when updates are available
        )
        mock_result.stdout = """vim.x86_64 2:9.0.1000-1 updates
git.x86_64 1:2.40.1-1 updates"""
        mock_result.stderr = ""

        with patch.object(
            dnf_manager, "_run_command", return_value=mock_result
        ):
            result = dnf_manager.update_system(dry_run=True)

        assert result.success is True
        assert "upgradeable packages" in result.output.lower()

    def test_update_system_failure(self, dnf_manager):
        """Test system update failure."""
        with patch.object(
            dnf_manager,
            "_run_command",
            side_effect=PackageManagerError("Update failed"),
        ):
            result = dnf_manager.update_system()

        assert result.success is False
        assert result.error_message is not None


class TestDnfPackageManagerIsInstalled:
    """Tests for DnfPackageManager is_installed method."""

    def test_is_installed_true(self, dnf_manager):
        """Test checking if installed package exists."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Status     : Installed"

        with patch.object(
            dnf_manager, "_run_command", return_value=mock_result
        ):
            result = dnf_manager.is_installed("vim")

        assert result is True

    def test_is_installed_false(self, dnf_manager):
        """Test checking if non-installed package exists."""
        mock_result = MagicMock()
        mock_result.returncode = 1

        with patch.object(
            dnf_manager, "_run_command", return_value=mock_result
        ):
            result = dnf_manager.is_installed("nonexistent")

        assert result is False


class TestDnfPackageManagerGetPackageInfo:
    """Tests for DnfPackageManager get_package_info method."""

    def test_get_package_info_installed(self, dnf_manager):
        """Test getting info for installed package."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = """Name         : vim-enhanced
Version      : 9.0.1234
Release      : 1.fc38
Architecture : x86_64
Size         : 1.8 M
Repository   : fedora
Summary      : A version of the VIM editor"""

        with patch.object(
            dnf_manager, "_run_command", return_value=mock_result
        ):
            info = dnf_manager.get_package_info("vim")

        assert info is not None
        assert info.name == "vim-enhanced"

    def test_get_package_info_not_found(self, dnf_manager):
        """Test getting info for non-existent package."""
        mock_result = MagicMock()
        mock_result.returncode = 1

        with patch.object(
            dnf_manager, "_run_command", return_value=mock_result
        ):
            info = dnf_manager.get_package_info("nonexistent")

        assert info is None
