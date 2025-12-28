"""Lock file detection for package managers."""

import os
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class LockStatus(Enum):
    """Status of a lock file."""

    NO_LOCK = "no_lock"
    ACTIVE_LOCK = "active_lock"
    STALE_LOCK = "stale_lock"


@dataclass
class LockCheckResult:
    """Result of checking for lock files."""

    status: LockStatus
    lock_file: Path | None = None
    holding_pid: int | None = None
    message: str = ""

    @property
    def is_locked(self) -> bool:
        """Check if there is any lock (active or stale)."""
        return self.status in (LockStatus.ACTIVE_LOCK, LockStatus.STALE_LOCK)

    @property
    def is_stale(self) -> bool:
        """Check if the lock is stale (can be safely removed)."""
        return self.status == LockStatus.STALE_LOCK


def _is_process_running(pid: int) -> bool:
    """Check if a process with given PID is running.

    Args:
        pid: Process ID to check

    Returns:
        True if process is running, False otherwise
    """
    try:
        # Check if process exists by sending signal 0
        os.kill(pid, 0)
        return True
    except (ProcessLookupError, PermissionError):
        # ProcessLookupError: No such process
        # PermissionError: Process exists but we can't signal it
        return False
    except OSError:
        return False


def _get_lock_holder_pid(lock_file: Path) -> int | None:
    """Get PID of process holding a lock file using fuser.

    Args:
        lock_file: Path to the lock file

    Returns:
        PID if found, None otherwise
    """
    try:
        result = subprocess.run(
            ["fuser", str(lock_file)],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.stdout.strip():
            # fuser outputs PIDs separated by spaces
            pids = result.stdout.strip().split()
            if pids:
                return int(pids[0])
    except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
        pass
    return None


def check_pacman_lock() -> LockCheckResult:
    """Check for pacman database lock.

    Lock file: /var/lib/pacman/db.lck

    Returns:
        LockCheckResult with status and details
    """
    lock_file = Path("/var/lib/pacman/db.lck")

    if not lock_file.exists():
        return LockCheckResult(
            status=LockStatus.NO_LOCK,
            message="No pacman lock file found",
        )

    # Check if any process is using the lock
    pid = _get_lock_holder_pid(lock_file)

    if pid is not None and _is_process_running(pid):
        return LockCheckResult(
            status=LockStatus.ACTIVE_LOCK,
            lock_file=lock_file,
            holding_pid=pid,
            message=f"Pacman database is locked by process {pid}. "
                    f"Wait for it to finish or check if it's stuck.",
        )
    else:
        return LockCheckResult(
            status=LockStatus.STALE_LOCK,
            lock_file=lock_file,
            message=f"Stale lock file found at {lock_file}. "
                    f"No process is using it. "
                    f"Remove with: sudo rm {lock_file}",
        )


def check_apt_lock() -> LockCheckResult:
    """Check for APT/dpkg locks.

    Lock files:
    - /var/lib/dpkg/lock
    - /var/lib/dpkg/lock-frontend
    - /var/lib/apt/lists/lock
    - /var/cache/apt/archives/lock

    Returns:
        LockCheckResult with status and details
    """
    lock_files = [
        Path("/var/lib/dpkg/lock"),
        Path("/var/lib/dpkg/lock-frontend"),
        Path("/var/lib/apt/lists/lock"),
        Path("/var/cache/apt/archives/lock"),
    ]

    for lock_file in lock_files:
        if not lock_file.exists():
            continue

        pid = _get_lock_holder_pid(lock_file)

        if pid is not None and _is_process_running(pid):
            return LockCheckResult(
                status=LockStatus.ACTIVE_LOCK,
                lock_file=lock_file,
                holding_pid=pid,
                message=f"APT database is locked by process {pid} ({lock_file}). "
                        f"Wait for it to finish or check if it's stuck.",
            )

    # Check for stale locks (file exists but no process)
    for lock_file in lock_files:
        if lock_file.exists():
            pid = _get_lock_holder_pid(lock_file)
            if pid is None or not _is_process_running(pid):
                return LockCheckResult(
                    status=LockStatus.STALE_LOCK,
                    lock_file=lock_file,
                    message=f"Stale lock file found at {lock_file}. "
                            f"Remove with: sudo rm {lock_file}",
                )

    return LockCheckResult(
        status=LockStatus.NO_LOCK,
        message="No APT lock files found",
    )


def check_dnf_lock() -> LockCheckResult:
    """Check for DNF/YUM locks.

    Lock files:
    - /var/run/yum.pid (YUM)
    - /var/lib/dnf/rpmdb_lock.pid (DNF)
    - /var/cache/dnf/metadata_lock.pid (DNF)

    Note: DNF handles locks better than other managers and can
    usually recover automatically from stale locks.

    Returns:
        LockCheckResult with status and details
    """
    lock_files = [
        Path("/var/run/yum.pid"),
        Path("/var/lib/dnf/rpmdb_lock.pid"),
        Path("/var/cache/dnf/metadata_lock.pid"),
    ]

    for lock_file in lock_files:
        if not lock_file.exists():
            continue

        # DNF stores PID in the lock file itself
        try:
            pid_str = lock_file.read_text().strip()
            if pid_str:
                pid = int(pid_str)
                if _is_process_running(pid):
                    return LockCheckResult(
                        status=LockStatus.ACTIVE_LOCK,
                        lock_file=lock_file,
                        holding_pid=pid,
                        message=f"DNF/YUM is locked by process {pid}. "
                                f"Wait for it to finish.",
                    )
        except (ValueError, PermissionError):
            pass

    # Check for stale locks
    for lock_file in lock_files:
        if lock_file.exists():
            return LockCheckResult(
                status=LockStatus.STALE_LOCK,
                lock_file=lock_file,
                message=f"Stale lock file found at {lock_file}. "
                        f"DNF usually handles this automatically, "
                        f"but you can remove with: sudo rm {lock_file}",
            )

    return LockCheckResult(
        status=LockStatus.NO_LOCK,
        message="No DNF lock files found",
    )
