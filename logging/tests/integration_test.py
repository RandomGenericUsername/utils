#!/usr/bin/env python3
"""Integration test for all Rich features in the logging module."""

import time

from logging import (
    ConsoleHandlers,
    Log,
    LogLevels,
    RichFeatureSettings,
    RichHandlerSettings,
)


def test_all_rich_features():
    """Test all Rich features in an integrated scenario."""

    # Create logger with all Rich features enabled
    logger = Log.create_logger(
        "integration_test",
        log_level=LogLevels.INFO,
        console_handler_type=ConsoleHandlers.RICH,
        handler_config=RichHandlerSettings(
            show_time=True, show_path=False, markup=True, rich_tracebacks=True
        ),
        rich_features=RichFeatureSettings(
            enabled=True,
            table_show_lines=True,
            panel_border_style="blue",
            tree_expanded=True,
            syntax_theme="monokai",
            json_indent=2,
            bar_chart_width=25,
        ),
    )

    # Test basic logging
    logger.info("🚀 Starting Rich Features Integration Test")

    # Test rule
    logger.rule("Tree Display Test", style="bold blue")

    # Test tree display
    file_structure = {
        "dotfiles/": {
            "config/": {
                "nvim/": "Neovim configuration",
                "zsh/": "Zsh configuration",
                "git/": "Git configuration",
            },
            "scripts/": {
                "install.sh": "Installation script",
                "backup.sh": "Backup script",
            },
        },
        "docs/": {"README.md": "Documentation", "CHANGELOG.md": "Change log"},
    }

    logger.tree(file_structure, title="Dotfiles Structure")

    # Test columns
    logger.rule("Multi-Column Layout Test")

    # Create panels directly for columns (since panel() method prints
    # immediately)
    from rich.panel import Panel

    system_panel = Panel(
        "OS: Linux\nShell: zsh\nTerminal: kitty", title="System Info"
    )

    progress_panel = Panel(
        "✓ Backup complete\n✓ Files copied\n⧗ Configuring...", title="Progress"
    )

    next_panel = Panel(
        "• Restart shell\n• Test config\n• Enjoy!", title="Next Steps"
    )

    logger.columns(system_panel, progress_panel, next_panel, equal=True)

    # Test syntax highlighting
    logger.rule("Syntax Highlighting Test")

    python_code = '''
def install_dotfiles():
    """Install dotfiles with backup."""
    backup_existing_files()
    create_symlinks()
    logger.info("Installation complete!")
    return True
'''

    logger.syntax(
        python_code, lexer="python", title="install.py", line_numbers=True
    )

    bash_script = """#!/bin/bash
echo "Installing dotfiles..."
cp ~/.zshrc ~/.zshrc.backup
ln -sf ~/dotfiles/zshrc ~/.zshrc
echo "Done!"
"""

    logger.syntax(bash_script, lexer="bash", title="install.sh")

    # Test markdown
    logger.rule("Markdown Rendering Test")

    markdown_content = """
# Installation Complete! 🎉

## What was installed:
- **Neovim** configuration with LSP
- **Zsh** with Oh My Zsh theme
- **Git** configuration and aliases

## Next steps:
1. Restart your terminal
2. Run `nvim` to install plugins
3. Enjoy your new setup!

```bash
# Test your setup
nvim --version
git --version
```
"""

    logger.markdown(markdown_content)

    # Test JSON display
    logger.rule("JSON Display Test")

    config_data = {
        "installation": {
            "type": "symlink",
            "backup": True,
            "timestamp": "2024-01-15T10:30:00Z",
        },
        "files": [
            {"source": "zshrc", "target": "~/.zshrc", "status": "success"},
            {"source": "vimrc", "target": "~/.vimrc", "status": "success"},
        ],
        "stats": {"total": 15, "successful": 15, "failed": 0},
    }

    logger.json(config_data, title="Installation Report")

    # Test bar chart
    logger.rule("Bar Chart Test")

    file_counts = {
        "Config Files": 15,
        "Scripts": 8,
        "Themes": 12,
        "Plugins": 25,
        "Docs": 6,
    }

    logger.bar_chart(file_counts, title="Files by Category")

    # Test text styling and alignment
    logger.rule("Text Styling Test")

    logger.text(
        "🎉 Installation Successful! 🎉", style="bold green", justify="center"
    )
    logger.text("Warning: Some files were skipped", style="yellow")
    logger.align("Centered important message", "center", style="bold blue")

    # Test object inspection
    logger.rule("Object Inspection Test")

    class TestConfig:
        def __init__(self):
            self.debug = True
            self.log_level = "INFO"
            self.features = ["backup", "symlink"]

        def get_status(self):
            return "ready"

    config = TestConfig()
    logger.inspect(config, title="Configuration Object")

    # Test pretty printing
    complex_data = {
        "settings": {
            "theme": "dark",
            "plugins": ["git", "zsh", "vim"],
            "features": {"auto_backup": True, "notifications": False},
        },
        "recent": [
            {"name": "nvim", "date": "2024-01-15", "status": "success"},
            {"name": "tmux", "date": "2024-01-14", "status": "success"},
        ],
    }

    logger.pretty(complex_data, title="Complex Configuration")

    # Test live updates (brief demo)
    logger.rule("Live Updates Test")

    files = ["zshrc", "vimrc", "gitconfig"]

    # Create a simple live demo without modifying table rows
    with logger.live("Starting installation...", refresh_per_second=2) as live:
        for i, file in enumerate(files):
            status = f"Installing {file}... ({i + 1}/{len(files)})"
            if live:
                live.update(status)
            time.sleep(0.8)

        if live:
            live.update("✅ All files installed successfully!")

    # Final success message
    logger.rule("Integration Test Complete", style="bold green")
    logger.panel(
        "All Rich features tested successfully!\n\n"
        "✅ Tree display\n"
        "✅ Multi-column layouts\n"
        "✅ Syntax highlighting\n"
        "✅ Markdown rendering\n"
        "✅ JSON display\n"
        "✅ Bar charts\n"
        "✅ Text styling\n"
        "✅ Object inspection\n"
        "✅ Live updates",
        title="Test Results",
        border_style="green",
    )

    logger.info("🎉 Integration test completed successfully!")


if __name__ == "__main__":
    test_all_rich_features()
