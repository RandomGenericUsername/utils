"""Package manager factory for automatic detection and creation."""

import shutil
from pathlib import Path

from dotfiles_package_manager.core.base import (
    PackageManager,
    PackageManagerError,
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


def detect_distribution_family() -> DistributionFamily:
    """
    Detect the current Linux distribution family.

    Returns:
        DistributionFamily enum value
    """
    try:
        with Path("/etc/os-release").open() as f:
            content = f.read().lower()

            # Check for Arch-based
            if any(
                x in content
                for x in ["arch linux", "manjaro", "endeavouros", "artix"]
            ):
                return DistributionFamily.ARCH

            # Check for Debian-based
            elif any(
                x in content
                for x in ["debian", "ubuntu", "mint", "pop", "elementary"]
            ):
                return DistributionFamily.DEBIAN

            # Check for RedHat-based
            elif any(
                x in content
                for x in [
                    "fedora",
                    "rhel",
                    "red hat",
                    "centos",
                    "rocky",
                    "alma",
                    "oracle",
                ]
            ):
                return DistributionFamily.REDHAT

    except FileNotFoundError:
        pass

    return DistributionFamily.UNKNOWN


class PackageManagerFactory:
    """Factory for creating package manager instances."""

    # Registry of available package managers
    _MANAGERS = {
        # Arch Linux
        PackageManagerType.PACMAN: PacmanPackageManager,
        PackageManagerType.YAY: YayPackageManager,
        PackageManagerType.PARU: ParuPackageManager,
        # Debian/Ubuntu
        PackageManagerType.APT: AptPackageManager,
        # RedHat/Fedora
        PackageManagerType.DNF: DnfPackageManager,
    }

    @classmethod
    def create_auto(
        cls,
        prefer_third_party: bool = True,
        distribution_family: DistributionFamily | None = None,
    ) -> PackageManager:
        """
        Auto-detect and create the best available package manager.

        Args:
            prefer_third_party: Prefer managers with third-party repo
                support.
                - Arch: Prefer paru/yay over pacman (for AUR access)
                - Debian/RedHat: No effect (apt/dnf handle third-party
                  natively)
            distribution_family: Override automatic distribution
                detection

        Returns:
            PackageManager instance

        Raises:
            PackageManagerError: If no suitable package manager found
        """
        family = distribution_family or detect_distribution_family()

        # Define preference order per distribution family
        if family == DistributionFamily.ARCH:
            if prefer_third_party:
                # Prefer AUR helpers for third-party package access
                preferences = [
                    PackageManagerType.PARU,
                    PackageManagerType.YAY,
                    PackageManagerType.PACMAN,
                ]
            else:
                # Official repos only
                preferences = [PackageManagerType.PACMAN]

        elif family == DistributionFamily.DEBIAN:
            preferences = [PackageManagerType.APT]

        elif family == DistributionFamily.REDHAT:
            preferences = [PackageManagerType.DNF]

        else:
            raise PackageManagerError(
                f"Unsupported distribution family: {family.value}. "
                f"Cannot auto-detect package manager."
            )

        # Try each manager in preference order
        for manager_type in preferences:
            if cls._is_available(manager_type):
                try:
                    return cls.create(manager_type)
                except PackageManagerError:
                    continue

        raise PackageManagerError(
            f"No package manager found for {family.value}. "
            f"Tried: {', '.join(p.value for p in preferences)}"
        )

    @classmethod
    def create(cls, manager_type: PackageManagerType) -> PackageManager:
        """
        Create a specific package manager instance.

        Args:
            manager_type: Type of package manager to create

        Returns:
            PackageManager instance

        Raises:
            PackageManagerError: If package manager type is not
                supported or not available
        """
        if manager_type not in cls._MANAGERS:
            raise PackageManagerError(
                f"Unsupported package manager type: {manager_type}"
            )

        manager_class = cls._MANAGERS[manager_type]

        try:
            return manager_class()
        except PackageManagerError as e:
            raise PackageManagerError(
                f"Failed to create {manager_type.value} package manager: {e}"
            ) from e

    @classmethod
    def get_available_managers(cls) -> list[PackageManagerType]:
        """
        Get list of available package managers on the system.

        Returns:
            List of available package manager types
        """
        available = []
        for manager_type in cls._MANAGERS:
            if cls._is_available(manager_type):
                available.append(manager_type)
        return available

    @classmethod
    def is_available(cls, manager_type: PackageManagerType) -> bool:
        """
        Check if a specific package manager is available on the system.

        Args:
            manager_type: Package manager type to check

        Returns:
            True if available, False otherwise
        """
        return cls._is_available(manager_type)

    @classmethod
    def _is_available(cls, manager_type: PackageManagerType) -> bool:
        """
        Internal method to check if a package manager is available.

        Args:
            manager_type: Package manager type to check

        Returns:
            True if available, False otherwise
        """
        executable_name = manager_type.value
        return shutil.which(executable_name) is not None

    @classmethod
    def get_recommended_manager(
        cls, distribution_family: DistributionFamily | None = None
    ) -> PackageManagerType | None:
        """
        Get the recommended package manager for the system.

        Args:
            distribution_family: Override automatic distribution detection

        Returns:
            Recommended package manager type, or None if none available
        """
        family = distribution_family or detect_distribution_family()

        # Define preference order per distribution family
        if family == DistributionFamily.ARCH:
            preferences = [
                PackageManagerType.PARU,
                PackageManagerType.YAY,
                PackageManagerType.PACMAN,
            ]
        elif family == DistributionFamily.DEBIAN:
            preferences = [PackageManagerType.APT]
        elif family == DistributionFamily.REDHAT:
            preferences = [PackageManagerType.DNF]
        else:
            return None

        # Return first available from preferences
        for manager_type in preferences:
            if cls._is_available(manager_type):
                return manager_type

        return None

    @classmethod
    def create_recommended(
        cls, distribution_family: DistributionFamily | None = None
    ) -> PackageManager:
        """
        Create an instance of the recommended package manager.

        Args:
            distribution_family: Override automatic distribution detection

        Returns:
            PackageManager instance

        Raises:
            PackageManagerError: If no package manager is available
        """
        recommended = cls.get_recommended_manager(distribution_family)
        if recommended is None:
            family = distribution_family or detect_distribution_family()
            raise PackageManagerError(
                f"No package manager available for {family.value}"
            )

        return cls.create(recommended)
