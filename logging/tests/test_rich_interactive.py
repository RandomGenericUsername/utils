"""Tests for Rich interactive features (prompts, live updates)."""

import rich_logging
import unittest
from unittest.mock import Mock, patch

from rich_logging.rich.rich_feature_settings import RichFeatureSettings
from rich_logging.rich.rich_logger import RichLogger


class TestRichInteractiveFeatures(unittest.TestCase):
    """Test suite for Rich interactive features."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_logger = Mock(spec=logging.Logger)
        self.mock_logger.name = "test_logger"
        self.rich_settings = RichFeatureSettings()
        self.rich_logger = RichLogger(self.mock_logger, self.rich_settings)

    @patch("logging.rich.rich_logger.RICH_AVAILABLE", True)
    @patch("logging.rich.rich_logger.console_manager")
    @patch("logging.rich.rich_logger.Prompt")
    def test_prompt_with_choices(
        self, mock_prompt_class, mock_console_manager
    ):
        """Test prompt functionality with choices."""
        mock_console = Mock()
        mock_console_manager.get_console.return_value = mock_console
        mock_prompt_class.ask.return_value = "symlink"

        result = self.rich_logger.prompt(
            "Choose installation type",
            choices=["symlink", "copy", "template"],
            default="symlink",
        )

        self.assertEqual(result, "symlink")
        mock_prompt_class.ask.assert_called_once_with(
            "Choose installation type",
            choices=["symlink", "copy", "template"],
            default="symlink",
            show_default=True,  # From settings
            show_choices=True,  # From settings
            console=mock_console,
        )

    @patch("logging.rich.rich_logger.RICH_AVAILABLE", True)
    @patch("logging.rich.rich_logger.console_manager")
    @patch("logging.rich.rich_logger.Prompt")
    def test_prompt_free_text(self, mock_prompt_class, mock_console_manager):
        """Test prompt functionality with free text input."""
        mock_console = Mock()
        mock_console_manager.get_console.return_value = mock_console
        mock_prompt_class.ask.return_value = "test_user"

        result = self.rich_logger.prompt("Enter your name", default="user")

        self.assertEqual(result, "test_user")
        mock_prompt_class.ask.assert_called_once_with(
            "Enter your name",
            default="user",
            show_default=True,
            console=mock_console,
        )

    @patch("logging.rich.rich_logger.RICH_AVAILABLE", False)
    def test_prompt_fallback_when_rich_unavailable(self):
        """Test prompt fallback when Rich is not available."""
        result = self.rich_logger.prompt("Test question", default="fallback")
        self.assertEqual(result, "fallback")

    @patch("logging.rich.rich_logger.RICH_AVAILABLE", True)
    @patch("logging.rich.rich_logger.console_manager")
    @patch("logging.rich.rich_logger.Confirm")
    def test_confirm_functionality(
        self, mock_confirm_class, mock_console_manager
    ):
        """Test confirm functionality."""
        mock_console = Mock()
        mock_console_manager.get_console.return_value = mock_console
        mock_confirm_class.ask.return_value = True

        result = self.rich_logger.confirm(
            "Do you want to continue?", default=False
        )

        self.assertTrue(result)
        mock_confirm_class.ask.assert_called_once_with(
            "Do you want to continue?", default=False, console=mock_console
        )

    @patch("logging.rich.rich_logger.RICH_AVAILABLE", False)
    def test_confirm_fallback_when_rich_unavailable(self):
        """Test confirm fallback when Rich is not available."""
        result = self.rich_logger.confirm("Test question", default=True)
        self.assertTrue(result)

    @patch("logging.rich.rich_logger.RICH_AVAILABLE", True)
    @patch("logging.rich.rich_logger.console_manager")
    @patch("logging.rich.rich_logger.Live")
    def test_live_context_manager(self, mock_live_class, mock_console_manager):
        """Test live updates context manager."""
        mock_console = Mock()
        mock_console_manager.get_console.return_value = mock_console

        # Create a mock Live instance
        mock_live_instance = Mock()
        mock_live_class.return_value.__enter__ = Mock(
            return_value=mock_live_instance
        )
        mock_live_class.return_value.__exit__ = Mock(return_value=None)

        test_renderable = "Test content"

        with self.rich_logger.live(
            test_renderable, refresh_per_second=2
        ) as live:
            self.assertEqual(live, mock_live_instance)

        # Verify Live was created with correct parameters
        mock_live_class.assert_called_once_with(
            test_renderable,
            console=mock_console,
            refresh_per_second=2,
            vertical_overflow="ellipsis",  # From settings
            auto_refresh=True,  # From settings
        )

    @patch("logging.rich.rich_logger.RICH_AVAILABLE", False)
    def test_live_fallback_when_rich_unavailable(self):
        """Test live updates fallback when Rich is not available."""
        with self.rich_logger.live("test") as live:
            self.assertIsNone(live)

    @patch("logging.rich.rich_logger.RICH_AVAILABLE", True)
    @patch("logging.rich.rich_logger.console_manager")
    @patch("logging.rich.rich_logger.rich_inspect")
    def test_inspect_functionality(self, mock_inspect, mock_console_manager):
        """Test object inspection functionality."""
        mock_console = Mock()
        mock_console_manager.get_console.return_value = mock_console

        test_obj = {"test": "object"}
        self.rich_logger.inspect(test_obj, title="Test Object", methods=True)

        mock_inspect.assert_called_once_with(
            test_obj,
            console=mock_console,
            title="Test Object",
            methods=True,
            help=False,  # From settings
            private=False,  # From settings
            dunder=False,  # From settings
            sort=True,  # From settings
        )

    @patch("logging.rich.rich_logger.RICH_AVAILABLE", True)
    @patch("logging.rich.rich_logger.console_manager")
    def test_pretty_print_functionality(self, mock_console_manager):
        """Test pretty print functionality."""
        mock_console = Mock()
        mock_console_manager.get_console.return_value = mock_console

        test_obj = {"complex": {"nested": {"data": [1, 2, 3]}}}
        self.rich_logger.pretty(test_obj, max_depth=2)

        mock_console.print.assert_called_once()

    def test_rich_unavailable_fallbacks(self):
        """Test all methods handle Rich unavailable gracefully."""
        with patch("logging.rich.rich_logger.RICH_AVAILABLE", False):
            # These should all complete without errors
            self.rich_logger.tree({"test": "data"})
            self.rich_logger.columns("col1", "col2")
            self.rich_logger.syntax("print('test')", "python")
            self.rich_logger.markdown("# Test")
            self.rich_logger.json({"test": "data"})
            self.rich_logger.bar_chart({"item": 5})
            self.rich_logger.text("test text")
            self.rich_logger.align("test", "center")
            self.rich_logger.inspect({"test": "obj"})
            self.rich_logger.pretty({"test": "obj"})

            # Interactive methods should return defaults
            result = self.rich_logger.prompt("test", default="default")
            self.assertEqual(result, "default")

            result = self.rich_logger.confirm("test", default=True)
            self.assertTrue(result)

            # Live should yield None
            with self.rich_logger.live("test") as live:
                self.assertIsNone(live)

    def test_custom_settings_override_defaults(self):
        """Test that method parameters override settings defaults."""
        custom_settings = RichFeatureSettings(
            prompt_show_default=False,
            prompt_show_choices=False,
            live_refresh_per_second=10,
            inspect_methods=True,
        )
        rich_logger = RichLogger(self.mock_logger, custom_settings)

        with (
            patch("logging.rich.rich_logger.RICH_AVAILABLE", True),
            patch(
                "logging.rich.rich_logger.console_manager"
            ) as mock_console_manager,
        ):
            mock_console = Mock()
            mock_console_manager.get_console.return_value = mock_console

            with patch(
                "logging.rich.rich_logger.Prompt"
            ) as mock_prompt:
                mock_prompt.ask.return_value = "test"

                # Method parameter should override setting
                rich_logger.prompt("test", show_default=True)

                # Verify the override was used
                call_args = mock_prompt.ask.call_args
                self.assertTrue(call_args.kwargs["show_default"])

    def test_empty_data_handling(self):
        """Test handling of empty or invalid data."""
        with (
            patch("logging.rich.rich_logger.RICH_AVAILABLE", True),
            patch(
                "logging.rich.rich_logger.console_manager"
            ) as mock_console_manager,
        ):
            mock_console = Mock()
            mock_console_manager.get_console.return_value = mock_console

            # Empty bar chart data should return early
            self.rich_logger.bar_chart({})
            mock_console.print.assert_not_called()

            # Reset mock
            mock_console.reset_mock()

            # Empty tree data should still work
            self.rich_logger.tree({})
            mock_console.print.assert_called_once()


if __name__ == "__main__":
    unittest.main()
