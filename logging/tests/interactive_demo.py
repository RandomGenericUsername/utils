#!/usr/bin/env python3
"""Interactive demo for Rich features in the logging module."""

import sys

from logging import (
    ConsoleHandlers,
    Log,
    LogLevels,
    RichFeatureSettings,
    RichHandlerSettings,
)


def interactive_demo():
    """Demo interactive Rich features."""

    # Create logger with all Rich features enabled
    logger = Log.create_logger(
        "interactive_demo",
        log_level=LogLevels.INFO,
        console_handler_type=ConsoleHandlers.RICH,
        handler_config=RichHandlerSettings(
            show_time=True, show_path=False, markup=True, rich_tracebacks=True
        ),
        rich_features=RichFeatureSettings(
            enabled=True, panel_border_style="blue"
        ),
    )

    logger.panel(
        "Welcome to the Interactive Rich Features Demo!\n\n"
        "This demo will show you the interactive features of the logging "
        "module.",
        title="Interactive Demo",
        border_style="blue",
    )

    # Test prompts
    logger.rule("Interactive Prompts Test")

    try:
        # Simple text input
        name = logger.prompt("What's your name?", default="User")
        logger.info(f"Hello, {name}!")

        # Choice selection
        favorite_editor = logger.prompt(
            "What's your favorite editor?",
            choices=["vim", "nvim", "emacs", "vscode", "other"],
            default="nvim",
        )
        logger.info(f"Great choice! {favorite_editor} is awesome.")

        # Confirmation
        wants_demo = logger.confirm(
            "Would you like to see more features?", default=True
        )

        if wants_demo:
            logger.text("✅ Continuing with the demo...", style="bold green")

            # More interactive features
            install_type = logger.prompt(
                "Choose installation type",
                choices=["symlink", "copy", "template"],
                default="symlink",
            )

            backup_files = logger.confirm(
                "Create backup of existing files?", default=True
            )

            # Summary
            summary = f"""
**Configuration Summary:**
- Name: {name}
- Editor: {favorite_editor}
- Install Type: {install_type}
- Backup: {"Yes" if backup_files else "No"}
"""

            logger.markdown(summary)

            final_confirm = logger.confirm(
                "Proceed with these settings?", default=True
            )

            if final_confirm:
                logger.panel(
                    "🎉 Demo completed successfully!\n\n"
                    "All interactive features are working properly.",
                    title="Success",
                    border_style="green",
                )
            else:
                logger.panel(
                    "Demo cancelled by user.",
                    title="Cancelled",
                    border_style="yellow",
                )
        else:
            logger.text(
                "Demo ended early. Thanks for trying it out!", style="yellow"
            )

    except KeyboardInterrupt:
        logger.panel(
            "Demo interrupted by user (Ctrl+C).",
            title="Interrupted",
            border_style="red",
        )
    except Exception as e:
        logger.panel(
            f"An error occurred: {e}", title="Error", border_style="red"
        )


if __name__ == "__main__":
    print(
        "Note: This is an interactive demo. Run it manually to test prompts."
    )
    print("For automated testing, use the integration_test.py instead.")

    # Only run interactively if explicitly requested
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_demo()
    else:
        print("Add --interactive flag to run the interactive demo.")
