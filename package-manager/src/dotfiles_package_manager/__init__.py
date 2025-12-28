"""Package manager abstraction for Linux systems (Arch, Debian, RedHat)."""

from dotfiles_package_manager.core.base import (
    PackageInfo,
    PackageManager,
    PackageManagerError,
    PackageManagerTimeoutError,
    PackageManagerLockError,
)
from dotfiles_package_manager.core.factory import (
    PackageManagerFactory,
    detect_distribution_family,
)
from dotfiles_package_manager.core.types import (
    DistributionFamily,
    InstallResult,
    PackageManagerType,
    SearchResult,
)

__all__ = [
    "PackageManager",
    "PackageManagerError",
    "PackageManagerTimeoutError",
    "PackageManagerLockError",
    "PackageInfo",
    "PackageManagerFactory",
    "PackageManagerType",
    "DistributionFamily",
    "InstallResult",
    "SearchResult",
    "detect_distribution_family",
]
