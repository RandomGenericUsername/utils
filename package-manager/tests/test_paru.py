"""Tests for Paru AUR helper implementation."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from dotfiles_package_manager.core.base import PackageManagerError
from dotfiles_package_manager.core.types import PackageManagerType
from dotfiles_package_manager.implementations.arch.paru import (
    ParuPackageManager,
)


@pytest.fixture
def paru_manager(tmp_path):
    """Create a ParuPackageManager instance for testing."""
    executable = tmp_path / "paru"
    executable.touch()
    with patch.object(
        ParuPackageManager, "_find_executable", return_value=executable
    ):
        manager = ParuPackageManager()
        return manager


class TestParuPackageManagerInit:
    """Tests for ParuPackageManager initialization."""

    def test_init_with_executable_path(self, tmp_path):
        """Test initialization with explicit executable path."""
        executable = tmp_path / "paru"
        executable.touch()
        manager = ParuPackageManager(executable_path=executable)
        assert manager.executable_path == executable
        assert manager.manager_type == PackageManagerType.PARU

    def test_init_without_executable_path(self):
        """Test initialization without explicit executable path."""
        with (
            patch.object(
                ParuPackageManager,
                "_find_executable",
                return_value=Path("/usr/bin/paru"),
            ),
            patch("pathlib.Path.exists", return_value=True),
        ):
            manager = ParuPackageManager()
            assert manager.executable_path == Path("/usr/bin/paru")
            assert manager.manager_type == PackageManagerType.PARU


class TestParuPackageManagerInstall:
    """Tests for ParuPackageManager install method."""

    def test_install_single_package_success(self, paru_manager):
        """Test installing a single package successfully."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Installing package..."
        mock_result.stderr = ""

        with patch.object(
            paru_manager, "_run_command", return_value=mock_result
        ):
            result = paru_manager.install(["vim"])

        assert result.success is True
        assert result.packages_installed == ["vim"]
        assert result.packages_failed == []

    def test_install_multiple_packages_success(self, paru_manager):
        """Test installing multiple packages successfully."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Installing packages..."
        mock_result.stderr = ""

        with patch.object(
            paru_manager, "_run_command", return_value=mock_result
        ):
            result = paru_manager.install(["vim", "git", "htop"])

        assert result.success is True
        assert result.packages_installed == ["vim", "git", "htop"]
        assert result.packages_failed == []

    def test_install_with_update_system(self, paru_manager):
        """Test installing with system update.

        Should perform full system upgrade first, then install packages.
        This prevents partial upgrades on Arch Linux.
        """
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Installing with update..."
        mock_result.stderr = ""

        with patch.object(
            paru_manager, "_run_command", return_value=mock_result
        ) as mock_run:
            result = paru_manager.install(["vim"], update_system=True)

        assert result.success is True
        # Verify two separate calls were made: update_system then install
        assert mock_run.call_count == 2
        # First call should be update_system with -Syu
        first_call_args = mock_run.call_args_list[0][0][0]
        assert "-Syu" in " ".join(first_call_args)
        # Second call should be install with -S (no -y)
        second_call_args = mock_run.call_args_list[1][0][0]
        assert "-S" in second_call_args
        assert "vim" in second_call_args

    def test_install_empty_list(self, paru_manager):
        """Test installing empty package list."""
        result = paru_manager.install([])
        assert result.success is True
        assert result.packages_installed == []
        assert result.packages_failed == []

    def test_install_package_not_found(self, paru_manager):
        """Test installing non-existent package."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "error: target not found: nonexistent"

        with patch.object(
            paru_manager, "_run_command", return_value=mock_result
        ):
            result = paru_manager.install(["nonexistent"])

        assert result.success is False
        assert result.packages_installed == []
        assert result.packages_failed == ["nonexistent"]

    def test_install_partial_failure(self, paru_manager):
        """Test installing with some packages failing."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = "Installed vim"
        mock_result.stderr = "error: target not found: nonexistent"

        with patch.object(
            paru_manager, "_run_command", return_value=mock_result
        ):
            result = paru_manager.install(["vim", "nonexistent"])

        assert result.success is True  # At least one succeeded
        assert "vim" in result.packages_installed
        assert "nonexistent" in result.packages_failed


class TestParuPackageManagerRemove:
    """Tests for ParuPackageManager remove method."""

    def test_remove_single_package(self, paru_manager):
        """Test removing a single package."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Removing package..."
        mock_result.stderr = ""

        with patch.object(
            paru_manager, "_run_command", return_value=mock_result
        ):
            result = paru_manager.remove(["vim"])

        assert result.success is True
        assert result.packages_installed == ["vim"]
        assert result.packages_failed == []

    def test_remove_with_dependencies(self, paru_manager):
        """Test removing package with dependencies."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Removing with dependencies..."
        mock_result.stderr = ""

        with patch.object(
            paru_manager, "_run_command", return_value=mock_result
        ) as mock_run:
            result = paru_manager.remove(["vim"], remove_dependencies=True)

        assert result.success is True
        # Verify -s flag was added
        call_args = mock_run.call_args[0][0]
        assert "-s" in call_args

    def test_remove_empty_list(self, paru_manager):
        """Test removing empty package list."""
        result = paru_manager.remove([])
        assert result.success is True
        assert result.packages_installed == []
        assert result.packages_failed == []


class TestParuPackageManagerSearch:
    """Tests for ParuPackageManager search method."""

    def test_search_packages(self, paru_manager):
        """Test searching for packages."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = """core/vim 9.0.1000-1
    Vi Improved, a highly configurable, improved version of the vi text editor
extra/neovim 0.9.0-1
    Fork of Vim aiming to improve user experience"""
        mock_result.stderr = ""

        with patch.object(
            paru_manager, "_run_command", return_value=mock_result
        ):
            result = paru_manager.search("vim")

        assert result.query == "vim"
        assert result.total_found >= 1
        assert len(result.packages) >= 1

    def test_search_with_limit(self, paru_manager):
        """Test searching with result limit."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = """core/vim 9.0.1000-1
    Vi Improved
extra/neovim 0.9.0-1
    Fork of Vim
extra/gvim 9.0.1000-1
    Graphical Vim"""
        mock_result.stderr = ""

        with patch.object(
            paru_manager, "_run_command", return_value=mock_result
        ):
            result = paru_manager.search("vim", limit=2)

        assert len(result.packages) <= 2

    def test_search_no_results(self, paru_manager):
        """Test searching with no results."""
        with patch.object(
            paru_manager,
            "_run_command",
            side_effect=PackageManagerError("No results"),
        ):
            result = paru_manager.search("nonexistentpackage12345")

        assert result.total_found == 0
        assert len(result.packages) == 0


class TestParuPackageManagerUpdateSystem:
    """Tests for ParuPackageManager update_system method."""

    def test_update_system_success(self, paru_manager):
        """Test updating system successfully."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Updating system..."
        mock_result.stderr = ""

        with patch.object(
            paru_manager, "_run_command", return_value=mock_result
        ):
            result = paru_manager.update_system()

        assert result.success is True

    def test_update_system_dry_run(self, paru_manager):
        """Test dry run system update."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = (
            "vim 9.0.1000-1 -> 9.0.1001-1\ngit 2.40.0-1 -> 2.40.1-1"
        )
        mock_result.stderr = ""

        with patch.object(
            paru_manager, "_run_command", return_value=mock_result
        ):
            result = paru_manager.update_system(dry_run=True)

        assert result.success is True
        assert "upgradeable packages" in result.output.lower()

    def test_update_system_failure(self, paru_manager):
        """Test system update failure."""
        with patch.object(
            paru_manager,
            "_run_command",
            side_effect=PackageManagerError("Update failed"),
        ):
            result = paru_manager.update_system()

        assert result.success is False
        assert result.error_message is not None


class TestParuPackageManagerIsInstalled:
    """Tests for ParuPackageManager is_installed method."""

    def test_is_installed_true(self, paru_manager):
        """Test checking if installed package exists."""
        mock_result = MagicMock()
        mock_result.returncode = 0

        with patch.object(
            paru_manager, "_run_command", return_value=mock_result
        ):
            result = paru_manager.is_installed("vim")

        assert result is True

    def test_is_installed_false(self, paru_manager):
        """Test checking if non-installed package exists."""
        mock_result = MagicMock()
        mock_result.returncode = 1

        with patch.object(
            paru_manager, "_run_command", return_value=mock_result
        ):
            result = paru_manager.is_installed("nonexistent")

        assert result is False


class TestParuPackageManagerGetPackageInfo:
    """Tests for ParuPackageManager get_package_info method."""

    def test_get_package_info_installed(self, paru_manager):
        """Test getting info for installed package."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = """Name            : vim
Version         : 9.0.1000-1
Description     : Vi Improved
Repository      : core
Installed Size  : 10.5 MiB"""

        with patch.object(
            paru_manager, "_run_command", return_value=mock_result
        ):
            info = paru_manager.get_package_info("vim")

        assert info is not None
        assert info.name == "vim"

    def test_get_package_info_not_found(self, paru_manager):
        """Test getting info for non-existent package."""
        mock_result = MagicMock()
        mock_result.returncode = 1

        with patch.object(
            paru_manager, "_run_command", return_value=mock_result
        ):
            info = paru_manager.get_package_info("nonexistent")

        assert info is None
