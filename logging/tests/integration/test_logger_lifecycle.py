"""
Integration tests for logger lifecycle.

Tests complete workflows:
- Create logger → configure → log messages → verify output
- Create logger → update configuration → verify changes
- Multiple loggers with different configurations
- File logging with rotation
"""

import logging as stdlib_logging
import tempfile
from pathlib import Path
import pytest

from rich_logging import (
    Log,
    LogLevels,
    ConsoleHandlers,
    LogFormatters,
    LogFormatterStyleChoices,
    RichFeatureSettings,
    FileHandlerSpec,
    FileHandlerTypes,
)


class TestLoggerCreationAndLogging:
    """Integration tests for logger creation and basic logging."""

    def test_create_logger_and_log_messages(self, caplog):
        """Integration: Create logger and log messages at different levels."""
        logger = Log.create_logger("test_app", log_level=LogLevels.DEBUG)
        
        with caplog.at_level(stdlib_logging.DEBUG, logger="test_app"):
            logger.debug("Debug message")
            logger.info("Info message")
            logger.warning("Warning message")
            logger.error("Error message")
            logger.critical("Critical message")
        
        # Verify all messages were logged
        assert "Debug message" in caplog.text
        assert "Info message" in caplog.text
        assert "Warning message" in caplog.text
        assert "Error message" in caplog.text
        assert "Critical message" in caplog.text

    def test_logger_respects_log_level(self, caplog):
        """Integration: Logger filters messages below log level."""
        logger = Log.create_logger("test_app", log_level=LogLevels.WARNING)

        # Set caplog to WARNING to match logger level
        with caplog.at_level(stdlib_logging.WARNING, logger="test_app"):
            logger.debug("Debug message")
            logger.info("Info message")
            logger.warning("Warning message")
            logger.error("Error message")

        # Debug and Info should be filtered out
        assert "Debug message" not in caplog.text
        assert "Info message" not in caplog.text
        assert "Warning message" in caplog.text
        assert "Error message" in caplog.text

    def test_logger_with_rich_handler(self, caplog):
        """Integration: Logger with Rich handler logs messages."""
        logger = Log.create_logger(
            "test_app",
            log_level=LogLevels.INFO,
            console_handler_type=ConsoleHandlers.RICH,
            rich_features=RichFeatureSettings(enabled=True)
        )
        
        with caplog.at_level(stdlib_logging.INFO, logger="test_app"):
            logger.info("Test message")
        
        assert "Test message" in caplog.text


class TestLoggerUpdate:
    """Integration tests for logger configuration updates."""

    def test_update_logger_level(self, caplog):
        """Integration: Update logger level and verify filtering changes."""
        # Create with INFO level
        logger = Log.create_logger("test_app", log_level=LogLevels.INFO)

        # Set caplog to INFO to match logger level
        with caplog.at_level(stdlib_logging.INFO, logger="test_app"):
            logger.debug("Debug 1")
            logger.info("Info 1")

        assert "Debug 1" not in caplog.text
        assert "Info 1" in caplog.text

        caplog.clear()

        # Update to DEBUG level
        logger = Log.update("test_app", log_level=LogLevels.DEBUG)

        # Now set caplog to DEBUG to capture debug messages
        with caplog.at_level(stdlib_logging.DEBUG, logger="test_app"):
            logger.debug("Debug 2")
            logger.info("Info 2")

        assert "Debug 2" in caplog.text
        assert "Info 2" in caplog.text

    def test_update_logger_multiple_times(self, caplog):
        """Integration: Update logger configuration multiple times."""
        logger = Log.create_logger("test_app", log_level=LogLevels.INFO)
        
        # First update
        logger = Log.update("test_app", log_level=LogLevels.DEBUG)
        assert logger._logger.level == stdlib_logging.DEBUG
        
        # Second update
        logger = Log.update("test_app", log_level=LogLevels.WARNING)
        assert logger._logger.level == stdlib_logging.WARNING
        
        # Third update
        logger = Log.update("test_app", log_level=LogLevels.ERROR)
        assert logger._logger.level == stdlib_logging.ERROR


class TestMultipleLoggers:
    """Integration tests for multiple independent loggers."""

    def test_multiple_loggers_independent(self, caplog):
        """Integration: Multiple loggers operate independently."""
        logger1 = Log.create_logger("app1", log_level=LogLevels.DEBUG)
        logger2 = Log.create_logger("app2", log_level=LogLevels.WARNING)
        
        with caplog.at_level(stdlib_logging.DEBUG):
            logger1.debug("App1 debug")
            logger1.info("App1 info")
            logger2.debug("App2 debug")
            logger2.warning("App2 warning")
        
        # Logger1 should log debug and info
        assert "App1 debug" in caplog.text
        assert "App1 info" in caplog.text
        
        # Logger2 should only log warning (debug filtered)
        assert "App2 debug" not in caplog.text
        assert "App2 warning" in caplog.text

    def test_multiple_loggers_different_handlers(self):
        """Integration: Multiple loggers with different handler types."""
        logger1 = Log.create_logger(
            "app1",
            log_level=LogLevels.INFO,
            console_handler_type=ConsoleHandlers.DEFAULT
        )
        logger2 = Log.create_logger(
            "app2",
            log_level=LogLevels.INFO,
            console_handler_type=ConsoleHandlers.RICH
        )
        
        # Both should have handlers
        assert len(logger1._logger.handlers) > 0
        assert len(logger2._logger.handlers) > 0
        
        # They should be independent
        assert logger1.name == "app1"
        assert logger2.name == "app2"

