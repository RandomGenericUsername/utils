"""Core package manager types and interfaces."""

from dotfiles_package_manager.core.base import (
    PackageInfo,
    PackageManager,
    PackageManagerError,
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
    "PackageInfo",
    "PackageManagerType",
    "DistributionFamily",
    "InstallResult",
    "SearchResult",
    "PackageManagerFactory",
    "detect_distribution_family",
]
