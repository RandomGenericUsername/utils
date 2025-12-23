"""
Contract tests for RichLogger API.

Tests the public interface of RichLogger class, verifying:
- Standard logging method delegation
- Rich display methods (table, panel, rule, etc.)
- Context managers (progress, status, live)
- Task context methods
- Interactive methods (prompt, confirm)
- Graceful degradation when Rich is unavailable
"""

import logging as stdlib_logging
from unittest.mock import Mock, patch, MagicMock
import pytest

from rich_logging import (
    Log,
    LogLevels,
    ConsoleHandlers,
    RichLogger,
    RichFeatureSettings,
)


class TestRichLoggerStandardLogging:
    """Contract tests for standard logging method delegation."""

    def test_info_delegates_to_stdlib_logger(self):
        """Contract: info() delegates to stdlib logger."""
        logger = Log.create_logger("test", log_level=LogLevels.INFO)
        
        with patch.object(logger._logger, 'info') as mock_info:
            logger.info("test message")
            mock_info.assert_called_once_with("test message")

    def test_debug_delegates_to_stdlib_logger(self):
        """Contract: debug() delegates to stdlib logger."""
        logger = Log.create_logger("test", log_level=LogLevels.DEBUG)
        
        with patch.object(logger._logger, 'debug') as mock_debug:
            logger.debug("debug message")
            mock_debug.assert_called_once_with("debug message")

    def test_warning_delegates_to_stdlib_logger(self):
        """Contract: warning() delegates to stdlib logger."""
        logger = Log.create_logger("test", log_level=LogLevels.INFO)
        
        with patch.object(logger._logger, 'warning') as mock_warning:
            logger.warning("warning message")
            mock_warning.assert_called_once_with("warning message")

    def test_error_delegates_to_stdlib_logger(self):
        """Contract: error() delegates to stdlib logger."""
        logger = Log.create_logger("test", log_level=LogLevels.INFO)
        
        with patch.object(logger._logger, 'error') as mock_error:
            logger.error("error message")
            mock_error.assert_called_once_with("error message")

    def test_critical_delegates_to_stdlib_logger(self):
        """Contract: critical() delegates to stdlib logger."""
        logger = Log.create_logger("test", log_level=LogLevels.INFO)
        
        with patch.object(logger._logger, 'critical') as mock_critical:
            logger.critical("critical message")
            mock_critical.assert_called_once_with("critical message")

    def test_exception_delegates_to_stdlib_logger(self):
        """Contract: exception() delegates to stdlib logger."""
        logger = Log.create_logger("test", log_level=LogLevels.INFO)
        
        with patch.object(logger._logger, 'exception') as mock_exception:
            logger.exception("exception message")
            mock_exception.assert_called_once_with("exception message")

    def test_log_delegates_to_stdlib_logger(self):
        """Contract: log() delegates to stdlib logger."""
        logger = Log.create_logger("test", log_level=LogLevels.INFO)
        
        with patch.object(logger._logger, 'log') as mock_log:
            logger.log(stdlib_logging.INFO, "log message")
            mock_log.assert_called_once_with(stdlib_logging.INFO, "log message")

    def test_setLevel_delegates_to_stdlib_logger(self):
        """Contract: setLevel() delegates to stdlib logger."""
        logger = Log.create_logger("test", log_level=LogLevels.INFO)
        
        with patch.object(logger._logger, 'setLevel') as mock_setLevel:
            logger.setLevel(stdlib_logging.DEBUG)
            mock_setLevel.assert_called_once_with(stdlib_logging.DEBUG)

    def test_addHandler_delegates_to_stdlib_logger(self):
        """Contract: addHandler() delegates to stdlib logger."""
        logger = Log.create_logger("test", log_level=LogLevels.INFO)
        handler = stdlib_logging.StreamHandler()
        
        with patch.object(logger._logger, 'addHandler') as mock_addHandler:
            logger.addHandler(handler)
            mock_addHandler.assert_called_once_with(handler)

    def test_removeHandler_delegates_to_stdlib_logger(self):
        """Contract: removeHandler() delegates to stdlib logger."""
        logger = Log.create_logger("test", log_level=LogLevels.INFO)
        handler = stdlib_logging.StreamHandler()
        
        with patch.object(logger._logger, 'removeHandler') as mock_removeHandler:
            logger.removeHandler(handler)
            mock_removeHandler.assert_called_once_with(handler)


class TestRichLoggerProperties:
    """Contract tests for RichLogger properties."""

    def test_name_property_returns_logger_name(self):
        """Contract: name property returns logger name."""
        logger = Log.create_logger("test_logger", log_level=LogLevels.INFO)
        
        assert logger.name == "test_logger"

    def test_name_property_for_root_logger(self):
        """Contract: name property returns 'root' for root logger."""
        logger = Log.create_logger(None, log_level=LogLevels.INFO)
        
        assert logger.name == "root"

    def test_logger_has_rich_settings(self):
        """Contract: RichLogger has _rich_settings attribute."""
        logger = Log.create_logger("test", log_level=LogLevels.INFO)
        
        assert hasattr(logger, '_rich_settings')
        assert isinstance(logger._rich_settings, RichFeatureSettings)

    def test_logger_has_wrapped_logger(self):
        """Contract: RichLogger has _logger attribute."""
        logger = Log.create_logger("test", log_level=LogLevels.INFO)

        assert hasattr(logger, '_logger')
        assert isinstance(logger._logger, stdlib_logging.Logger)


class TestRichLoggerDisplayMethods:
    """Contract tests for Rich display methods."""

    @patch('rich_logging.rich.rich_logger.console_manager')
    def test_table_with_list_data(self, mock_console_manager):
        """Contract: table() accepts list of rows."""
        mock_console = Mock()
        mock_console_manager.get_console.return_value = mock_console

        logger = Log.create_logger(
            "test",
            log_level=LogLevels.INFO,
            console_handler_type=ConsoleHandlers.RICH,
            rich_features=RichFeatureSettings(enabled=True)
        )

        data = [["Alice", "30"], ["Bob", "25"]]
        logger.table(data)

        # Should call console.print with a Table
        assert mock_console.print.called

    @patch('rich_logging.rich.rich_logger.console_manager')
    def test_table_with_dict_data(self, mock_console_manager):
        """Contract: table() accepts dict of columns."""
        mock_console = Mock()
        mock_console_manager.get_console.return_value = mock_console

        logger = Log.create_logger(
            "test",
            log_level=LogLevels.INFO,
            console_handler_type=ConsoleHandlers.RICH,
            rich_features=RichFeatureSettings(enabled=True)
        )

        data = {"Name": ["Alice", "Bob"], "Age": ["30", "25"]}
        logger.table(data)

        assert mock_console.print.called

    @patch('rich_logging.rich.rich_logger.console_manager')
    def test_panel_displays_message(self, mock_console_manager):
        """Contract: panel() displays a panel with message."""
        mock_console = Mock()
        mock_console_manager.get_console.return_value = mock_console

        logger = Log.create_logger(
            "test",
            log_level=LogLevels.INFO,
            console_handler_type=ConsoleHandlers.RICH,
            rich_features=RichFeatureSettings(enabled=True)
        )

        logger.panel("Test message", title="Test")

        assert mock_console.print.called

    @patch('rich_logging.rich.rich_logger.console_manager')
    def test_rule_displays_separator(self, mock_console_manager):
        """Contract: rule() displays a horizontal rule."""
        mock_console = Mock()
        mock_console_manager.get_console.return_value = mock_console

        logger = Log.create_logger(
            "test",
            log_level=LogLevels.INFO,
            console_handler_type=ConsoleHandlers.RICH,
            rich_features=RichFeatureSettings(enabled=True)
        )

        logger.rule("Section Title")

        assert mock_console.print.called

    @patch('rich_logging.rich.rich_logger.console_manager')
    def test_tree_with_dict_data(self, mock_console_manager):
        """Contract: tree() accepts dict data."""
        mock_console = Mock()
        mock_console_manager.get_console.return_value = mock_console

        logger = Log.create_logger(
            "test",
            log_level=LogLevels.INFO,
            console_handler_type=ConsoleHandlers.RICH,
            rich_features=RichFeatureSettings(enabled=True)
        )

        data = {"folder": {"file1.txt": "content", "file2.txt": "content"}}
        logger.tree(data, title="Files")

        assert mock_console.print.called

    @patch('rich_logging.rich.rich_logger.console_manager')
    def test_syntax_displays_code(self, mock_console_manager):
        """Contract: syntax() displays syntax-highlighted code."""
        mock_console = Mock()
        mock_console_manager.get_console.return_value = mock_console

        logger = Log.create_logger(
            "test",
            log_level=LogLevels.INFO,
            console_handler_type=ConsoleHandlers.RICH,
            rich_features=RichFeatureSettings(enabled=True)
        )

        logger.syntax("print('hello')", "python")

        assert mock_console.print.called

    @patch('rich_logging.rich.rich_logger.console_manager')
    def test_markdown_displays_formatted_text(self, mock_console_manager):
        """Contract: markdown() displays markdown-formatted text."""
        mock_console = Mock()
        mock_console_manager.get_console.return_value = mock_console

        logger = Log.create_logger(
            "test",
            log_level=LogLevels.INFO,
            console_handler_type=ConsoleHandlers.RICH,
            rich_features=RichFeatureSettings(enabled=True)
        )

        logger.markdown("# Title\n\nParagraph")

        assert mock_console.print.called

    @patch('rich_logging.rich.rich_logger.console_manager')
    def test_json_displays_formatted_json(self, mock_console_manager):
        """Contract: json() displays formatted JSON."""
        mock_console = Mock()
        mock_console_manager.get_console.return_value = mock_console

        logger = Log.create_logger(
            "test",
            log_level=LogLevels.INFO,
            console_handler_type=ConsoleHandlers.RICH,
            rich_features=RichFeatureSettings(enabled=True)
        )

        logger.json({"key": "value"})

        assert mock_console.print.called


class TestRichLoggerContextManagers:
    """Contract tests for Rich context managers."""

    @patch('rich_logging.rich.rich_logger.console_manager')
    def test_progress_context_manager(self, mock_console_manager):
        """Contract: progress() returns a context manager."""
        mock_console = MagicMock()
        mock_console.__enter__ = Mock(return_value=mock_console)
        mock_console.__exit__ = Mock(return_value=False)
        mock_console_manager.get_console.return_value = mock_console

        logger = Log.create_logger(
            "test",
            log_level=LogLevels.INFO,
            console_handler_type=ConsoleHandlers.RICH,
            rich_features=RichFeatureSettings(enabled=True)
        )

        with logger.progress("Processing", total=100) as progress:
            # Should return a progress object (or dummy)
            assert progress is not None

    @patch('rich_logging.rich.rich_logger.console_manager')
    def test_status_context_manager(self, mock_console_manager):
        """Contract: status() returns a context manager."""
        mock_console = MagicMock()
        mock_console.__enter__ = Mock(return_value=mock_console)
        mock_console.__exit__ = Mock(return_value=False)
        mock_console_manager.get_console.return_value = mock_console

        logger = Log.create_logger(
            "test",
            log_level=LogLevels.INFO,
            console_handler_type=ConsoleHandlers.RICH,
            rich_features=RichFeatureSettings(enabled=True)
        )

        with logger.status("Loading...") as status:
            # Should return a status object (or dummy)
            assert status is not None

    @patch('rich_logging.rich.rich_logger.console_manager')
    def test_live_context_manager(self, mock_console_manager):
        """Contract: live() returns a context manager."""
        mock_console = MagicMock()
        mock_console.__enter__ = Mock(return_value=mock_console)
        mock_console.__exit__ = Mock(return_value=False)
        mock_console_manager.get_console.return_value = mock_console

        logger = Log.create_logger(
            "test",
            log_level=LogLevels.INFO,
            console_handler_type=ConsoleHandlers.RICH,
            rich_features=RichFeatureSettings(enabled=True)
        )

        from rich.table import Table
        table = Table()

        with logger.live(table):
            # Should return a live object (or None)
            pass  # live can be None if Rich unavailable

    def test_progress_fallback_when_rich_disabled(self):
        """Contract: progress() returns dummy when Rich disabled."""
        logger = Log.create_logger(
            "test",
            log_level=LogLevels.INFO,
            rich_features=RichFeatureSettings(enabled=False)
        )

        with logger.progress("Processing") as progress:
            # Should return dummy progress
            assert progress is not None

    def test_status_fallback_when_rich_disabled(self):
        """Contract: status() returns dummy when Rich disabled."""
        logger = Log.create_logger(
            "test",
            log_level=LogLevels.INFO,
            rich_features=RichFeatureSettings(enabled=False)
        )

        with logger.status("Loading...") as status:
            # Should return dummy status
            assert status is not None


class TestRichLoggerTaskContext:
    """Contract tests for task context methods."""

    @patch('rich_logging.rich.rich_logger.LogContext')
    def test_set_task_context(self, mock_log_context):
        """Contract: set_task_context() sets thread-local context."""
        logger = Log.create_logger("test", log_level=LogLevels.INFO)

        logger.set_task_context("task1", "Task One")

        mock_log_context.set_task_context.assert_called_once_with(
            "task1", "Task One"
        )

    @patch('rich_logging.rich.rich_logger.LogContext')
    def test_clear_task_context(self, mock_log_context):
        """Contract: clear_task_context() clears thread-local context."""
        logger = Log.create_logger("test", log_level=LogLevels.INFO)

        logger.clear_task_context()

        mock_log_context.clear_task_context.assert_called_once()

    @patch('rich_logging.rich.rich_logger.LogContext')
    def test_task_context_manager(self, mock_log_context):
        """Contract: task_context() is a context manager."""
        logger = Log.create_logger("test", log_level=LogLevels.INFO)

        with logger.task_context("task1", "Task One"):
            # Context should be set
            mock_log_context.set_task_context.assert_called_once_with(
                "task1", "Task One"
            )

        # Context should be cleared after exiting
        mock_log_context.clear_task_context.assert_called_once()

    @patch('rich_logging.rich.rich_logger.LogContext')
    def test_task_context_clears_on_exception(self, mock_log_context):
        """Contract: task_context() clears context even on exception."""
        logger = Log.create_logger("test", log_level=LogLevels.INFO)

        try:
            with logger.task_context("task1"):
                raise ValueError("Test error")
        except ValueError:
            pass

        # Context should still be cleared
        mock_log_context.clear_task_context.assert_called_once()


class TestRichLoggerInteractiveMethods:
    """Contract tests for interactive methods."""

    @patch('rich_logging.rich.rich_logger.Prompt')
    @patch('rich_logging.rich.rich_logger.console_manager')
    def test_prompt_returns_user_input(self, mock_console_manager, mock_prompt):
        """Contract: prompt() returns user input."""
        mock_console = Mock()
        mock_console_manager.get_console.return_value = mock_console
        mock_prompt.ask.return_value = "user input"

        logger = Log.create_logger(
            "test",
            log_level=LogLevels.INFO,
            console_handler_type=ConsoleHandlers.RICH,
            rich_features=RichFeatureSettings(enabled=True)
        )

        result = logger.prompt("Enter value")

        assert result == "user input"

    @patch('rich_logging.rich.rich_logger.Confirm')
    @patch('rich_logging.rich.rich_logger.console_manager')
    def test_confirm_returns_boolean(self, mock_console_manager, mock_confirm):
        """Contract: confirm() returns boolean."""
        mock_console = Mock()
        mock_console_manager.get_console.return_value = mock_console
        mock_confirm.ask.return_value = True

        logger = Log.create_logger(
            "test",
            log_level=LogLevels.INFO,
            console_handler_type=ConsoleHandlers.RICH,
            rich_features=RichFeatureSettings(enabled=True)
        )

        result = logger.confirm("Continue?")

        assert result is True

    def test_prompt_returns_default_when_rich_disabled(self):
        """Contract: prompt() returns default when Rich disabled."""
        logger = Log.create_logger(
            "test",
            log_level=LogLevels.INFO,
            rich_features=RichFeatureSettings(enabled=False)
        )

        result = logger.prompt("Enter value", default="default_value")

        assert result == "default_value"

    def test_confirm_returns_default_when_rich_disabled(self):
        """Contract: confirm() returns default when Rich disabled."""
        logger = Log.create_logger(
            "test",
            log_level=LogLevels.INFO,
            rich_features=RichFeatureSettings(enabled=False)
        )

        result = logger.confirm("Continue?", default=False)

        assert result is False


class TestRichLoggerGracefulDegradation:
    """Contract tests for graceful degradation when Rich unavailable."""

    def test_table_does_not_raise_when_rich_disabled(self):
        """Contract: table() does not raise when Rich disabled."""
        logger = Log.create_logger(
            "test",
            log_level=LogLevels.INFO,
            rich_features=RichFeatureSettings(enabled=False)
        )

        # Should not raise
        logger.table([["data"]])

    def test_panel_does_not_raise_when_rich_disabled(self):
        """Contract: panel() does not raise when Rich disabled."""
        logger = Log.create_logger(
            "test",
            log_level=LogLevels.INFO,
            rich_features=RichFeatureSettings(enabled=False)
        )

        # Should not raise
        logger.panel("message")

    def test_rule_does_not_raise_when_rich_disabled(self):
        """Contract: rule() does not raise when Rich disabled."""
        logger = Log.create_logger(
            "test",
            log_level=LogLevels.INFO,
            rich_features=RichFeatureSettings(enabled=False)
        )

        # Should not raise
        logger.rule("title")

    def test_tree_does_not_raise_when_rich_disabled(self):
        """Contract: tree() does not raise when Rich disabled."""
        logger = Log.create_logger(
            "test",
            log_level=LogLevels.INFO,
            rich_features=RichFeatureSettings(enabled=False)
        )

        # Should not raise
        logger.tree({"data": "value"})

    def test_syntax_does_not_raise_when_rich_disabled(self):
        """Contract: syntax() does not raise when Rich disabled."""
        logger = Log.create_logger(
            "test",
            log_level=LogLevels.INFO,
            rich_features=RichFeatureSettings(enabled=False)
        )

        # Should not raise
        logger.syntax("code", "python")

    def test_markdown_does_not_raise_when_rich_disabled(self):
        """Contract: markdown() does not raise when Rich disabled."""
        logger = Log.create_logger(
            "test",
            log_level=LogLevels.INFO,
            rich_features=RichFeatureSettings(enabled=False)
        )

        # Should not raise
        logger.markdown("# Title")

    def test_json_does_not_raise_when_rich_disabled(self):
        """Contract: json() does not raise when Rich disabled."""
        logger = Log.create_logger(
            "test",
            log_level=LogLevels.INFO,
            rich_features=RichFeatureSettings(enabled=False)
        )

        # Should not raise
        logger.json({"key": "value"})

