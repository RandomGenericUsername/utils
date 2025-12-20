"""RedHat/Fedora package manager implementations."""

from dotfiles_package_manager.implementations.redhat.base import (
    RedHatPackageManagerBase,
)
from dotfiles_package_manager.implementations.redhat.dnf import (
    DnfPackageManager,
)

__all__ = [
    "RedHatPackageManagerBase",
    "DnfPackageManager",
]
