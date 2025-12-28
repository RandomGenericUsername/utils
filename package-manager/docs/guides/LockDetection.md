# Lock File Detection

The package manager library can detect when the package database is locked by another process.

## Overview

Package managers use lock files to prevent concurrent access:

| Distribution | Lock File |
|--------------|-----------|
| Arch (pacman/yay/paru) | `/var/lib/pacman/db.lck` |
| Debian (apt/dpkg) | `/var/lib/dpkg/lock`, `/var/lib/dpkg/lock-frontend` |
| RedHat (dnf/yum) | `/var/run/yum.pid`, `/var/lib/dnf/rpmdb_lock.pid` |

## Lock States

| State | Description |
|-------|-------------|
| `NO_LOCK` | No lock file exists |
| `ACTIVE_LOCK` | Lock file exists and a process is using it |
| `STALE_LOCK` | Lock file exists but no process is using it (safe to remove) |

## Usage

### Check Lock Before Install

```python
from dotfiles_package_manager import PackageManagerFactory

pm = PackageManagerFactory.create_auto()

# Check for locks
lock_result = pm.check_lock()

if lock_result.is_locked:
    if lock_result.is_stale:
        print(f"Stale lock detected: {lock_result.lock_file}")
        print(f"Remove with: sudo rm {lock_result.lock_file}")
    else:
        print(f"Active lock by PID {lock_result.holding_pid}")
        print("Wait for the process to finish.")
else:
    # Safe to proceed
    result = pm.install(["vim"])
```

### Automatic Lock Checking

The `install()` method automatically checks for locks and raises `PackageManagerLockError` if locked:

```python
from dotfiles_package_manager import (
    PackageManagerFactory,
    PackageManagerLockError,
)

pm = PackageManagerFactory.create_auto()

try:
    result = pm.install(["vim"])
except PackageManagerLockError as e:
    if e.is_stale:
        print(f"Remove stale lock: sudo rm {e.lock_file}")
    else:
        print(f"Wait for lock to be released")
```

## Common Issues

### Stale Lock After System Crash

If your system crashed or was force-restarted during a package operation, a stale lock file may remain.

**Solution:**
```bash
# Arch Linux
sudo rm /var/lib/pacman/db.lck

# Debian/Ubuntu
sudo rm /var/lib/dpkg/lock /var/lib/dpkg/lock-frontend

# Fedora/RHEL
sudo rm /var/run/yum.pid
```

### Lock Held by Background Process

System update services (like `packagekit` or `unattended-upgrades`) may hold locks.

**Solution:**
```bash
# Check what's holding the lock
sudo fuser /var/lib/pacman/db.lck  # Arch
sudo lsof /var/lib/dpkg/lock       # Debian

# Wait for the process or stop the service
sudo systemctl stop packagekit
```

## Lock Detection Mechanism

The lock detection uses:

1. **Process validation**: `os.kill(pid, 0)` signal-based check to non-destructively verify if a process exists
2. **Lock holder identification**: `fuser` command to find which process is holding a lock file
3. **Distribution-specific detection**: Each distribution has its own lock file locations and detection strategy
