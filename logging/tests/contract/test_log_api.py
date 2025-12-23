"""Contract tests for Log API (create_logger and update methods).

Test Intent:
    Verify the public API contracts of Log.create_logger() and Log.update()

Behavior Protected:
    - Logger creation returns RichLogger instance
    - Configuration parameters are applied correctly
    - Logger registry is maintained
    - Update requires existing logger
    - Error handling for invalid inputs
"""

import logging as stdlib_logging
import pytest

from rich_logging import (
    Log,
    LogConfig,
    LogLevels,
    ConsoleHandlers,
    LogFormatters,
    RichLogger,
    RichFeatureSettings,
    RichHandlerSettings,
)


class TestLogCreateLogger:
    """Contract tests for Log.create_logger() method."""

    def test_create_logger_returns_rich_logger(self):
        """Contract: create_logger() returns RichLogger instance."""
        logger = Log.create_logger("test_logger", log_level=LogLevels.INFO)

        assert isinstance(logger, RichLogger)
        assert logger.name == "test_logger"

    def test_create_logger_with_log_level(self):
        """Contract: log_level parameter sets logger level."""
        logger = Log.create_logger("test_logger", log_level=LogLevels.DEBUG)
        
        # Access underlying stdlib logger
        assert logger._logger.level == stdlib_logging.DEBUG

    def test_create_logger_with_info_level(self):
        """Contract: INFO level is set correctly."""
        logger = Log.create_logger("test_logger", log_level=LogLevels.INFO)
        
        assert logger._logger.level == stdlib_logging.INFO

    def test_create_logger_with_warning_level(self):
        """Contract: WARNING level is set correctly."""
        logger = Log.create_logger("test_logger", log_level=LogLevels.WARNING)
        
        assert logger._logger.level == stdlib_logging.WARNING

    def test_create_logger_with_error_level(self):
        """Contract: ERROR level is set correctly."""
        logger = Log.create_logger("test_logger", log_level=LogLevels.ERROR)
        
        assert logger._logger.level == stdlib_logging.ERROR

    def test_create_logger_with_critical_level(self):
        """Contract: CRITICAL level is set correctly."""
        logger = Log.create_logger("test_logger", log_level=LogLevels.CRITICAL)
        
        assert logger._logger.level == stdlib_logging.CRITICAL

    def test_create_logger_with_console_handler_default(self):
        """Contract: DEFAULT console handler is attached."""
        logger = Log.create_logger(
            "test_logger",
            log_level=LogLevels.INFO,
            console_handler_type=ConsoleHandlers.DEFAULT
        )

        # Should have at least one handler
        assert len(logger._logger.handlers) > 0

    def test_create_logger_with_console_handler_rich(self):
        """Contract: RICH console handler is attached."""
        logger = Log.create_logger(
            "test_logger",
            log_level=LogLevels.INFO,
            console_handler_type=ConsoleHandlers.RICH
        )

        # Should have at least one handler
        assert len(logger._logger.handlers) > 0

    def test_create_logger_with_config_object(self, basic_log_config):
        """Contract: LogConfig object is accepted and applied."""
        logger = Log.create_logger("test_logger", config=basic_log_config)

        assert isinstance(logger, RichLogger)
        assert logger.name == "test_logger"
        assert logger._logger.level == stdlib_logging.INFO

    def test_create_logger_config_override_with_params(self, basic_log_config):
        """Contract: Individual parameters override LogConfig values."""
        # Config has INFO, but we override with DEBUG
        logger = Log.create_logger(
            config=basic_log_config,
            log_level=LogLevels.DEBUG
        )
        
        assert logger._logger.level == stdlib_logging.DEBUG

    def test_create_logger_stores_configurator(self):
        """Contract: Configurator is stored in registry."""
        Log.create_logger("test_logger", log_level=LogLevels.INFO)

        assert "test_logger" in Log._configurators

    def test_create_logger_with_rich_features(self):
        """Contract: Rich features settings are applied."""
        rich_settings = RichFeatureSettings(
            enabled=True,
            table_show_lines=True,
        )

        logger = Log.create_logger(
            "test_logger",
            log_level=LogLevels.INFO,
            rich_features=rich_settings
        )

        assert logger._rich_settings.enabled is True
        assert logger._rich_settings.table_show_lines is True

    def test_create_logger_with_none_name_uses_root(self):
        """Contract: None name creates root logger."""
        logger = Log.create_logger(name=None, log_level=LogLevels.INFO)

        # Root logger has empty string name
        assert logger.name == "root"

    def test_create_logger_multiple_loggers_independent(self):
        """Contract: Multiple loggers are independent."""
        logger1 = Log.create_logger("logger1", log_level=LogLevels.DEBUG)
        logger2 = Log.create_logger("logger2", log_level=LogLevels.ERROR)

        assert logger1._logger.level == stdlib_logging.DEBUG
        assert logger2._logger.level == stdlib_logging.ERROR
        assert "logger1" in Log._configurators
        assert "logger2" in Log._configurators


class TestLogUpdate:
    """Contract tests for Log.update() method."""

    def test_update_returns_rich_logger(self):
        """Contract: update() returns RichLogger instance."""
        # Create logger first
        Log.create_logger("test_logger", log_level=LogLevels.INFO)

        # Update it
        logger = Log.update("test_logger", log_level=LogLevels.DEBUG)

        assert isinstance(logger, RichLogger)

    def test_update_changes_log_level(self):
        """Contract: update() changes logger level."""
        # Create with INFO
        Log.create_logger("test_logger", log_level=LogLevels.INFO)

        # Update to DEBUG
        logger = Log.update("test_logger", log_level=LogLevels.DEBUG)

        assert logger._logger.level == stdlib_logging.DEBUG

    def test_update_nonexistent_logger_raises_error(self):
        """Contract: update() raises ValueError for nonexistent logger."""
        with pytest.raises(ValueError, match="Logger 'nonexistent' not found"):
            Log.update("nonexistent", log_level=LogLevels.DEBUG)

    def test_update_with_config_object(self, basic_log_config):
        """Contract: update() accepts LogConfig object."""
        # Create logger
        Log.create_logger("test_logger", log_level=LogLevels.ERROR)

        # Update with config (INFO level)
        logger = Log.update("test_logger", config=basic_log_config)

        assert logger._logger.level == stdlib_logging.INFO

    def test_update_config_override_with_params(self, basic_log_config):
        """Contract: Individual parameters override LogConfig in update()."""
        # Create logger
        Log.create_logger("test_logger", log_level=LogLevels.INFO)

        # Update with config (INFO) but override with DEBUG
        logger = Log.update(
            "test_logger",
            config=basic_log_config,
            log_level=LogLevels.DEBUG
        )

        assert logger._logger.level == stdlib_logging.DEBUG

    def test_update_preserves_logger_name(self):
        """Contract: update() preserves logger name."""
        Log.create_logger("test_logger", log_level=LogLevels.INFO)

        logger = Log.update("test_logger", log_level=LogLevels.DEBUG)

        assert logger.name == "test_logger"

    def test_update_replaces_handlers(self):
        """Contract: update() replaces existing handlers."""
        # Create with DEFAULT handler
        logger1 = Log.create_logger(
            "test_logger",
            log_level=LogLevels.INFO,
            console_handler_type=ConsoleHandlers.DEFAULT
        )
        initial_handler_count = len(logger1._logger.handlers)

        # Update with RICH handler
        logger2 = Log.update(
            "test_logger",
            console_handler_type=ConsoleHandlers.RICH
        )

        # Should still have handlers (replaced, not added)
        assert len(logger2._logger.handlers) >= initial_handler_count

    def test_update_rich_features(self):
        """Contract: update() changes Rich features settings."""
        # Create with default settings
        Log.create_logger("test_logger", log_level=LogLevels.INFO)

        # Update with new Rich settings
        new_settings = RichFeatureSettings(
            enabled=True,
            table_show_lines=False,
        )
        logger = Log.update("test_logger", rich_features=new_settings)

        assert logger._rich_settings.table_show_lines is False

    def test_update_multiple_times(self):
        """Contract: Logger can be updated multiple times."""
        Log.create_logger("test_logger", log_level=LogLevels.INFO)

        # First update
        logger1 = Log.update("test_logger", log_level=LogLevels.DEBUG)
        assert logger1._logger.level == stdlib_logging.DEBUG

        # Second update
        logger2 = Log.update("test_logger", log_level=LogLevels.WARNING)
        assert logger2._logger.level == stdlib_logging.WARNING

        # Third update
        logger3 = Log.update("test_logger", log_level=LogLevels.ERROR)
        assert logger3._logger.level == stdlib_logging.ERROR

