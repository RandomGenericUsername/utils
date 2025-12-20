"""Tests for base package manager class and exceptions."""

import subprocess
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from dotfiles_package_manager.core.base import (
    PackageInstallationError,
    PackageManager,
    PackageManagerError,
    PackageNotFoundError,
)
from dotfiles_package_manager.core.types import (
    InstallResult,
    PackageInfo,
    PackageManagerType,
    SearchResult,
)


class TestPackageManagerExceptions:
    """Tests for package manager exception classes."""

    def test_package_manager_error_basic(self):
        """Test basic PackageManagerError creation."""
        error = PackageManagerError("Test error")
        assert str(error) == "Test error"
        assert error.command is None
        assert error.exit_code is None

    def test_package_manager_error_with_command(self):
        """Test PackageManagerError with command."""
        error = PackageManagerError("Test error", command="apt install vim")
        assert str(error) == "Test error"
        assert error.command == "apt install vim"
        assert error.exit_code is None

    def test_package_manager_error_with_exit_code(self):
        """Test PackageManagerError with exit code."""
        error = PackageManagerError(
            "Test error", command="apt install vim", exit_code=1
        )
        assert str(error) == "Test error"
        assert error.command == "apt install vim"
        assert error.exit_code == 1

    def test_package_not_found_error(self):
        """Test PackageNotFoundError inherits from PackageManagerError."""
        error = PackageNotFoundError(
            "Package not found", command="apt search foo"
        )
        assert isinstance(error, PackageManagerError)
        assert str(error) == "Package not found"
        assert error.command == "apt search foo"

    def test_package_installation_error(self):
        """Test PackageInstallationError inherits from PackageManagerError."""
        error = PackageInstallationError(
            "Installation failed", command="apt install foo", exit_code=100
        )
        assert isinstance(error, PackageManagerError)
        assert str(error) == "Installation failed"
        assert error.command == "apt install foo"
        assert error.exit_code == 100


class ConcretePackageManager(PackageManager):
    """Concrete implementation for testing abstract base class."""

    def __init__(
        self,
        executable_path: Path | None = None,
        manager_type_value=PackageManagerType.PACMAN,
    ):
        self._manager_type = manager_type_value
        super().__init__(executable_path)

    @property
    def manager_type(self) -> PackageManagerType:
        return self._manager_type

    def _find_executable(self) -> Path | None:
        return Path("/usr/bin/test-pm")

    def install(
        self, packages: list[str], update_system: bool = False
    ) -> InstallResult:
        return InstallResult(
            success=True, packages_installed=packages, packages_failed=[]
        )

    def remove(
        self, packages: list[str], remove_dependencies: bool = False
    ) -> InstallResult:
        return InstallResult(
            success=True, packages_installed=[], packages_failed=[]
        )

    def search(self, query: str, limit: int | None = None) -> SearchResult:
        return SearchResult(packages=[], query=query, total_found=0)

    def update_system(self, dry_run: bool = False) -> InstallResult:
        return InstallResult(
            success=True, packages_installed=[], packages_failed=[]
        )

    def is_installed(self, package: str) -> bool:
        return False

    def get_package_info(self, package: str) -> PackageInfo | None:
        return None


class TestPackageManagerInit:
    """Tests for PackageManager initialization."""

    def test_init_with_valid_executable_path(self, tmp_path):
        """Test initialization with valid executable path."""
        executable = tmp_path / "test-pm"
        executable.touch()

        manager = ConcretePackageManager(executable_path=executable)
        assert manager.executable_path == executable

    def test_init_with_none_uses_find_executable(self):
        """Test initialization with None uses _find_executable."""
        with (
            patch.object(
                ConcretePackageManager,
                "_find_executable",
                return_value=Path("/usr/bin/test-pm"),
            ),
            patch("pathlib.Path.exists", return_value=True),
        ):
            manager = ConcretePackageManager(executable_path=None)
            assert manager.executable_path == Path("/usr/bin/test-pm")

    def test_init_with_nonexistent_path_raises_error(self, tmp_path):
        """Test initialization with nonexistent path raises error."""
        executable = tmp_path / "nonexistent"

        with pytest.raises(PackageManagerError) as exc_info:
            ConcretePackageManager(executable_path=executable)

        assert "not found" in str(exc_info.value).lower()

    def test_init_with_find_executable_returning_none(self):
        """Test initialization when _find_executable returns None."""
        with patch.object(
            ConcretePackageManager, "_find_executable", return_value=None
        ):
            with pytest.raises(PackageManagerError) as exc_info:
                ConcretePackageManager(executable_path=None)

            assert "not found" in str(exc_info.value).lower()


class TestPackageManagerRunCommand:
    """Tests for PackageManager._run_command method."""

    def test_run_command_success(self, tmp_path):
        """Test successful command execution."""
        executable = tmp_path / "test-pm"
        executable.touch()
        manager = ConcretePackageManager(executable_path=executable)

        mock_result = Mock(spec=subprocess.CompletedProcess)
        mock_result.returncode = 0
        mock_result.stdout = "success"
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            result = manager._run_command(["echo", "test"])

            assert result.returncode == 0
            assert result.stdout == "success"
            mock_run.assert_called_once_with(
                ["echo", "test"],
                capture_output=True,
                text=True,
                check=True,
                timeout=None,
            )

    def test_run_command_with_timeout(self, tmp_path):
        """Test command execution with timeout."""
        executable = tmp_path / "test-pm"
        executable.touch()
        manager = ConcretePackageManager(executable_path=executable)

        mock_result = Mock(spec=subprocess.CompletedProcess)
        mock_result.returncode = 0

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            manager._run_command(["echo", "test"], timeout=30)

            mock_run.assert_called_once_with(
                ["echo", "test"],
                capture_output=True,
                text=True,
                check=True,
                timeout=30,
            )

    def test_run_command_timeout_expired(self, tmp_path):
        """Test command execution when timeout expires."""
        executable = tmp_path / "test-pm"
        executable.touch()
        manager = ConcretePackageManager(executable_path=executable)

        with patch(
            "subprocess.run",
            side_effect=subprocess.TimeoutExpired(["sleep", "10"], 5),
        ):
            with pytest.raises(PackageManagerError) as exc_info:
                manager._run_command(["sleep", "10"], timeout=5)

            assert "timed out" in str(exc_info.value).lower()
            assert exc_info.value.command == "sleep 10"

    def test_run_command_called_process_error(self, tmp_path):
        """Test command execution when command fails."""
        executable = tmp_path / "test-pm"
        executable.touch()
        manager = ConcretePackageManager(executable_path=executable)

        error = subprocess.CalledProcessError(1, ["false"])
        with patch("subprocess.run", side_effect=error):
            with pytest.raises(PackageManagerError) as exc_info:
                manager._run_command(["false"])

            assert "failed" in str(exc_info.value).lower()
            assert exc_info.value.command == "false"
            assert exc_info.value.exit_code == 1

    def test_run_command_file_not_found(self, tmp_path):
        """Test command execution when executable not found."""
        executable = tmp_path / "test-pm"
        executable.touch()
        manager = ConcretePackageManager(executable_path=executable)

        with patch(
            "subprocess.run", side_effect=FileNotFoundError("nonexistent")
        ):
            with pytest.raises(PackageManagerError) as exc_info:
                manager._run_command(["nonexistent"])

            assert "not found" in str(exc_info.value).lower()

    def test_run_command_no_capture_output(self, tmp_path):
        """Test command execution without capturing output."""
        executable = tmp_path / "test-pm"
        executable.touch()
        manager = ConcretePackageManager(executable_path=executable)

        mock_result = Mock(spec=subprocess.CompletedProcess)
        mock_result.returncode = 0

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            manager._run_command(["echo", "test"], capture_output=False)

            mock_run.assert_called_once_with(
                ["echo", "test"],
                capture_output=False,
                text=True,
                check=True,
                timeout=None,
            )

    def test_run_command_no_check(self, tmp_path):
        """Test command execution without checking return code."""
        executable = tmp_path / "test-pm"
        executable.touch()
        manager = ConcretePackageManager(executable_path=executable)

        mock_result = Mock(spec=subprocess.CompletedProcess)
        mock_result.returncode = 1

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            result = manager._run_command(["false"], check=False)

            assert result.returncode == 1
            mock_run.assert_called_once_with(
                ["false"],
                capture_output=True,
                text=True,
                check=False,
                timeout=None,
            )


class TestPackageManagerAbstractMethods:
    """Tests for abstract method enforcement."""

    def test_cannot_instantiate_abstract_class(self):
        """Test that PackageManager cannot be instantiated directly."""
        with pytest.raises(TypeError) as exc_info:
            PackageManager()  # type: ignore

        assert "abstract" in str(exc_info.value).lower()

    def test_concrete_class_must_implement_all_methods(self):
        """Test that concrete class must implement all abstract methods."""

        class IncompletePackageManager(PackageManager):
            """Incomplete implementation missing some methods."""

            @property
            def manager_type(self) -> PackageManagerType:
                return PackageManagerType.PACMAN

        with pytest.raises(TypeError) as exc_info:
            IncompletePackageManager()  # type: ignore

        assert "abstract" in str(exc_info.value).lower()
