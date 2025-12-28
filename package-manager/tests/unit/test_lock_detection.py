"""Unit tests for lock file detection."""

import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from dotfiles_package_manager.core.lock import (
    LockStatus,
    LockCheckResult,
    check_pacman_lock,
    check_apt_lock,
    check_dnf_lock,
    _is_process_running,
    _get_lock_holder_pid,
)


class TestIsProcessRunning:
    """Tests for _is_process_running helper."""

    def test_returns_true_for_current_process(self):
        """Current process should be detected as running."""
        assert _is_process_running(os.getpid()) is True

    def test_returns_false_for_nonexistent_pid(self):
        """Non-existent PID should return False."""
        # Use a very high PID that's unlikely to exist
        assert _is_process_running(999999999) is False


class TestCheckPacmanLock:
    """Tests for check_pacman_lock."""

    def test_no_lock_when_file_missing(self):
        """Returns NO_LOCK when lock file doesn't exist."""
        with patch.object(Path, "exists", return_value=False):
            result = check_pacman_lock()

        assert result.status == LockStatus.NO_LOCK
        assert result.lock_file is None

    def test_stale_lock_when_no_process(self):
        """Returns STALE_LOCK when file exists but no process."""
        with patch.object(Path, "exists", return_value=True):
            with patch(
                "dotfiles_package_manager.core.lock._get_lock_holder_pid",
                return_value=None,
            ):
                result = check_pacman_lock()

        assert result.status == LockStatus.STALE_LOCK
        assert result.is_stale is True
        assert "sudo rm" in result.message

    def test_active_lock_when_process_running(self):
        """Returns ACTIVE_LOCK when process is holding lock."""
        with patch.object(Path, "exists", return_value=True):
            with patch(
                "dotfiles_package_manager.core.lock._get_lock_holder_pid",
                return_value=1234,
            ):
                with patch(
                    "dotfiles_package_manager.core.lock._is_process_running",
                    return_value=True,
                ):
                    result = check_pacman_lock()

        assert result.status == LockStatus.ACTIVE_LOCK
        assert result.holding_pid == 1234
        assert result.is_locked is True
        assert result.is_stale is False


class TestCheckAptLock:
    """Tests for check_apt_lock."""

    def test_no_lock_when_files_missing(self):
        """Returns NO_LOCK when no lock files exist."""
        with patch.object(Path, "exists", return_value=False):
            result = check_apt_lock()

        assert result.status == LockStatus.NO_LOCK

    def test_active_lock_for_first_locked_file(self):
        """Returns ACTIVE_LOCK for first locked file found."""
        with patch.object(Path, "exists", return_value=True):
            with patch(
                "dotfiles_package_manager.core.lock._get_lock_holder_pid",
                return_value=5678,
            ):
                with patch(
                    "dotfiles_package_manager.core.lock._is_process_running",
                    return_value=True,
                ):
                    result = check_apt_lock()

        assert result.status == LockStatus.ACTIVE_LOCK
        assert result.holding_pid == 5678


class TestCheckDnfLock:
    """Tests for check_dnf_lock."""

    def test_no_lock_when_files_missing(self):
        """Returns NO_LOCK when no lock files exist."""
        with patch.object(Path, "exists", return_value=False):
            result = check_dnf_lock()

        assert result.status == LockStatus.NO_LOCK

    def test_active_lock_from_pid_file(self):
        """Returns ACTIVE_LOCK when PID in lock file is running."""
        mock_file = MagicMock()
        mock_file.read_text.return_value = "9999"
        mock_file.exists.return_value = True

        with patch("pathlib.Path.__new__") as mock_path:
            mock_path.return_value = mock_file
            with patch(
                "dotfiles_package_manager.core.lock._is_process_running",
                return_value=True,
            ):
                result = check_dnf_lock()

        assert result.status == LockStatus.ACTIVE_LOCK


class TestLockCheckResult:
    """Tests for LockCheckResult dataclass."""

    def test_is_locked_true_for_active(self):
        """is_locked is True for ACTIVE_LOCK."""
        result = LockCheckResult(status=LockStatus.ACTIVE_LOCK)
        assert result.is_locked is True

    def test_is_locked_true_for_stale(self):
        """is_locked is True for STALE_LOCK."""
        result = LockCheckResult(status=LockStatus.STALE_LOCK)
        assert result.is_locked is True

    def test_is_locked_false_for_no_lock(self):
        """is_locked is False for NO_LOCK."""
        result = LockCheckResult(status=LockStatus.NO_LOCK)
        assert result.is_locked is False

    def test_is_stale_true_only_for_stale(self):
        """is_stale is True only for STALE_LOCK."""
        assert LockCheckResult(status=LockStatus.STALE_LOCK).is_stale is True
        assert LockCheckResult(status=LockStatus.ACTIVE_LOCK).is_stale is False
        assert LockCheckResult(status=LockStatus.NO_LOCK).is_stale is False
