"""Contract tests for log level utility functions.

Test Intent:
    Verify the contracts of log level parsing and validation utilities

Behavior Protected:
    - String to LogLevels conversion
    - Verbosity to LogLevels conversion
    - Error handling for invalid inputs
    - Case-insensitive parsing
    - Abbreviation support
"""

import pytest

from rich_logging import (
    LogLevels,
    parse_log_level,
    validate_log_level_string,
    get_log_level_from_verbosity,
)


class TestValidateLogLevelString:
    """Contract tests for validate_log_level_string() function."""

    def test_validate_debug_lowercase(self):
        """Contract: 'debug' string returns DEBUG level."""
        result = validate_log_level_string("debug")
        assert result == LogLevels.DEBUG

    def test_validate_debug_uppercase(self):
        """Contract: 'DEBUG' string returns DEBUG level."""
        result = validate_log_level_string("DEBUG")
        assert result == LogLevels.DEBUG

    def test_validate_debug_mixed_case(self):
        """Contract: 'DeBuG' string returns DEBUG level (case-insensitive)."""
        result = validate_log_level_string("DeBuG")
        assert result == LogLevels.DEBUG

    def test_validate_info(self):
        """Contract: 'info' string returns INFO level."""
        result = validate_log_level_string("info")
        assert result == LogLevels.INFO

    def test_validate_warning(self):
        """Contract: 'warning' string returns WARNING level."""
        result = validate_log_level_string("warning")
        assert result == LogLevels.WARNING

    def test_validate_error(self):
        """Contract: 'error' string returns ERROR level."""
        result = validate_log_level_string("error")
        assert result == LogLevels.ERROR

    def test_validate_critical(self):
        """Contract: 'critical' string returns CRITICAL level."""
        result = validate_log_level_string("critical")
        assert result == LogLevels.CRITICAL

    def test_validate_debug_abbreviation_d(self):
        """Contract: 'd' abbreviation returns DEBUG level."""
        result = validate_log_level_string("d")
        assert result == LogLevels.DEBUG

    def test_validate_debug_abbreviation_D(self):
        """Contract: 'D' abbreviation returns DEBUG level."""
        result = validate_log_level_string("D")
        assert result == LogLevels.DEBUG

    def test_validate_info_abbreviation_i(self):
        """Contract: 'i' abbreviation returns INFO level."""
        result = validate_log_level_string("i")
        assert result == LogLevels.INFO

    def test_validate_warning_abbreviation_w(self):
        """Contract: 'w' abbreviation returns WARNING level."""
        result = validate_log_level_string("w")
        assert result == LogLevels.WARNING

    def test_validate_error_abbreviation_e(self):
        """Contract: 'e' abbreviation returns ERROR level."""
        result = validate_log_level_string("e")
        assert result == LogLevels.ERROR

    def test_validate_critical_abbreviation_c(self):
        """Contract: 'c' abbreviation returns CRITICAL level."""
        result = validate_log_level_string("c")
        assert result == LogLevels.CRITICAL

    def test_validate_invalid_string_raises_error(self):
        """Contract: Invalid string raises ValueError."""
        with pytest.raises(ValueError, match="Invalid log level"):
            validate_log_level_string("invalid")

    def test_validate_empty_string_raises_error(self):
        """Contract: Empty string raises ValueError."""
        with pytest.raises(ValueError, match="Invalid log level"):
            validate_log_level_string("")

    def test_validate_numeric_string_raises_error(self):
        """Contract: Numeric string raises ValueError."""
        with pytest.raises(ValueError, match="Invalid log level"):
            validate_log_level_string("123")


class TestGetLogLevelFromVerbosity:
    """Contract tests for get_log_level_from_verbosity() function."""

    def test_verbosity_0_returns_critical(self):
        """Contract: Verbosity 0 returns CRITICAL level."""
        result = get_log_level_from_verbosity(0)
        assert result == LogLevels.CRITICAL

    def test_verbosity_1_returns_warning(self):
        """Contract: Verbosity 1 returns WARNING level."""
        result = get_log_level_from_verbosity(1)
        assert result == LogLevels.WARNING

    def test_verbosity_2_returns_info(self):
        """Contract: Verbosity 2 returns INFO level."""
        result = get_log_level_from_verbosity(2)
        assert result == LogLevels.INFO

    def test_verbosity_3_returns_debug(self):
        """Contract: Verbosity 3 returns DEBUG level."""
        result = get_log_level_from_verbosity(3)
        assert result == LogLevels.DEBUG

    def test_verbosity_negative_raises_error(self):
        """Contract: Negative verbosity raises ValueError."""
        with pytest.raises(ValueError, match="Verbosity cannot be negative"):
            get_log_level_from_verbosity(-1)

    def test_verbosity_exceeds_max_raises_error(self):
        """Contract: Verbosity > 3 raises ValueError."""
        with pytest.raises(ValueError, match="exceeds maximum"):
            get_log_level_from_verbosity(4)


class TestParseLogLevel:
    """Contract tests for parse_log_level() function."""

    def test_parse_with_verbosity_ignores_string(self):
        """Contract: Verbosity > 0 takes precedence over log_level_str."""
        result = parse_log_level("error", verbosity=2, fallback=LogLevels.CRITICAL)
        # Verbosity 2 = INFO, not ERROR
        assert result == LogLevels.INFO

    def test_parse_with_log_level_string(self):
        """Contract: log_level_str is used when verbosity is 0."""
        result = parse_log_level("debug", verbosity=0, fallback=LogLevels.INFO)
        assert result == LogLevels.DEBUG

    def test_parse_with_fallback(self):
        """Contract: Fallback is used when both are None/0."""
        result = parse_log_level(None, verbosity=0, fallback=LogLevels.WARNING)
        assert result == LogLevels.WARNING

    def test_parse_verbosity_priority(self):
        """Contract: Verbosity has priority over log_level_str."""
        result = parse_log_level("critical", verbosity=3, fallback=LogLevels.INFO)
        # Verbosity 3 = DEBUG
        assert result == LogLevels.DEBUG

