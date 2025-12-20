"""Package manager implementations."""

from dotfiles_package_manager.implementations.arch import (
    ArchPackageManagerBase,
    PacmanPackageManager,
    ParuPackageManager,
    YayPackageManager,
)
from dotfiles_package_manager.implementations.debian import (
    AptPackageManager,
    DebianPackageManagerBase,
)
from dotfiles_package_manager.implementations.redhat import (
    DnfPackageManager,
    RedHatPackageManagerBase,
)

__all__ = [
    # Arch Linux
    "ArchPackageManagerBase",
    "PacmanPackageManager",
    "YayPackageManager",
    "ParuPackageManager",
    # Debian/Ubuntu
    "DebianPackageManagerBase",
    "AptPackageManager",
    # RedHat/Fedora
    "RedHatPackageManagerBase",
    "DnfPackageManager",
]
