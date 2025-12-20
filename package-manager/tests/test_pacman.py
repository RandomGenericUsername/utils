"""Tests for Pacman package manager implementation."""

import subprocess
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from dotfiles_package_manager.core.types import PackageManagerType
from dotfiles_package_manager.implementations.arch.pacman import (
    PacmanPackageManager,
)


@pytest.fixture
def pacman_manager(tmp_path):
    """Create a PacmanPackageManager instance for testing."""
    executable = tmp_path / "pacman"
    executable.touch()
    with patch.object(
        PacmanPackageManager, "_find_executable", return_value=executable
    ):
        manager = PacmanPackageManager()
        return manager


class TestPacmanManagerInit:
    """Tests for PacmanPackageManager initialization."""

    def test_manager_type(self, pacman_manager):
        """Test that manager type is PACMAN."""
        assert pacman_manager.manager_type == PackageManagerType.PACMAN

    def test_find_executable_with_pacman_available(self):
        """Test finding pacman executable when available."""
        with (
            patch(
                "dotfiles_package_manager.implementations.arch.pacman.shutil.which",  # noqa: E501
                return_value="/usr/bin/pacman",
            ),
            patch("pathlib.Path.exists", return_value=True),
        ):
            manager = PacmanPackageManager()
            assert manager.executable_path == Path("/usr/bin/pacman")


class TestPacmanInstall:
    """Tests for Pacman install method."""

    def test_install_empty_list(self, pacman_manager):
        """Test installing empty package list."""
        result = pacman_manager.install([])
        assert result.success is True
        assert result.packages_installed == []
        assert result.packages_failed == []

    def test_install_single_package_success(self, pacman_manager):
        """Test successful installation of single package."""
        mock_result = Mock(spec=subprocess.CompletedProcess)
        mock_result.returncode = 0
        mock_result.stdout = "Installing vim..."
        mock_result.stderr = ""

        with patch.object(
            pacman_manager, "_run_command", return_value=mock_result
        ) as mock_run:
            result = pacman_manager.install(["vim"])

            assert result.success is True
            assert result.packages_installed == ["vim"]
            assert result.packages_failed == []
            assert result.output == "Installing vim..."

            # Verify command
            mock_run.assert_called_once()
            command = mock_run.call_args[0][0]
            assert command[0] == "sudo"
            assert "-S" in command
            assert "--noconfirm" in command
            assert "vim" in command

    def test_install_multiple_packages_success(self, pacman_manager):
        """Test successful installation of multiple packages."""
        mock_result = Mock(spec=subprocess.CompletedProcess)
        mock_result.returncode = 0
        mock_result.stdout = "Installing packages..."
        mock_result.stderr = ""

        with patch.object(
            pacman_manager, "_run_command", return_value=mock_result
        ):
            result = pacman_manager.install(["vim", "git", "htop"])

            assert result.success is True
            assert result.packages_installed == ["vim", "git", "htop"]
            assert result.packages_failed == []

    def test_install_with_update_system(self, pacman_manager):
        """Test installation with system update.

        Should perform full system upgrade first, then install packages.
        This prevents partial upgrades on Arch Linux.
        """
        mock_result = Mock(spec=subprocess.CompletedProcess)
        mock_result.returncode = 0
        mock_result.stdout = "Updating and installing..."
        mock_result.stderr = ""

        with patch.object(
            pacman_manager, "_run_command", return_value=mock_result
        ) as mock_run:
            result = pacman_manager.install(["vim"], update_system=True)

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

    def test_install_package_not_found(self, pacman_manager):
        """Test installation when package not found."""
        mock_result = Mock(spec=subprocess.CompletedProcess)
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "error: target not found: nonexistent"

        with patch.object(
            pacman_manager, "_run_command", return_value=mock_result
        ):
            result = pacman_manager.install(["nonexistent"])

            assert result.success is False
            assert result.packages_installed == []
            assert result.packages_failed == ["nonexistent"]
            assert "target not found" in result.error_message

    def test_install_partial_failure(self, pacman_manager):
        """Test installation with some packages failing."""
        mock_result = Mock(spec=subprocess.CompletedProcess)
        mock_result.returncode = 1
        mock_result.stdout = "Installing vim..."
        mock_result.stderr = "error: target not found: nonexistent"

        with patch.object(
            pacman_manager, "_run_command", return_value=mock_result
        ):
            result = pacman_manager.install(["vim", "nonexistent"])

            assert result.success is True  # At least one succeeded
            assert "vim" in result.packages_installed
            assert "nonexistent" in result.packages_failed


class TestPacmanRemove:
    """Tests for Pacman remove method."""

    def test_remove_empty_list(self, pacman_manager):
        """Test removing empty package list."""
        result = pacman_manager.remove([])
        assert result.success is True
        assert result.packages_installed == []
        assert result.packages_failed == []

    def test_remove_single_package_success(self, pacman_manager):
        """Test successful removal of single package."""
        mock_result = Mock(spec=subprocess.CompletedProcess)
        mock_result.returncode = 0
        mock_result.stdout = "Removing vim..."
        mock_result.stderr = ""

        with patch.object(
            pacman_manager, "_run_command", return_value=mock_result
        ) as mock_run:
            result = pacman_manager.remove(["vim"])

            assert result.success is True
            assert result.packages_installed == [
                "vim"
            ]  # "installed" means "removed"
            assert result.packages_failed == []

            # Verify command
            command = mock_run.call_args[0][0]
            assert "sudo" in command
            assert "-R" in command
            assert "--noconfirm" in command
            assert "vim" in command

    def test_remove_with_dependencies(self, pacman_manager):
        """Test removal with dependencies."""
        mock_result = Mock(spec=subprocess.CompletedProcess)
        mock_result.returncode = 0
        mock_result.stdout = "Removing with dependencies..."
        mock_result.stderr = ""

        with patch.object(
            pacman_manager, "_run_command", return_value=mock_result
        ) as mock_run:
            result = pacman_manager.remove(["vim"], remove_dependencies=True)

            assert result.success is True
            command = mock_run.call_args[0][0]
            assert "-s" in command


class TestPacmanSearch:
    """Tests for Pacman search method."""

    def test_search_success(self, pacman_manager):
        """Test successful package search."""
        mock_result = Mock(spec=subprocess.CompletedProcess)
        mock_result.returncode = 0
        mock_result.stdout = """core/vim 9.0.1234-1
    Vi Improved, a highly configurable text editor
extra/neovim 0.9.0-1
    Fork of Vim aiming to improve user experience"""
        mock_result.stderr = ""

        with patch.object(
            pacman_manager, "_run_command", return_value=mock_result
        ):
            result = pacman_manager.search("vim")

            assert result.query == "vim"
            assert result.total_found == 2
            assert len(result.packages) == 2
            assert result.packages[0].name == "vim"
            assert result.packages[1].name == "neovim"

    def test_search_with_limit(self, pacman_manager):
        """Test search with result limit."""
        mock_result = Mock(spec=subprocess.CompletedProcess)
        mock_result.returncode = 0
        mock_result.stdout = """core/vim 9.0.1234-1
    Vi Improved
extra/neovim 0.9.0-1
    Fork of Vim
extra/gvim 9.0.1234-1
    GUI version"""
        mock_result.stderr = ""

        with patch.object(
            pacman_manager, "_run_command", return_value=mock_result
        ):
            result = pacman_manager.search("vim", limit=2)

            assert len(result.packages) == 2
            assert result.total_found == 2

    def test_search_no_results(self, pacman_manager):
        """Test search with no results."""
        mock_result = Mock(spec=subprocess.CompletedProcess)
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""

        with patch.object(
            pacman_manager, "_run_command", return_value=mock_result
        ):
            result = pacman_manager.search("nonexistent")

            assert result.query == "nonexistent"
            assert result.total_found == 0
            assert len(result.packages) == 0


class TestPacmanUpdateSystem:
    """Tests for Pacman update_system method."""

    def test_update_system_success(self, pacman_manager):
        """Test successful system update.

        Should use -Syu for full system upgrade to prevent partial upgrades.
        """
        mock_result = Mock(spec=subprocess.CompletedProcess)
        mock_result.returncode = 0
        mock_result.stdout = "Synchronizing package databases..."
        mock_result.stderr = ""

        with patch.object(
            pacman_manager, "_run_command", return_value=mock_result
        ) as mock_run:
            result = pacman_manager.update_system()

            assert result.success is True
            command = mock_run.call_args[0][0]
            assert "sudo" in command
            # Should use -Syu not -Sy to prevent partial upgrades
            assert "-Syu" in " ".join(command)

    def test_update_system_dry_run(self, pacman_manager):
        """Test system update dry run."""
        mock_result = Mock(spec=subprocess.CompletedProcess)
        mock_result.returncode = 0
        mock_result.stdout = (
            "vim 9.0.1234-1 -> 9.0.1235-1\ngit 2.40.0-1 -> 2.40.1-1"
        )
        mock_result.stderr = ""

        with patch.object(
            pacman_manager, "_run_command", return_value=mock_result
        ) as mock_run:
            result = pacman_manager.update_system(dry_run=True)

            assert result.success is True
            assert "2 upgradeable packages" in result.output
            command = mock_run.call_args[0][0]
            assert "-Qu" in command
            assert "sudo" not in command

    def test_update_system_dry_run_no_updates(self, pacman_manager):
        """Test dry run when system is up to date."""
        mock_result = Mock(spec=subprocess.CompletedProcess)
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""

        with patch.object(
            pacman_manager, "_run_command", return_value=mock_result
        ):
            result = pacman_manager.update_system(dry_run=True)

            assert result.success is True
            assert "up to date" in result.output.lower()


class TestPacmanIsInstalled:
    """Tests for Pacman is_installed method."""

    def test_is_installed_true(self, pacman_manager):
        """Test checking if package is installed (true)."""
        mock_result = Mock(spec=subprocess.CompletedProcess)
        mock_result.returncode = 0

        with patch.object(
            pacman_manager, "_run_command", return_value=mock_result
        ):
            assert pacman_manager.is_installed("vim") is True

    def test_is_installed_false(self, pacman_manager):
        """Test checking if package is installed (false)."""
        mock_result = Mock(spec=subprocess.CompletedProcess)
        mock_result.returncode = 1

        with patch.object(
            pacman_manager, "_run_command", return_value=mock_result
        ):
            assert pacman_manager.is_installed("nonexistent") is False


class TestPacmanGetPackageInfo:
    """Tests for Pacman get_package_info method."""

    def test_get_package_info_installed(self, pacman_manager):
        """Test getting info for installed package."""
        mock_result = Mock(spec=subprocess.CompletedProcess)
        mock_result.returncode = 0
        mock_result.stdout = """Name            : vim
Version         : 9.0.1234-1
Description     : Vi Improved
Repository      : core
Installed Size  : 50 MB
Depends On      : glibc ncurses"""
        mock_result.stderr = ""

        with patch.object(
            pacman_manager, "_run_command", return_value=mock_result
        ):
            info = pacman_manager.get_package_info("vim")

            assert info is not None
            assert info.name == "vim"
            assert info.version == "9.0.1234-1"
            assert info.description == "Vi Improved"
            assert info.repository == "core"

    def test_get_package_info_not_found(self, pacman_manager):
        """Test getting info for non-existent package."""
        mock_result = Mock(spec=subprocess.CompletedProcess)
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "error: package 'nonexistent' was not found"

        with patch.object(
            pacman_manager, "_run_command", return_value=mock_result
        ):
            info = pacman_manager.get_package_info("nonexistent")
            assert info is None
