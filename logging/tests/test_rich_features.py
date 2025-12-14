"""Tests for Rich features in the logging module."""

import rich_logging
import unittest
from unittest.mock import Mock, patch

from rich_logging.rich.rich_feature_settings import RichFeatureSettings
from rich_logging.rich.rich_logger import RichLogger


class TestRichFeatures(unittest.TestCase):
    """Test suite for Rich features in RichLogger."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_logger = Mock(spec=logging.Logger)
        self.mock_logger.name = "test_logger"
        self.rich_settings = RichFeatureSettings()
        self.rich_logger = RichLogger(self.mock_logger, self.rich_settings)

    @patch("logging.rich.rich_logger.RICH_AVAILABLE", True)
    @patch("logging.rich.rich_logger.console_manager")
    def test_tree_with_dict_data(self, mock_console_manager):
        """Test tree display with dictionary data."""
        mock_console = Mock()
        mock_console_manager.get_console.return_value = mock_console

        test_data = {
            "config/": {
                "nvim/": "Neovim configuration",
                "zsh/": "Zsh configuration",
            },
            "scripts/": {"install.sh": "Installation script"},
        }

        self.rich_logger.tree(test_data, title="Test Structure")

        # Verify console.print was called
        mock_console.print.assert_called_once()
        # Verify the tree was created with correct title
        args, kwargs = mock_console.print.call_args
        tree_obj = args[0]
        self.assertEqual(tree_obj.label, "Test Structure")

    @patch("logging.rich.rich_logger.RICH_AVAILABLE", False)
    def test_tree_fallback_when_rich_unavailable(self):
        """Test tree graceful fallback when Rich is not available."""
        test_data = {"config/": {"nvim/": "test"}}

        # Should not raise an exception
        self.rich_logger.tree(test_data)

    @patch("logging.rich.rich_logger.RICH_AVAILABLE", True)
    @patch("logging.rich.rich_logger.console_manager")
    def test_columns_display(self, mock_console_manager):
        """Test columns display functionality."""
        mock_console = Mock()
        mock_console_manager.get_console.return_value = mock_console

        self.rich_logger.columns("Column 1", "Column 2", "Column 3")

        mock_console.print.assert_called_once()
        args, kwargs = mock_console.print.call_args
        columns_obj = args[0]
        # Verify it's a Columns object with correct renderables
        self.assertEqual(len(columns_obj.renderables), 3)

    @patch("logging.rich.rich_logger.RICH_AVAILABLE", True)
    @patch("logging.rich.rich_logger.console_manager")
    def test_syntax_highlighting(self, mock_console_manager):
        """Test syntax highlighting functionality."""
        mock_console = Mock()
        mock_console_manager.get_console.return_value = mock_console

        code = 'print("Hello, World!")'
        self.rich_logger.syntax(code, lexer="python", title="Test Code")

        mock_console.print.assert_called_once()
        # Should wrap in panel when title is provided
        args, kwargs = mock_console.print.call_args
        panel_obj = args[0]
        self.assertEqual(panel_obj.title, "Test Code")

    @patch("logging.rich.rich_logger.RICH_AVAILABLE", True)
    @patch("logging.rich.rich_logger.console_manager")
    def test_markdown_rendering(self, mock_console_manager):
        """Test markdown rendering functionality."""
        mock_console = Mock()
        mock_console_manager.get_console.return_value = mock_console

        markdown_text = "# Test\n\nThis is **bold** text."
        self.rich_logger.markdown(markdown_text)

        mock_console.print.assert_called_once()

    @patch("logging.rich.rich_logger.RICH_AVAILABLE", True)
    @patch("logging.rich.rich_logger.console_manager")
    def test_json_display_with_dict(self, mock_console_manager):
        """Test JSON display with dictionary data."""
        mock_console = Mock()
        mock_console_manager.get_console.return_value = mock_console

        test_data = {"name": "test", "version": "1.0", "items": [1, 2, 3]}
        self.rich_logger.json(test_data, title="Test JSON")

        mock_console.print.assert_called_once()
        # Should wrap in panel when title is provided
        args, kwargs = mock_console.print.call_args
        panel_obj = args[0]
        self.assertEqual(panel_obj.title, "Test JSON")

    @patch("logging.rich.rich_logger.RICH_AVAILABLE", True)
    @patch("logging.rich.rich_logger.console_manager")
    def test_json_display_with_string(self, mock_console_manager):
        """Test JSON display with JSON string."""
        mock_console = Mock()
        mock_console_manager.get_console.return_value = mock_console

        json_string = '{"status": "complete", "errors": []}'
        self.rich_logger.json(json_string)

        mock_console.print.assert_called_once()

    @patch("logging.rich.rich_logger.RICH_AVAILABLE", True)
    @patch("logging.rich.rich_logger.console_manager")
    def test_bar_chart_display(self, mock_console_manager):
        """Test bar chart display functionality."""
        mock_console = Mock()
        mock_console_manager.get_console.return_value = mock_console

        test_data = {
            "Config Files": 15,
            "Scripts": 8,
            "Themes": 12,
            "Plugins": 25,
        }
        self.rich_logger.bar_chart(test_data, title="Test Chart")

        mock_console.print.assert_called_once()
        args, kwargs = mock_console.print.call_args
        table_obj = args[0]
        self.assertEqual(table_obj.title, "Test Chart")

    @patch("logging.rich.rich_logger.RICH_AVAILABLE", True)
    @patch("logging.rich.rich_logger.console_manager")
    def test_text_styling(self, mock_console_manager):
        """Test text styling functionality."""
        mock_console = Mock()
        mock_console_manager.get_console.return_value = mock_console

        self.rich_logger.text(
            "Test text", style="bold green", justify="center"
        )

        mock_console.print.assert_called_once()

    @patch("logging.rich.rich_logger.RICH_AVAILABLE", True)
    @patch("logging.rich.rich_logger.console_manager")
    def test_align_functionality(self, mock_console_manager):
        """Test content alignment functionality."""
        mock_console = Mock()
        mock_console_manager.get_console.return_value = mock_console

        self.rich_logger.align("Centered text", "center")

        mock_console.print.assert_called_once()

    def test_rich_feature_settings_validation(self):
        """Test RichFeatureSettings validation."""
        # Test valid settings
        RichFeatureSettings(
            json_indent=4, bar_chart_width=30, live_refresh_per_second=5
        )
        # Should not raise an exception

        # Test invalid settings
        with self.assertRaises(ValueError):
            RichFeatureSettings(json_indent=-1)

        with self.assertRaises(ValueError):
            RichFeatureSettings(bar_chart_width=0)

        with self.assertRaises(ValueError):
            RichFeatureSettings(live_refresh_per_second=-1)

        with self.assertRaises(ValueError):
            RichFeatureSettings(text_justify="invalid")

        with self.assertRaises(ValueError):
            RichFeatureSettings(text_overflow="invalid")

        with self.assertRaises(ValueError):
            RichFeatureSettings(live_vertical_overflow="invalid")

    def test_settings_defaults_used(self):
        """Test that settings defaults are properly used."""
        custom_settings = RichFeatureSettings(
            tree_guide_style="bold blue",
            syntax_theme="github-dark",
            json_indent=4,
        )
        rich_logger = RichLogger(self.mock_logger, custom_settings)

        # Verify settings are stored
        self.assertEqual(
            rich_logger._rich_settings.tree_guide_style, "bold blue"
        )
        self.assertEqual(
            rich_logger._rich_settings.syntax_theme, "github-dark"
        )
        self.assertEqual(rich_logger._rich_settings.json_indent, 4)


if __name__ == "__main__":
    unittest.main()
