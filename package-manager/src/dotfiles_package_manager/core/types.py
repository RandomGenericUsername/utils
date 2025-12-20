"""Core types and enums for package management."""

from dataclasses import dataclass
from enum import Enum


class DistributionFamily(Enum):
    """Linux distribution families."""

    ARCH = "arch"
    DEBIAN = "debian"
    REDHAT = "redhat"
    UNKNOWN = "unknown"


class PackageManagerType(Enum):
    """Supported package manager types."""

    # Arch Linux family
    PACMAN = "pacman"
    YAY = "yay"
    PARU = "paru"

    # Debian/Ubuntu family
    APT = "apt"
    APT_GET = "apt-get"

    # RedHat/Fedora/CentOS family
    DNF = "dnf"
    YUM = "yum"

    @property
    def distribution_family(self) -> DistributionFamily:
        """Get the distribution family for this package manager."""
        if self in (
            PackageManagerType.PACMAN,
            PackageManagerType.YAY,
            PackageManagerType.PARU,
        ):
            return DistributionFamily.ARCH
        elif self in (PackageManagerType.APT, PackageManagerType.APT_GET):
            return DistributionFamily.DEBIAN
        elif self in (PackageManagerType.DNF, PackageManagerType.YUM):
            return DistributionFamily.REDHAT
        return DistributionFamily.UNKNOWN

    @property
    def is_third_party_helper(self) -> bool:
        """
        Check if this is a third-party repository helper.

        Returns:
            True for AUR helpers (yay, paru), False otherwise.
            Note: apt and dnf handle third-party repos (PPAs, COPR) natively.
        """
        return self in (PackageManagerType.YAY, PackageManagerType.PARU)

    @property
    def requires_sudo(self) -> bool:
        """Check if this manager requires sudo for privileged operations."""
        # AUR helpers handle sudo internally
        return not self.is_third_party_helper


@dataclass
class PackageInfo:
    """Information about a package."""

    name: str
    version: str | None = None
    description: str | None = None
    repository: str | None = None
    installed: bool = False
    size: str | None = None
    dependencies: list[str] | None = None

    def __post_init__(self) -> None:
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class InstallResult:
    """Result of a package installation/removal operation."""

    success: bool
    packages_installed: list[str] | None = None
    packages_failed: list[str] | None = None
    output: str = ""
    error_message: str | None = None

    def __post_init__(self) -> None:
        if self.packages_installed is None:
            self.packages_installed = []
        if self.packages_failed is None:
            self.packages_failed = []


@dataclass
class SearchResult:
    """Result of a package search operation."""

    packages: list[PackageInfo] | None = None
    query: str = ""
    total_found: int = 0

    def __post_init__(self) -> None:
        if self.packages is None:
            self.packages = []
        if self.total_found == 0:
            self.total_found = len(self.packages)
