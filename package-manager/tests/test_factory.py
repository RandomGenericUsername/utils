"""Tests for package manager factory and distribution detection."""

from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from dotfiles_package_manager.core.base import PackageManagerError
from dotfiles_package_manager.core.factory import (
    PackageManagerFactory,
    detect_distribution_family,
)
from dotfiles_package_manager.core.types import (
    DistributionFamily,
    PackageManagerType,
)
from dotfiles_package_manager.implementations.arch.pacman import (
    PacmanPackageManager,
)
from dotfiles_package_manager.implementations.arch.paru import (
    ParuPackageManager,
)
from dotfiles_package_manager.implementations.arch.yay import YayPackageManager
from dotfiles_package_manager.implementations.debian.apt import (
    AptPackageManager,
)
from dotfiles_package_manager.implementations.redhat.dnf import (
    DnfPackageManager,
)


class TestDetectDistributionFamily:
    """Tests for distribution family detection."""

    def test_detect_arch_linux(self):
        """Test detection of Arch Linux."""
        os_release_content = """NAME="Arch Linux"
ID=arch
ID_LIKE=archlinux
PRETTY_NAME="Arch Linux"
"""
        with patch(
            "pathlib.Path.open", mock_open(read_data=os_release_content)
        ):
            result = detect_distribution_family()
            assert result == DistributionFamily.ARCH

    def test_detect_manjaro(self):
        """Test detection of Manjaro (Arch-based)."""
        os_release_content = """NAME="Manjaro Linux"
ID=manjaro
ID_LIKE=arch
PRETTY_NAME="Manjaro Linux"
"""
        with patch(
            "pathlib.Path.open", mock_open(read_data=os_release_content)
        ):
            result = detect_distribution_family()
            assert result == DistributionFamily.ARCH

    def test_detect_ubuntu(self):
        """Test detection of Ubuntu."""
        os_release_content = """NAME="Ubuntu"
ID=ubuntu
ID_LIKE=debian
PRETTY_NAME="Ubuntu 22.04 LTS"
"""
        with patch(
            "pathlib.Path.open", mock_open(read_data=os_release_content)
        ):
            result = detect_distribution_family()
            assert result == DistributionFamily.DEBIAN

    def test_detect_debian(self):
        """Test detection of Debian."""
        os_release_content = """NAME="Debian GNU/Linux"
ID=debian
PRETTY_NAME="Debian GNU/Linux 12 (bookworm)"
"""
        with patch(
            "pathlib.Path.open", mock_open(read_data=os_release_content)
        ):
            result = detect_distribution_family()
            assert result == DistributionFamily.DEBIAN

    def test_detect_fedora(self):
        """Test detection of Fedora."""
        os_release_content = """NAME="Fedora Linux"
ID=fedora
ID_LIKE=rhel
PRETTY_NAME="Fedora Linux 38"
"""
        with patch(
            "pathlib.Path.open", mock_open(read_data=os_release_content)
        ):
            result = detect_distribution_family()
            assert result == DistributionFamily.REDHAT

    def test_detect_centos(self):
        """Test detection of CentOS."""
        os_release_content = """NAME="CentOS Linux"
ID=centos
ID_LIKE="rhel fedora"
PRETTY_NAME="CentOS Linux 8"
"""
        with patch(
            "pathlib.Path.open", mock_open(read_data=os_release_content)
        ):
            result = detect_distribution_family()
            assert result == DistributionFamily.REDHAT

    def test_detect_unknown_no_file(self):
        """Test detection when /etc/os-release doesn't exist."""
        with patch("pathlib.Path.open", side_effect=FileNotFoundError):
            result = detect_distribution_family()
            assert result == DistributionFamily.UNKNOWN

    def test_detect_unknown_unrecognized(self):
        """Test detection of unrecognized distribution."""
        os_release_content = """NAME="Unknown OS"
ID=unknown
PRETTY_NAME="Unknown OS 1.0"
"""
        with patch(
            "pathlib.Path.open", mock_open(read_data=os_release_content)
        ):
            result = detect_distribution_family()
            assert result == DistributionFamily.UNKNOWN


class TestPackageManagerFactoryIsAvailable:
    """Tests for checking package manager availability."""

    def test_is_available_pacman_found(self, mock_shutil_which):
        """Test is_available returns True when pacman is found."""
        mock_shutil_which.return_value = "/usr/bin/pacman"
        result = PackageManagerFactory.is_available(PackageManagerType.PACMAN)
        assert result is True
        mock_shutil_which.assert_called_once_with("pacman")

    def test_is_available_pacman_not_found(self, mock_shutil_which):
        """Test is_available returns False when pacman is not found."""
        mock_shutil_which.return_value = None
        result = PackageManagerFactory.is_available(PackageManagerType.PACMAN)
        assert result is False

    def test_is_available_apt_found(self, mock_shutil_which):
        """Test is_available returns True when apt is found."""
        mock_shutil_which.return_value = "/usr/bin/apt"
        result = PackageManagerFactory.is_available(PackageManagerType.APT)
        assert result is True
        mock_shutil_which.assert_called_once_with("apt")

    def test_is_available_yay_found(self, mock_shutil_which):
        """Test is_available returns True when yay is found."""
        mock_shutil_which.return_value = "/usr/bin/yay"
        result = PackageManagerFactory.is_available(PackageManagerType.YAY)
        assert result is True


class TestPackageManagerFactoryGetAvailableManagers:
    """Tests for getting list of available package managers."""

    def test_get_available_managers_none(self, mock_shutil_which):
        """Test get_available_managers when no managers are available."""
        mock_shutil_which.return_value = None
        result = PackageManagerFactory.get_available_managers()
        assert result == []

    def test_get_available_managers_pacman_only(self, mock_shutil_which):
        """Test get_available_managers when only pacman is available."""

        def which_side_effect(name):
            return "/usr/bin/pacman" if name == "pacman" else None

        mock_shutil_which.side_effect = which_side_effect
        result = PackageManagerFactory.get_available_managers()
        assert PackageManagerType.PACMAN in result
        assert PackageManagerType.YAY not in result
        assert PackageManagerType.APT not in result

    def test_get_available_managers_multiple(self, mock_shutil_which):
        """Test get_available_managers when multiple managers are available."""

        def which_side_effect(name):
            if name in ["pacman", "yay", "paru"]:
                return f"/usr/bin/{name}"
            return None

        mock_shutil_which.side_effect = which_side_effect
        result = PackageManagerFactory.get_available_managers()
        assert PackageManagerType.PACMAN in result
        assert PackageManagerType.YAY in result
        assert PackageManagerType.PARU in result


class TestPackageManagerFactoryGetRecommendedManager:
    """Tests for getting recommended package manager."""

    def test_get_recommended_manager_arch_paru(self, mock_shutil_which):
        """Test recommended manager for Arch (prefer paru)."""

        def which_side_effect(name):
            return f"/usr/bin/{name}" if name in ["pacman", "paru"] else None

        mock_shutil_which.side_effect = which_side_effect

        result = PackageManagerFactory.get_recommended_manager(
            DistributionFamily.ARCH
        )
        assert result == PackageManagerType.PARU

    def test_get_recommended_manager_arch_yay(self, mock_shutil_which):
        """Test recommended manager for Arch (yay if paru not available)."""

        def which_side_effect(name):
            return f"/usr/bin/{name}" if name in ["pacman", "yay"] else None

        mock_shutil_which.side_effect = which_side_effect

        result = PackageManagerFactory.get_recommended_manager(
            DistributionFamily.ARCH
        )
        assert result == PackageManagerType.YAY

    def test_get_recommended_manager_arch_pacman(self, mock_shutil_which):
        """Test recommended manager for Arch (pacman if no AUR helpers)."""

        def which_side_effect(name):
            return "/usr/bin/pacman" if name == "pacman" else None

        mock_shutil_which.side_effect = which_side_effect

        result = PackageManagerFactory.get_recommended_manager(
            DistributionFamily.ARCH
        )
        assert result == PackageManagerType.PACMAN

    def test_get_recommended_manager_debian(self, mock_shutil_which):
        """Test recommended manager for Debian."""
        mock_shutil_which.return_value = "/usr/bin/apt"

        result = PackageManagerFactory.get_recommended_manager(
            DistributionFamily.DEBIAN
        )
        assert result == PackageManagerType.APT

    def test_get_recommended_manager_redhat(self, mock_shutil_which):
        """Test recommended manager for RedHat."""
        mock_shutil_which.return_value = "/usr/bin/dnf"

        result = PackageManagerFactory.get_recommended_manager(
            DistributionFamily.REDHAT
        )
        assert result == PackageManagerType.DNF

    def test_get_recommended_manager_unknown(self, mock_shutil_which):
        """Test recommended manager for unknown distribution."""
        result = PackageManagerFactory.get_recommended_manager(
            DistributionFamily.UNKNOWN
        )
        assert result is None

    def test_get_recommended_manager_none_available(self, mock_shutil_which):
        """Test recommended manager when none are available."""
        mock_shutil_which.return_value = None

        result = PackageManagerFactory.get_recommended_manager(
            DistributionFamily.ARCH
        )
        assert result is None


class TestPackageManagerFactoryCreate:
    """Tests for creating specific package manager instances."""

    def test_create_pacman(self):
        """Test creating pacman package manager."""
        with patch.object(
            PacmanPackageManager,
            "_find_executable",
            return_value=Path("/usr/bin/pacman"),
        ):
            manager = PackageManagerFactory.create(PackageManagerType.PACMAN)
            assert manager is not None
            assert manager.manager_type == PackageManagerType.PACMAN

    def test_create_apt(self):
        """Test creating apt package manager."""
        with (
            patch.object(
                AptPackageManager,
                "_find_executable",
                return_value=Path("/usr/bin/apt"),
            ),
            patch("pathlib.Path.exists", return_value=True),
        ):
            manager = PackageManagerFactory.create(PackageManagerType.APT)
            assert manager is not None
            assert manager.manager_type == PackageManagerType.APT

    def test_create_dnf(self):
        """Test creating dnf package manager."""
        with (
            patch.object(
                DnfPackageManager,
                "_find_executable",
                return_value=Path("/usr/bin/dnf"),
            ),
            patch("pathlib.Path.exists", return_value=True),
        ):
            manager = PackageManagerFactory.create(PackageManagerType.DNF)
            assert manager is not None
            assert manager.manager_type == PackageManagerType.DNF

    def test_create_yay(self):
        """Test creating yay package manager."""
        with patch.object(
            YayPackageManager,
            "_find_executable",
            return_value=Path("/usr/bin/yay"),
        ):
            manager = PackageManagerFactory.create(PackageManagerType.YAY)
            assert manager is not None
            assert manager.manager_type == PackageManagerType.YAY

    def test_create_paru(self):
        """Test creating paru package manager."""
        with (
            patch.object(
                ParuPackageManager,
                "_find_executable",
                return_value=Path("/usr/bin/paru"),
            ),
            patch("pathlib.Path.exists", return_value=True),
        ):
            manager = PackageManagerFactory.create(PackageManagerType.PARU)
            assert manager is not None
            assert manager.manager_type == PackageManagerType.PARU

    def test_create_not_available(self):
        """Test creating package manager when executable not found."""
        with patch.object(
            PacmanPackageManager, "_find_executable", return_value=None
        ):
            with pytest.raises(PackageManagerError) as exc_info:
                PackageManagerFactory.create(PackageManagerType.PACMAN)
            assert "not found" in str(exc_info.value).lower()


class TestPackageManagerFactoryCreateAuto:
    """Tests for auto-creating package manager based on distribution."""

    def test_create_auto_arch_prefer_paru(self):
        """Test auto-create on Arch prefers paru when available."""
        with (
            patch(
                "dotfiles_package_manager.core.factory.detect_distribution_family",
                return_value=DistributionFamily.ARCH,
            ),
            patch(
                "dotfiles_package_manager.core.factory.shutil.which",
                side_effect=lambda x: (
                    f"/usr/bin/{x}" if x in ["pacman", "paru", "yay"] else None
                ),
            ),
            patch.object(
                PacmanPackageManager,
                "_find_executable",
                return_value=Path("/usr/bin/pacman"),
            ),
            patch.object(
                ParuPackageManager,
                "_find_executable",
                return_value=Path("/usr/bin/paru"),
            ),
            patch.object(
                YayPackageManager,
                "_find_executable",
                return_value=Path("/usr/bin/yay"),
            ),
            patch("pathlib.Path.exists", return_value=True),
        ):
            manager = PackageManagerFactory.create_auto(
                prefer_third_party=True
            )
            assert manager.manager_type == PackageManagerType.PARU

    def test_create_auto_arch_prefer_yay(self):
        """Test auto-create on Arch prefers yay when paru not available."""
        with (
            patch(
                "dotfiles_package_manager.core.factory.detect_distribution_family",
                return_value=DistributionFamily.ARCH,
            ),
            patch.object(
                PacmanPackageManager,
                "_find_executable",
                return_value=Path("/usr/bin/pacman"),
            ),
            patch.object(
                ParuPackageManager, "_find_executable", return_value=None
            ),
            patch.object(
                YayPackageManager,
                "_find_executable",
                return_value=Path("/usr/bin/yay"),
            ),
            patch("pathlib.Path.exists", return_value=True),
        ):
            manager = PackageManagerFactory.create_auto(
                prefer_third_party=True
            )
            assert manager.manager_type == PackageManagerType.YAY

    def test_create_auto_arch_no_third_party(self):
        """Test auto-create on Arch without third-party preference."""
        with (
            patch(
                "dotfiles_package_manager.core.factory.detect_distribution_family",
                return_value=DistributionFamily.ARCH,
            ),
            patch.object(
                PacmanPackageManager,
                "_find_executable",
                return_value=Path("/usr/bin/pacman"),
            ),
            patch("pathlib.Path.exists", return_value=True),
        ):
            manager = PackageManagerFactory.create_auto(
                prefer_third_party=False
            )
            assert manager.manager_type == PackageManagerType.PACMAN

    def test_create_auto_debian(self):
        """Test auto-create on Debian."""
        with (
            patch(
                "dotfiles_package_manager.core.factory.detect_distribution_family",
                return_value=DistributionFamily.DEBIAN,
            ),
            patch(
                "dotfiles_package_manager.core.factory.shutil.which",
                return_value="/usr/bin/apt",
            ),
            patch.object(
                AptPackageManager,
                "_find_executable",
                return_value=Path("/usr/bin/apt"),
            ),
            patch("pathlib.Path.exists", return_value=True),
        ):
            manager = PackageManagerFactory.create_auto()
            assert manager.manager_type == PackageManagerType.APT

    def test_create_auto_redhat(self):
        """Test auto-create on RedHat."""
        with (
            patch(
                "dotfiles_package_manager.core.factory.detect_distribution_family",
                return_value=DistributionFamily.REDHAT,
            ),
            patch(
                "dotfiles_package_manager.core.factory.shutil.which",
                return_value="/usr/bin/dnf",
            ),
            patch.object(
                DnfPackageManager,
                "_find_executable",
                return_value=Path("/usr/bin/dnf"),
            ),
            patch("pathlib.Path.exists", return_value=True),
        ):
            manager = PackageManagerFactory.create_auto()
            assert manager.manager_type == PackageManagerType.DNF

    def test_create_auto_unknown_distribution(self):
        """Test auto-create on unknown distribution raises error."""
        with patch(
            "dotfiles_package_manager.core.factory.detect_distribution_family",
            return_value=DistributionFamily.UNKNOWN,
        ):
            with pytest.raises(PackageManagerError) as exc_info:
                PackageManagerFactory.create_auto()
            assert "unsupported" in str(exc_info.value).lower()

    def test_create_auto_no_manager_available(self):
        """Test auto-create when no package manager is available."""
        with (
            patch(
                "dotfiles_package_manager.core.factory.detect_distribution_family",
                return_value=DistributionFamily.ARCH,
            ),
            patch("shutil.which", return_value=None),
        ):
            with pytest.raises(PackageManagerError) as exc_info:
                PackageManagerFactory.create_auto()
            assert "no package manager found" in str(exc_info.value).lower()


class TestPackageManagerFactoryCreateRecommended:
    """Tests for creating recommended package manager."""

    def test_create_recommended_arch(self):
        """Test creating recommended manager for Arch."""
        with (
            patch(
                "dotfiles_package_manager.core.factory.shutil.which",
                return_value="/usr/bin/paru",
            ),
            patch.object(
                ParuPackageManager,
                "_find_executable",
                return_value=Path("/usr/bin/paru"),
            ),
            patch("pathlib.Path.exists", return_value=True),
        ):
            manager = PackageManagerFactory.create_recommended(
                DistributionFamily.ARCH
            )
            assert manager.manager_type == PackageManagerType.PARU

    def test_create_recommended_debian(self):
        """Test creating recommended manager for Debian."""
        with (
            patch(
                "dotfiles_package_manager.core.factory.shutil.which",
                return_value="/usr/bin/apt",
            ),
            patch.object(
                AptPackageManager,
                "_find_executable",
                return_value=Path("/usr/bin/apt"),
            ),
            patch("pathlib.Path.exists", return_value=True),
        ):
            manager = PackageManagerFactory.create_recommended(
                DistributionFamily.DEBIAN
            )
            assert manager.manager_type == PackageManagerType.APT

    def test_create_recommended_redhat(self):
        """Test creating recommended manager for RedHat."""
        with (
            patch(
                "dotfiles_package_manager.core.factory.shutil.which",
                return_value="/usr/bin/dnf",
            ),
            patch.object(
                DnfPackageManager,
                "_find_executable",
                return_value=Path("/usr/bin/dnf"),
            ),
            patch("pathlib.Path.exists", return_value=True),
        ):
            manager = PackageManagerFactory.create_recommended(
                DistributionFamily.REDHAT
            )
            assert manager.manager_type == PackageManagerType.DNF

    def test_create_recommended_none_available(self):
        """Test creating recommended manager when none available."""
        with patch("shutil.which", return_value=None):
            with pytest.raises(PackageManagerError) as exc_info:
                PackageManagerFactory.create_recommended(
                    DistributionFamily.ARCH
                )
            assert (
                "no package manager available" in str(exc_info.value).lower()
            )

    def test_create_recommended_unknown_distribution(self):
        """Test creating recommended manager for unknown distribution."""
        with pytest.raises(PackageManagerError) as exc_info:
            PackageManagerFactory.create_recommended(
                DistributionFamily.UNKNOWN
            )
        assert "no package manager available" in str(exc_info.value).lower()
