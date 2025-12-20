# Arch Linux Partial Upgrades

## Overview

This document explains the partial upgrade issue specific to Arch Linux and how the package-manager module prevents it.

## The Problem

**Partial upgrades are not supported on Arch Linux.** This is a critical difference between Arch (rolling release) and other distributions (stable/versioned releases).

### What is a Partial Upgrade?

A partial upgrade occurs when you sync the package databases (`-Sy`) and install a package without upgrading the entire system (`-u`).

```bash
# ❌ WRONG - Partial Upgrade
yay -Sy thunderbird
```

This command:
1. Syncs package databases (gets latest package information)
2. Installs `thunderbird` with its dependencies
3. **Does NOT upgrade existing packages**

### Why is This Dangerous on Arch?

Arch Linux is a **rolling release** distribution where packages are constantly updated. When you sync databases without upgrading, you can create library version mismatches.

**Example Scenario:**

```
Day 1: Your system state
├── libvpx.so.8 (installed)
├── ffmpeg (depends on libvpx.so.8)
└── thunderbird (not installed)

You run: yay -Sy thunderbird

Package database now shows:
├── libvpx.so.9 (available in repos)
├── thunderbird (requires libvpx.so.9)

Result after install:
├── libvpx.so.8 (still installed - NOT upgraded)
├── libvpx.so.9 (newly installed for thunderbird)
├── ffmpeg (still depends on libvpx.so.8 - BROKEN!)
└── thunderbird (uses libvpx.so.9 - works)

Error: ffmpeg: error while loading shared libraries: libvpx.so.8: cannot open shared object file
```

### Real-World Impact

This causes:
- **Broken dependencies**: Applications fail to start
- **Library conflicts**: Multiple versions of the same library
- **System instability**: Critical system components may break
- **Difficult recovery**: Requires manual intervention to fix

## The Solution

### Proper Package Installation on Arch

There are three correct approaches:

#### 1. Full System Upgrade First (Recommended)

```bash
# Step 1: Full system upgrade
yay -Syu

# Step 2: Install package
yay -S thunderbird
```

#### 2. Single Command Method

```bash
# Upgrade system and install package in one command
yay -Syu thunderbird
```

#### 3. Install Only (If System Already Updated)

```bash
# Safe only if you just ran yay -Syu
yay -S thunderbird
```

### Implementation in This Module

The package-manager module implements **Option 1** (separated operations) for clarity and error handling:

```python
def install(self, packages: list[str], update_system: bool = False) -> InstallResult:
    """Install packages using yay."""
    if not packages:
        return InstallResult(success=True, packages_installed=[], packages_failed=[])

    # Perform full system upgrade first if requested
    if update_system:
        upgrade_result = self.update_system(dry_run=False)
        if not upgrade_result.success:
            return InstallResult(
                success=False,
                packages_installed=[],
                packages_failed=packages.copy(),
                error_message=f"System upgrade failed: {upgrade_result.error_message}",
            )

    # Install packages with -S only (no -y)
    command = [str(self.executable_path), "-S", "--noconfirm"]
    command.extend(packages)
```

The `update_system()` method uses `-Syu`:

```python
def update_system(self, dry_run: bool = False) -> InstallResult:
    """Update system packages.

    Performs a full system upgrade (-Syu) to prevent partial upgrades.
    """
    if dry_run:
        command = [str(self.executable_path), "-Qu"]
    else:
        # Use -Syu for full system upgrade (sync + upgrade)
        command = [str(self.executable_path), "-Syu", "--noconfirm"]
```

## Comparison with Other Distributions

| Distribution | Partial Upgrade Issue? | Reason |
|--------------|------------------------|---------|
| **Arch/EndeavourOS/Manjaro** | ❌ **Critical Issue** | Rolling release: constant updates cause library mismatches |
| **Debian/Ubuntu** | ✅ **Not an Issue** | Stable releases: packages tested together, metadata updates safe |
| **Fedora/RedHat/CentOS** | ✅ **Not an Issue** | Versioned releases: controlled update cycles |

### Why APT and DNF Don't Have This Issue

**APT (Debian/Ubuntu):**
- `apt update` = Update package metadata only (safe)
- `apt upgrade` = Upgrade installed packages (separate operation)
- `apt install` = Install specific packages
- Packages are tested together in stable releases

**DNF (Fedora/RedHat):**
- `dnf check-update` = Check for updates (metadata refresh)
- `dnf upgrade` = Upgrade installed packages (separate operation)
- `dnf install` = Install specific packages
- Versioned releases with controlled update cycles

## References

- [Arch Wiki: System Maintenance](https://wiki.archlinux.org/title/System_maintenance#Partial_upgrades_are_unsupported)
- [Arch Wiki: Pacman](https://wiki.archlinux.org/title/Pacman#Upgrading_packages)
- Feature Request: `feature_request/proper_yay_package_installation.md`

## Implementation Details

### Affected Files

- `src/dotfiles_package_manager/implementations/arch/pacman.py`
- `src/dotfiles_package_manager/implementations/arch/yay.py`
- `src/dotfiles_package_manager/implementations/arch/paru.py`

### Changes Made

1. **`update_system()` method**: Changed from `-Sy` to `-Syu`
2. **`install()` method**: Separated operations when `update_system=True`
3. **Tests**: Updated to verify correct behavior

### Testing

All tests pass (63/63):
```bash
cd src/common/modules/package-manager
uv sync --all-extras
uv run pytest tests/test_yay.py tests/test_paru.py tests/test_pacman.py -v
```
