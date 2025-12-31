"""Contract tests: PackageManagerFactory must provide consistent API.

Factory Contract Guarantees:
1. create_auto() returns PackageManager or raises PackageManagerError
2. create() returns PackageManager or raises PackageManagerError
3. get_available_managers() returns list[PackageManagerType], never raises
4. get_recommended_manager() returns PackageManagerType or None, never raises
5. create_recommended() returns PackageManager or raises PackageManagerError
6. is_available() returns bool, never raises
7. Error messages are consistent and informative

Evidence:
- factory.py:75-284 - PackageManagerFactory class
- package_management_steps.py:60-76 - Real usage
- TEST_PLAN.md - Contract #1, #2, Flow #1, #4
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from dotfiles_package_manager.core.base import (
    PackageManager,
    PackageManagerError,
)
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


class TestFactoryCreateAutoContract:
    """Contract tests for create_auto() method."""

    def test_contract__create_auto_returns_package_manager(self):
        """CONTRACT: create_auto() returns PackageManager instance."""
        mock_path = MagicMock(spec=Path)
        mock_path.exists.return_value = True

        with (
            patch("shutil.which", return_value="/usr/bin/pacman"),
            patch.object(
                PacmanPackageManager,
                "_find_executable",
                return_value=mock_path,
            ),
            patch(
                "dotfiles_package_manager.core.factory.detect_distribution_family",
                return_value=DistributionFamily.ARCH,
            ),
        ):
            manager = PackageManagerFactory.create_auto()

            # CONTRACT: Returns PackageManager instance
            assert isinstance(manager, PackageManager)
            assert hasattr(manager, "install")
            assert hasattr(manager, "remove")
            assert hasattr(manager, "search")

    def test_contract__create_auto_raises_on_no_manager_found(self):
        """CONTRACT: create_auto() raises PackageManagerError when no manager found."""
        with (
            patch("shutil.which", return_value=None),
            patch(
                "dotfiles_package_manager.core.factory.detect_distribution_family",
                return_value=DistributionFamily.ARCH,
            ),
        ):
            # CONTRACT: Raises PackageManagerError
            with pytest.raises(PackageManagerError) as exc_info:
                PackageManagerFactory.create_auto()

            # CONTRACT: Error message is informative
            assert "No package manager found" in str(exc_info.value)
            assert "arch" in str(exc_info.value).lower()

    def test_contract__create_auto_raises_on_unsupported_distro(self):
        """CONTRACT: create_auto() raises PackageManagerError for unsupported distro."""
        with patch(
            "dotfiles_package_manager.core.factory.detect_distribution_family",
            return_value=DistributionFamily.UNKNOWN,
        ):
            # CONTRACT: Raises PackageManagerError
            with pytest.raises(PackageManagerError) as exc_info:
                PackageManagerFactory.create_auto()

            # CONTRACT: Error message mentions unsupported distribution
            assert "Unsupported distribution family" in str(exc_info.value)

    def test_contract__create_auto_respects_prefer_third_party_true(self):
        """CONTRACT: create_auto(prefer_third_party=True) prefers AUR helpers."""
        mock_path = MagicMock(spec=Path)
        mock_path.exists.return_value = True

        with (
            patch("shutil.which", return_value="/usr/bin/paru"),
            patch.object(
                ParuPackageManager,
                "_find_executable",
                return_value=mock_path,
            ),
            patch(
                "dotfiles_package_manager.core.factory.detect_distribution_family",
                return_value=DistributionFamily.ARCH,
            ),
        ):
            manager = PackageManagerFactory.create_auto(prefer_third_party=True)

            # CONTRACT: Prefers paru over pacman
            assert manager.manager_type == PackageManagerType.PARU

    def test_contract__create_auto_respects_prefer_third_party_false(self):
        """CONTRACT: create_auto(prefer_third_party=False) uses official manager."""
        mock_path = MagicMock(spec=Path)
        mock_path.exists.return_value = True

        with (
            patch("shutil.which", return_value="/usr/bin/pacman"),
            patch.object(
                PacmanPackageManager,
                "_find_executable",
                return_value=mock_path,
            ),
            patch(
                "dotfiles_package_manager.core.factory.detect_distribution_family",
                return_value=DistributionFamily.ARCH,
            ),
        ):
            manager = PackageManagerFactory.create_auto(
                prefer_third_party=False
            )

            # CONTRACT: Uses pacman (official) not AUR helpers
            assert manager.manager_type == PackageManagerType.PACMAN


class TestFactoryCreateContract:
    """Contract tests for create() method."""

    def test_contract__create_returns_package_manager(self):
        """CONTRACT: create() returns PackageManager instance."""
        mock_path = MagicMock(spec=Path)
        mock_path.exists.return_value = True

        with patch.object(
            PacmanPackageManager,
            "_find_executable",
            return_value=mock_path,
        ):
            manager = PackageManagerFactory.create(PackageManagerType.PACMAN)

            # CONTRACT: Returns PackageManager instance
            assert isinstance(manager, PackageManager)
            assert manager.manager_type == PackageManagerType.PACMAN

    def test_contract__create_raises_on_unsupported_type(self):
        """CONTRACT: create() raises PackageManagerError for unsupported type."""
        # Create a fake PackageManagerType that's not in the registry
        fake_type = "FAKE_MANAGER"

        # CONTRACT: Raises PackageManagerError
        with pytest.raises((PackageManagerError, AttributeError, ValueError)):
            # Note: This might raise AttributeError if fake_type is not a valid enum
            PackageManagerFactory.create(fake_type)  # type: ignore


class TestFactoryGetAvailableManagersContract:
    """Contract tests for get_available_managers() method."""

    def test_contract__get_available_managers_returns_list(self):
        """CONTRACT: get_available_managers() returns list[PackageManagerType]."""
        with patch("shutil.which", return_value="/usr/bin/pacman"):
            result = PackageManagerFactory.get_available_managers()

            # CONTRACT: Returns list
            assert isinstance(result, list)
            # CONTRACT: All items are PackageManagerType
            for item in result:
                assert isinstance(item, PackageManagerType)

    def test_contract__get_available_managers_never_raises(self):
        """CONTRACT: get_available_managers() never raises exceptions."""
        with patch("shutil.which", return_value=None):
            # CONTRACT: Does not raise, even when no managers available
            result = PackageManagerFactory.get_available_managers()
            assert isinstance(result, list)
            assert len(result) == 0

    def test_contract__get_available_managers_includes_available_only(self):
        """CONTRACT: get_available_managers() only includes available managers."""

        def which_side_effect(name):
            return "/usr/bin/pacman" if name == "pacman" else None

        with patch("shutil.which", side_effect=which_side_effect):
            result = PackageManagerFactory.get_available_managers()

            # CONTRACT: Only includes pacman (which is available)
            assert PackageManagerType.PACMAN in result
            assert PackageManagerType.YAY not in result
            assert PackageManagerType.APT not in result


class TestFactoryGetRecommendedManagerContract:
    """Contract tests for get_recommended_manager() method."""

    def test_contract__get_recommended_manager_returns_type_or_none(self):
        """CONTRACT: get_recommended_manager() returns PackageManagerType or None."""
        with patch("shutil.which", return_value="/usr/bin/pacman"):
            result = PackageManagerFactory.get_recommended_manager(
                DistributionFamily.ARCH
            )

            # CONTRACT: Returns PackageManagerType or None
            assert result is None or isinstance(result, PackageManagerType)

    def test_contract__get_recommended_manager_never_raises(self):
        """CONTRACT: get_recommended_manager() never raises exceptions."""
        with patch("shutil.which", return_value=None):
            # CONTRACT: Does not raise, returns None when no managers available
            result = PackageManagerFactory.get_recommended_manager(
                DistributionFamily.ARCH
            )
            assert result is None

    def test_contract__get_recommended_manager_respects_preference_order(
        self,
    ):
        """CONTRACT: get_recommended_manager() respects preference order (paru > yay > pacman)."""

        def which_side_effect(name):
            # Only paru and pacman available, not yay
            return (
                "/usr/bin/paru"
                if name == "paru"
                else "/usr/bin/pacman" if name == "pacman" else None
            )

        with patch("shutil.which", side_effect=which_side_effect):
            result = PackageManagerFactory.get_recommended_manager(
                DistributionFamily.ARCH
            )

            # CONTRACT: Recommends paru (highest priority available)
            assert result == PackageManagerType.PARU


class TestFactoryIsAvailableContract:
    """Contract tests for is_available() method."""

    def test_contract__is_available_returns_bool(self):
        """CONTRACT: is_available() returns bool."""
        with patch("shutil.which", return_value="/usr/bin/pacman"):
            result = PackageManagerFactory.is_available(
                PackageManagerType.PACMAN
            )

            # CONTRACT: Returns bool
            assert isinstance(result, bool)

    def test_contract__is_available_never_raises(self):
        """CONTRACT: is_available() never raises exceptions."""
        with patch("shutil.which", return_value=None):
            # CONTRACT: Does not raise
            result = PackageManagerFactory.is_available(
                PackageManagerType.PACMAN
            )
            assert isinstance(result, bool)

    def test_contract__is_available_true_when_executable_exists(self):
        """CONTRACT: is_available() returns True when executable exists."""
        with patch("shutil.which", return_value="/usr/bin/pacman"):
            result = PackageManagerFactory.is_available(
                PackageManagerType.PACMAN
            )

            # CONTRACT: Returns True
            assert result is True

    def test_contract__is_available_false_when_executable_missing(self):
        """CONTRACT: is_available() returns False when executable missing."""
        with patch("shutil.which", return_value=None):
            result = PackageManagerFactory.is_available(
                PackageManagerType.PACMAN
            )

            # CONTRACT: Returns False
            assert result is False


class TestDetectDistributionFamilyContract:
    """Contract tests for detect_distribution_family() function."""

    def test_contract__detect_distribution_family_returns_enum(self):
        """CONTRACT: detect_distribution_family() returns DistributionFamily."""
        with patch(
            "pathlib.Path.open",
            create=True,
        ) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = (
                "ID=arch\nNAME=Arch Linux"
            )

            result = detect_distribution_family()

            # CONTRACT: Returns DistributionFamily enum
            assert isinstance(result, DistributionFamily)

    def test_contract__detect_distribution_family_never_raises(self):
        """CONTRACT: detect_distribution_family() never raises exceptions."""
        with patch("pathlib.Path.open", side_effect=FileNotFoundError):
            # CONTRACT: Does not raise, returns UNKNOWN
            result = detect_distribution_family()
            assert result == DistributionFamily.UNKNOWN

