"""
Integration tests for Rich features.

Tests end-to-end Rich functionality:
- Rich display methods (table, panel, rule, etc.)
- Context managers (progress, status, live)
- Task context for parallel execution
- Graceful degradation when Rich disabled
"""

import pytest
from unittest.mock import patch

from rich_logging import (
    Log,
    LogLevels,
    ConsoleHandlers,
    RichFeatureSettings,
)


class TestRichDisplayFeatures:
    """Integration tests for Rich display methods."""

    def test_table_displays_data(self):
        """Integration: table() displays tabular data."""
        logger = Log.create_logger(
            "test_app",
            log_level=LogLevels.INFO,
            console_handler_type=ConsoleHandlers.RICH,
            rich_features=RichFeatureSettings(enabled=True)
        )

        # Should not raise - first row is headers when show_header=True
        logger.table(
            [["Name", "Age"], ["Alice", "30"], ["Bob", "25"]],
            show_header=True
        )

    def test_panel_displays_message(self):
        """Integration: panel() displays message in panel."""
        logger = Log.create_logger(
            "test_app",
            log_level=LogLevels.INFO,
            console_handler_type=ConsoleHandlers.RICH,
            rich_features=RichFeatureSettings(enabled=True)
        )

        # Should not raise
        logger.panel("Important message", title="Alert")

    def test_rule_displays_separator(self):
        """Integration: rule() displays separator."""
        logger = Log.create_logger(
            "test_app",
            log_level=LogLevels.INFO,
            console_handler_type=ConsoleHandlers.RICH,
            rich_features=RichFeatureSettings(enabled=True)
        )

        # Should not raise
        logger.rule("Section Title")

    def test_syntax_displays_code(self):
        """Integration: syntax() displays syntax-highlighted code."""
        logger = Log.create_logger(
            "test_app",
            log_level=LogLevels.INFO,
            console_handler_type=ConsoleHandlers.RICH,
            rich_features=RichFeatureSettings(enabled=True)
        )

        # Should not raise
        logger.syntax("def hello(): pass", "python")

    def test_markdown_displays_formatted_text(self):
        """Integration: markdown() displays formatted markdown."""
        logger = Log.create_logger(
            "test_app",
            log_level=LogLevels.INFO,
            console_handler_type=ConsoleHandlers.RICH,
            rich_features=RichFeatureSettings(enabled=True)
        )

        # Should not raise
        logger.markdown("# Title\n\nParagraph")

    def test_json_displays_formatted_json(self):
        """Integration: json() displays formatted JSON."""
        logger = Log.create_logger(
            "test_app",
            log_level=LogLevels.INFO,
            console_handler_type=ConsoleHandlers.RICH,
            rich_features=RichFeatureSettings(enabled=True)
        )

        # Should not raise
        logger.json({"key": "value", "number": 42})


class TestRichContextManagers:
    """Integration tests for Rich context managers."""

    @patch('rich_logging.rich.rich_logger.console_manager')
    def test_progress_context_manager_workflow(self, mock_console_manager):
        """Integration: progress() context manager workflow."""
        from unittest.mock import MagicMock
        mock_console = MagicMock()
        mock_console.__enter__ = MagicMock(return_value=mock_console)
        mock_console.__exit__ = MagicMock(return_value=False)
        mock_console_manager.get_console.return_value = mock_console

        logger = Log.create_logger(
            "test_app",
            log_level=LogLevels.INFO,
            console_handler_type=ConsoleHandlers.RICH,
            rich_features=RichFeatureSettings(enabled=True)
        )

        # Should work as context manager
        with logger.progress("Processing", total=100) as progress:
            assert progress is not None

    def test_progress_fallback_when_disabled(self):
        """Integration: progress() returns dummy when Rich disabled."""
        logger = Log.create_logger(
            "test_app",
            log_level=LogLevels.INFO,
            rich_features=RichFeatureSettings(enabled=False)
        )

        # Should return dummy progress
        with logger.progress("Processing", total=100) as progress:
            # Dummy progress should have add_task method
            assert hasattr(progress, 'add_task')


class TestTaskContext:
    """Integration tests for task context."""

    def test_task_context_workflow(self):
        """Integration: Task context workflow."""
        logger = Log.create_logger("test_app", log_level=LogLevels.INFO)

        # Set task context
        logger.set_task_context("task1")

        # Clear task context
        logger.clear_task_context()

