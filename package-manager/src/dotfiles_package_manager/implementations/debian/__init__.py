"""Debian/Ubuntu package manager implementations."""

from dotfiles_package_manager.implementations.debian.apt import (
    AptPackageManager,
)
from dotfiles_package_manager.implementations.debian.base import (
    DebianPackageManagerBase,
)

__all__ = [
    "DebianPackageManagerBase",
    "AptPackageManager",
]
