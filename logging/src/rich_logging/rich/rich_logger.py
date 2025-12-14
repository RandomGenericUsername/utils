"""Enhanced logger with Rich features integration."""

import logging as stdlib_logging
import rich_logging
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from .rich_console_manager import console_manager
from .rich_feature_settings import RichFeatureSettings

try:
    from rich import box
    from rich import inspect as rich_inspect
    from rich.align import Align
    from rich.columns import Columns
    from rich.console import Console
    from rich.json import JSON
    from rich.live import Live
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich.pretty import Pretty
    from rich.progress import Progress, TaskID
    from rich.prompt import Confirm, Prompt
    from rich.rule import Rule
    from rich.status import Status
    from rich.syntax import Syntax
    from rich.table import Table
    from rich.text import Text
    from rich.tree import Tree

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    Console = None
    Table = None
    Panel = None
    Rule = None
    Progress = None
    TaskID = None
    Status = None
    box = None
    Tree = None
    Columns = None
    Syntax = None
    Markdown = None
    JSON = None
    Live = None
    Text = None
    Align = None
    Pretty = None
    Prompt = None
    Confirm = None
    rich_inspect = None


class RichLogger:
    """
    Enhanced logger wrapper that adds Rich features to standard logging.

    Provides Rich tables, panels, progress bars, and other Rich components
    while maintaining full compatibility with standard stdlib_logging.Logger.
    """

    def __init__(
        self,
        logger: stdlib_logging.Logger,
        rich_settings: RichFeatureSettings | None = None,
    ):
        """
        Initialize Rich logger wrapper.

        Args:
            logger: Standard stdlib_logging.Logger instance to wrap
            rich_settings: Configuration for Rich features
        """
        self._logger = logger
        self._rich_settings = rich_settings or RichFeatureSettings()
        self._name = logger.name

    def __getattr__(self, name: str) -> Any:
        """Delegate all standard logging methods to wrapped logger."""
        return getattr(self._logger, name)

    def __copy__(self):
        """Return self for shallow copy (loggers should not be copied)."""
        return self

    def __deepcopy__(self, memo):
        """Return self for deep copy (loggers should not be copied)."""
        return self

    @property
    def name(self) -> str:
        """Get logger name."""
        return self._name

    def _get_console(self) -> Console | None:
        """Get the console for this logger."""
        if not RICH_AVAILABLE or not self._rich_settings.enabled:
            return None
        return console_manager.get_console(self._name)

    def table(
        self,
        data: list[list[Any]] | dict[str, list[Any]],
        *,
        title: str | None = None,
        show_header: bool | None = None,
        show_lines: bool | None = None,
        show_edge: bool | None = None,
        expand: bool | None = None,
        **kwargs,
    ) -> None:
        """
        Display a Rich table.

        Args:
            data: Table data as list of rows or dict of columns
            title: Optional table title
            show_header: Whether to show table header (uses settings
                default if None)
            show_lines: Whether to show lines between rows (uses settings
                default if None)
            show_edge: Whether to show table border (uses settings default
                if None)
            expand: Whether to expand to fill width (uses settings default
                if None)
            **kwargs: Additional arguments passed to Rich Table
        """
        console = self._get_console()
        if not console:
            return

        # Use settings defaults for None values
        show_header = (
            show_header
            if show_header is not None
            else self._rich_settings.table_show_header
        )
        show_lines = (
            show_lines
            if show_lines is not None
            else self._rich_settings.table_show_lines
        )
        show_edge = (
            show_edge
            if show_edge is not None
            else self._rich_settings.table_show_edge
        )
        expand = (
            expand if expand is not None else self._rich_settings.table_expand
        )

        table = Table(
            title=title,
            show_header=show_header,
            show_lines=show_lines,
            show_edge=show_edge,
            expand=expand,
            **kwargs,
        )

        if isinstance(data, dict):
            # Dict format: {"Column1": [values], "Column2": [values]}
            columns = list(data.keys())
            for col in columns:
                table.add_column(col)

            # Transpose data to get rows
            if data:
                max_rows = max(len(values) for values in data.values())
                for i in range(max_rows):
                    row = []
                    for col in columns:
                        values = data[col]
                        row.append(str(values[i]) if i < len(values) else "")
                    table.add_row(*row)

        elif isinstance(data, list) and data:
            # List format: [[row1], [row2], ...]
            if show_header and data:
                # First row as headers
                for header in data[0]:
                    table.add_column(str(header))
                # Remaining rows as data
                for row in data[1:]:
                    table.add_row(*[str(cell) for cell in row])
            else:
                # All rows as data, no headers
                if data:
                    for _ in range(len(data[0])):
                        table.add_column()
                    for row in data:
                        table.add_row(*[str(cell) for cell in row])

        console.print(table)

    def panel(
        self,
        content: Any,
        *,
        title: str | None = None,
        subtitle: str | None = None,
        border_style: str | None = None,
        box_style: str | None = None,
        expand: bool | None = None,
        padding: tuple[int, int] | None = None,
        **kwargs,
    ) -> None:
        """
        Display a Rich panel.

        Args:
            content: Content to display in the panel
            title: Optional panel title
            subtitle: Optional panel subtitle
            border_style: Border color/style (uses settings default if None)
            box_style: Box type ('rounded', 'square', 'double', etc.)
            expand: Whether to expand to fill width (uses settings default
                if None)
            padding: Padding as (vertical, horizontal) (uses settings
                default if None)
            **kwargs: Additional arguments passed to Rich Panel
        """
        console = self._get_console()
        if not console:
            return

        # Use settings defaults for None values
        border_style = (
            border_style
            if border_style is not None
            else self._rich_settings.panel_border_style
        )
        expand = (
            expand if expand is not None else self._rich_settings.panel_expand
        )
        padding = (
            padding
            if padding is not None
            else self._rich_settings.panel_padding
        )
        box_style = (
            box_style
            if box_style is not None
            else self._rich_settings.panel_box_style
        )

        # Handle box style
        panel_box = box.ROUNDED  # Default
        if box_style == "square":
            panel_box = box.SQUARE
        elif box_style == "double":
            panel_box = box.DOUBLE
        elif box_style == "heavy":
            panel_box = box.HEAVY
        elif box_style == "ascii":
            panel_box = box.ASCII

        panel = Panel(
            content,
            title=title,
            subtitle=subtitle,
            border_style=border_style,
            box=panel_box,
            expand=expand,
            padding=padding,
            **kwargs,
        )

        console.print(panel)

    def rule(
        self,
        title: str | None = None,
        *,
        style: str | None = None,
        align: str | None = None,
        **kwargs,
    ) -> None:
        """
        Display a Rich rule/separator.

        Args:
            title: Optional rule title
            style: Rule style (uses settings default if None)
            align: Title alignment (uses settings default if None)
            **kwargs: Additional arguments passed to Rich Rule
        """
        console = self._get_console()
        if not console:
            return

        # Use settings defaults for None values
        style = style if style is not None else self._rich_settings.rule_style
        align = align if align is not None else self._rich_settings.rule_align

        rule = Rule(title=title, style=style, align=align, **kwargs)

        console.print(rule)

    @contextmanager
    def progress(
        self,
        description: str | None = None,
        total: int | None = None,
        **kwargs,
    ) -> Iterator[Progress]:
        """
        Create a Rich progress context manager.

        Args:
            description: Progress description
            total: Total number of steps (None for indeterminate)
            **kwargs: Additional arguments passed to Rich Progress

        Yields:
            Progress instance for updating progress

        Example:
            with logger.progress("Processing files", total=100) as progress:
                task = progress.add_task("Processing", total=100)
                for i in range(100):
                    progress.update(task, advance=1)
        """
        console = self._get_console()
        if not console:
            # Fallback: yield a dummy progress object
            yield _DummyProgress()
            return

        # Use settings defaults
        auto_refresh = kwargs.pop(
            "auto_refresh", self._rich_settings.progress_auto_refresh
        )
        refresh_per_second = kwargs.pop(
            "refresh_per_second",
            self._rich_settings.progress_refresh_per_second,
        )
        speed_estimate_period = kwargs.pop(
            "speed_estimate_period",
            self._rich_settings.progress_speed_estimate_period,
        )

        with Progress(
            console=console,
            auto_refresh=auto_refresh,
            refresh_per_second=refresh_per_second,
            speed_estimate_period=speed_estimate_period,
            **kwargs,
        ) as progress:
            if description and total is not None:
                # Auto-add task if description and total provided
                task = progress.add_task(description, total=total)
                progress._auto_task = task  # Store for potential use
            yield progress

    @contextmanager
    def status(
        self, message: str, *, spinner: str | None = None, **kwargs
    ) -> Iterator[Status]:
        """
        Create a Rich status context manager.

        Args:
            message: Status message to display
            spinner: Spinner style (uses settings default if None)
            **kwargs: Additional arguments passed to Rich Status

        Yields:
            Status instance for updating status

        Example:
            with logger.status("Loading data...") as status:
                # Do work here
                status.update("Processing data...")
                # More work
        """
        console = self._get_console()
        if not console:
            # Fallback: yield a dummy status object
            yield _DummyStatus()
            return

        # Use settings defaults
        spinner = (
            spinner
            if spinner is not None
            else self._rich_settings.status_spinner
        )
        refresh_per_second = kwargs.pop(
            "refresh_per_second", self._rich_settings.status_refresh_per_second
        )

        with Status(
            message,
            console=console,
            spinner=spinner,
            refresh_per_second=refresh_per_second,
            **kwargs,
        ) as status:
            yield status

    def tree(
        self,
        data: dict[str, Any] | str,
        *,
        title: str | None = None,
        guide_style: str | None = None,
        expanded: bool | None = None,
        **kwargs,
    ) -> None:
        """
        Display hierarchical data as a tree.

        Args:
            data: Tree data as nested dict or root label string
            title: Optional tree title (used as root if data is dict)
            guide_style: Style for tree guide lines (uses settings default
                if None)
            expanded: Whether nodes should be expanded (uses settings
                default if None)
            **kwargs: Additional arguments passed to Rich Tree

        Examples:
            # Simple tree from dict
            logger.tree({
                "config/": {
                    "nvim/": "Neovim configuration",
                    "zsh/": "Zsh configuration"
                },
                "scripts/": {
                    "install.sh": "Installation script"
                }
            }, title="Dotfiles Structure")

            # Tree with custom styling
            logger.tree(data, guide_style="bold blue", expanded=False)
        """
        console = self._get_console()
        if not console:
            return

        # Use settings defaults for None values
        guide_style = (
            guide_style
            if guide_style is not None
            else self._rich_settings.tree_guide_style
        )
        expanded = (
            expanded
            if expanded is not None
            else self._rich_settings.tree_expanded
        )

        # Create root tree
        if isinstance(data, dict):
            root_label = title or "Tree"
            tree = Tree(
                root_label,
                guide_style=guide_style,
                expanded=expanded,
                **kwargs,
            )
            self._add_tree_nodes(tree, data, expanded)
        else:
            # data is a string label
            tree = Tree(
                data, guide_style=guide_style, expanded=expanded, **kwargs
            )

        console.print(tree)

    def _add_tree_nodes(
        self, parent_node: "Tree", data: dict[str, Any], expanded: bool
    ) -> None:
        """
        Recursively add nodes to a tree.

        Args:
            parent_node: Parent tree node to add children to
            data: Dictionary of child data
            expanded: Whether nodes should be expanded
        """
        if not RICH_AVAILABLE:
            return

        for key, value in data.items():
            if isinstance(value, dict):
                # Directory/folder node
                branch = parent_node.add(
                    (
                        f"[bold blue]{key}[/bold blue]"
                        if key.endswith("/")
                        else f"[bold]{key}[/bold]"
                    ),
                    expanded=expanded,
                )
                self._add_tree_nodes(branch, value, expanded)
            elif isinstance(value, list):
                # List of items
                branch = parent_node.add(
                    f"[bold]{key}[/bold]", expanded=expanded
                )
                for item in value:
                    if isinstance(item, dict):
                        self._add_tree_nodes(branch, item, expanded)
                    else:
                        branch.add(str(item))
            else:
                # Leaf node
                if value:
                    parent_node.add(f"{key} [dim]({value})[/dim]")
                else:
                    parent_node.add(key)

    def columns(
        self,
        *renderables: Any,
        equal: bool | None = None,
        expand: bool | None = None,
        padding: tuple[int, int] | None = None,
        **kwargs,
    ) -> None:
        """
        Display content in multiple columns.

        Args:
            *renderables: Content to display in columns (can be strings,
                panels, tables, etc.)
            equal: Whether columns should have equal width (uses settings
                default if None)
            expand: Whether columns should expand to fill width (uses
                settings default if None)
            padding: Padding as (vertical, horizontal) (uses settings
                default if None)
            **kwargs: Additional arguments passed to Rich Columns

        Examples:
            # Simple text columns
            logger.columns("Column 1", "Column 2", "Column 3")

            # Mixed content columns
            logger.columns(
                Panel("System Info\nOS: Linux", title="Environment"),
                Panel("Progress\n✓ Complete", title="Status"),
                Panel("Next Steps\n• Restart", title="Actions")
            )

            # Custom layout
            logger.columns(table1, table2, equal=True, expand=True)
        """
        console = self._get_console()
        if not console:
            return

        # Use settings defaults for None values
        equal = (
            equal if equal is not None else self._rich_settings.columns_equal
        )
        expand = (
            expand
            if expand is not None
            else self._rich_settings.columns_expand
        )
        padding = (
            padding
            if padding is not None
            else self._rich_settings.columns_padding
        )

        columns = Columns(
            renderables,
            equal=equal,
            expand=expand,
            padding=padding,
            **kwargs,
        )

        console.print(columns)

    def syntax(
        self,
        code: str,
        lexer: str = "python",
        *,
        theme: str | None = None,
        line_numbers: bool | None = None,
        word_wrap: bool | None = None,
        background_color: str | None = None,
        title: str | None = None,
        **kwargs,
    ) -> None:
        """
        Display syntax-highlighted code.

        Args:
            code: Code string to highlight
            lexer: Language lexer (e.g., 'python', 'bash', 'javascript',
                'json')
            theme: Syntax highlighting theme (uses settings default if
                None)
            line_numbers: Whether to show line numbers (uses settings
                default if None)
            word_wrap: Whether to enable word wrap (uses settings default
                if None)
            background_color: Background color (uses settings default if
                None)
            title: Optional title for the code block
            **kwargs: Additional arguments passed to Rich Syntax

        Examples:
            # Python code
            logger.syntax('print("Hello, World!")', lexer="python")

            # Bash script with line numbers
            logger.syntax(
                script_content, lexer="bash", line_numbers=True,
                title="install.sh"
            )

            # JSON with custom theme
            logger.syntax(json_str, lexer="json", theme="github-dark")
        """
        console = self._get_console()
        if not console:
            return

        # Use settings defaults for None values
        theme = (
            theme if theme is not None else self._rich_settings.syntax_theme
        )
        line_numbers = (
            line_numbers
            if line_numbers is not None
            else self._rich_settings.syntax_line_numbers
        )
        word_wrap = (
            word_wrap
            if word_wrap is not None
            else self._rich_settings.syntax_word_wrap
        )
        background_color = (
            background_color
            if background_color is not None
            else self._rich_settings.syntax_background_color
        )

        syntax = Syntax(
            code,
            lexer,
            theme=theme,
            line_numbers=line_numbers,
            word_wrap=word_wrap,
            background_color=background_color,
            **kwargs,
        )

        if title:
            # Wrap in panel with title
            panel = Panel(syntax, title=title, expand=False)
            console.print(panel)
        else:
            console.print(syntax)

    def markdown(
        self,
        markdown_text: str,
        *,
        code_theme: str | None = None,
        hyperlinks: bool | None = None,
        inline_code_lexer: str | None = None,
        **kwargs,
    ) -> None:
        """
        Render markdown text with Rich formatting.

        Args:
            markdown_text: Markdown text to render
            code_theme: Theme for code blocks (uses settings default if
                None)
            hyperlinks: Whether to enable hyperlinks (uses settings default
                if None)
            inline_code_lexer: Lexer for inline code (uses settings default
                if None)
            **kwargs: Additional arguments passed to Rich Markdown

        Examples:
            # Simple markdown
            logger.markdown(
                "# Installation Complete\\n\\nEverything is ready!"
            )

            # Complex markdown with code
            logger.markdown('''
            # Installation Summary

            ## What was installed:
            - **Neovim** configuration
            - **Zsh** with custom theme

            ## Next steps:
            1. Restart terminal
            2. Run `nvim` to install plugins

            ```bash
            # Test your setup
            nvim --version
            ```
            ''')
        """
        console = self._get_console()
        if not console:
            return

        # Use settings defaults for None values
        code_theme = (
            code_theme
            if code_theme is not None
            else self._rich_settings.markdown_code_theme
        )
        hyperlinks = (
            hyperlinks
            if hyperlinks is not None
            else self._rich_settings.markdown_hyperlinks
        )
        inline_code_lexer = (
            inline_code_lexer
            if inline_code_lexer is not None
            else self._rich_settings.markdown_inline_code_lexer
        )

        markdown = Markdown(
            markdown_text,
            code_theme=code_theme,
            hyperlinks=hyperlinks,
            inline_code_lexer=inline_code_lexer,
            **kwargs,
        )

        console.print(markdown)

    def json(
        self,
        data: dict[str, Any] | list[Any] | str,
        *,
        indent: int | None = None,
        highlight: bool | None = None,
        sort_keys: bool | None = None,
        title: str | None = None,
        **kwargs,
    ) -> None:
        """
        Display JSON data with syntax highlighting.

        Args:
            data: JSON data (dict, list, or JSON string)
            indent: Indentation level (uses settings default if None)
            highlight: Whether to enable syntax highlighting (uses settings
                default if None)
            sort_keys: Whether to sort keys (uses settings default if None)
            title: Optional title for the JSON display
            **kwargs: Additional arguments passed to Rich JSON

        Examples:
            # Dictionary data
            config = {
                "name": "dotfiles", "version": "1.0",
                "files": ["zshrc", "vimrc"]
            }
            logger.json(config, title="Configuration")

            # JSON string
            logger.json('{"status": "complete", "errors": []}')

            # Custom formatting
            logger.json(data, indent=4, sort_keys=True, highlight=True)
        """
        console = self._get_console()
        if not console:
            return

        # Use settings defaults for None values
        indent = (
            indent if indent is not None else self._rich_settings.json_indent
        )
        highlight = (
            highlight
            if highlight is not None
            else self._rich_settings.json_highlight
        )
        sort_keys = (
            sort_keys
            if sort_keys is not None
            else self._rich_settings.json_sort_keys
        )

        # Handle different input types
        if isinstance(data, str):
            # Assume it's a JSON string
            try:
                import json as json_module

                parsed_data = json_module.loads(data)
                json_obj = JSON.from_data(
                    parsed_data,
                    indent=indent,
                    highlight=highlight,
                    sort_keys=sort_keys,
                    **kwargs,
                )
            except (json_module.JSONDecodeError, ImportError):
                # Fallback: treat as raw JSON string
                json_obj = JSON(data, **kwargs)
        else:
            # Dict or list
            json_obj = JSON.from_data(
                data,
                indent=indent,
                highlight=highlight,
                sort_keys=sort_keys,
                **kwargs,
            )

        if title:
            # Wrap in panel with title
            panel = Panel(json_obj, title=title, expand=False)
            console.print(panel)
        else:
            console.print(json_obj)

    @contextmanager
    def live(
        self,
        renderable: Any,
        *,
        refresh_per_second: int | None = None,
        vertical_overflow: str | None = None,
        auto_refresh: bool | None = None,
        **kwargs,
    ) -> Iterator[Live | None]:
        """
        Create a live-updating display context manager.

        Args:
            renderable: Content to display and update (table, panel, etc.)
            refresh_per_second: Refresh rate (uses settings default if
                None)
            vertical_overflow: Overflow handling (uses settings default if
                None)
            auto_refresh: Whether to auto-refresh (uses settings default if
                None)
            **kwargs: Additional arguments passed to Rich Live

        Yields:
            Live instance for updating display (None if Rich not available)

        Examples:
            # Live updating table
            table = Table(title="Installation Progress")
            table.add_column("File")
            table.add_column("Status")

            with logger.live(table, refresh_per_second=2) as live:
                for file in files:
                    table.add_row(file, "Installing...")
                    if live:
                        live.update(table)
                    install_file(file)
                    if live:
                        table.rows[-1] = (file, "✓ Complete")
                        live.update(table)
        """
        console = self._get_console()
        if not console:
            # Fallback: yield None
            yield None
            return

        # Use settings defaults for None values
        refresh_per_second = (
            refresh_per_second
            if refresh_per_second is not None
            else self._rich_settings.live_refresh_per_second
        )
        vertical_overflow = (
            vertical_overflow
            if vertical_overflow is not None
            else self._rich_settings.live_vertical_overflow
        )
        auto_refresh = (
            auto_refresh
            if auto_refresh is not None
            else self._rich_settings.live_auto_refresh
        )

        with Live(
            renderable,
            console=console,
            refresh_per_second=refresh_per_second,
            vertical_overflow=vertical_overflow,
            auto_refresh=auto_refresh,
            **kwargs,
        ) as live:
            yield live

    def bar_chart(
        self,
        data: dict[str, int | float],
        *,
        title: str | None = None,
        width: int | None = None,
        character: str | None = None,
        show_values: bool | None = None,
        **kwargs,
    ) -> None:
        """
        Display a simple bar chart using table format.

        Args:
            data: Dictionary mapping labels to values
            title: Optional chart title
            width: Width of bars in characters (uses settings default if None)
            character: Character to use for bars (uses settings default if
                None)
            show_values: Whether to show numeric values (uses settings
                default if None)
            **kwargs: Additional arguments passed to Rich Table

        Examples:
            # Simple bar chart
            logger.bar_chart({
                "Config Files": 15,
                "Scripts": 8,
                "Themes": 12,
                "Plugins": 25
            }, title="Installation Breakdown")

            # Custom styling
            logger.bar_chart(data, width=30, character="▓", show_values=True)
        """
        console = self._get_console()
        if not console:
            return

        if not data:
            return

        # Use settings defaults for None values
        width = (
            width if width is not None else self._rich_settings.bar_chart_width
        )
        character = (
            character
            if character is not None
            else self._rich_settings.bar_chart_character
        )
        show_values = (
            show_values
            if show_values is not None
            else self._rich_settings.bar_chart_show_values
        )

        # Create table for bar chart
        table = Table(title=title, show_header=True, **kwargs)
        table.add_column("Item", style="cyan", no_wrap=True)
        if show_values:
            table.add_column("Value", style="magenta", justify="right")
        table.add_column("Chart", style="green")

        # Calculate scaling
        max_value = max(data.values()) if data else 1
        if max_value == 0:
            max_value = 1

        # Add rows
        for item, value in data.items():
            bar_width = int((value / max_value) * width)
            bar = character * bar_width

            if show_values:
                if isinstance(value, float):
                    value_str = f"{value:.1f}"
                else:
                    value_str = str(value)
                table.add_row(str(item), value_str, bar)
            else:
                table.add_row(str(item), bar)

        console.print(table)

    def text(
        self,
        text: str,
        *,
        style: str | None = None,
        justify: str | None = None,
        overflow: str | None = None,
        no_wrap: bool | None = None,
        **kwargs,
    ) -> None:
        """
        Display styled and formatted text.

        Args:
            text: Text to display
            style: Text style (e.g., "bold red", "italic blue")
            justify: Text justification (uses settings default if None)
            overflow: Overflow handling (uses settings default if None)
            no_wrap: Whether to disable wrapping (uses settings default if
                None)
            **kwargs: Additional arguments passed to Rich Text

        Examples:
            # Simple styled text
            logger.text("Success!", style="bold green")

            # Centered text
            logger.text(
                "Installation Complete", justify="center", style="bold"
            )

            # Text with overflow handling
            logger.text(long_text, overflow="ellipsis", no_wrap=True)
        """
        console = self._get_console()
        if not console:
            return

        # Use settings defaults for None values
        justify = (
            justify
            if justify is not None
            else self._rich_settings.text_justify
        )
        overflow = (
            overflow
            if overflow is not None
            else self._rich_settings.text_overflow
        )
        no_wrap = (
            no_wrap
            if no_wrap is not None
            else self._rich_settings.text_no_wrap
        )

        rich_text = Text(
            text,
            style=style,
            justify=justify,
            overflow=overflow,
            no_wrap=no_wrap,
            **kwargs,
        )

        console.print(rich_text)

    def align(
        self,
        renderable: Any,
        align: str = "center",
        *,
        style: str | None = None,
        vertical: str | None = None,
        **kwargs,
    ) -> None:
        """
        Display content with specific alignment.

        Args:
            renderable: Content to align (text, panel, table, etc.)
            align: Horizontal alignment ("left", "center", "right")
            style: Optional style for the aligned content
            vertical: Vertical alignment ("top", "middle", "bottom")
            **kwargs: Additional arguments passed to Rich Align

        Examples:
            # Center a panel
            panel = Panel("Centered content", title="Info")
            logger.align(panel, "center")

            # Right-align text
            logger.align("Right-aligned text", "right", style="bold")

            # Center with vertical alignment
            logger.align(content, "center", vertical="middle")
        """
        console = self._get_console()
        if not console:
            return

        aligned = Align(
            renderable,
            align=align,
            style=style,
            vertical=vertical,
            **kwargs,
        )

        console.print(aligned)

    def prompt(
        self,
        question: str,
        *,
        choices: list[str] | None = None,
        default: str | None = None,
        show_default: bool | None = None,
        show_choices: bool | None = None,
        **kwargs,
    ) -> str:
        """
        Display an interactive prompt for user input.

        Args:
            question: Question to ask the user
            choices: List of valid choices (None for free text input)
            default: Default value if user presses Enter
            show_default: Whether to show default value (uses settings
                default if None)
            show_choices: Whether to show available choices (uses settings
                default if None)
            **kwargs: Additional arguments passed to Rich Prompt

        Returns:
            User's input as string

        Examples:
            # Simple text input
            name = logger.prompt("Enter your name")

            # Choice selection
            install_type = logger.prompt(
                "Choose installation type",
                choices=["symlink", "copy", "template"],
                default="symlink"
            )

            # Custom prompt
            path = logger.prompt(
                "Install directory", default="/home/user/.config"
            )
        """
        console = self._get_console()
        if not console:
            return default or ""

        # Use settings defaults for None values
        show_default = (
            show_default
            if show_default is not None
            else self._rich_settings.prompt_show_default
        )
        show_choices = (
            show_choices
            if show_choices is not None
            else self._rich_settings.prompt_show_choices
        )

        if choices:
            return Prompt.ask(
                question,
                choices=choices,
                default=default,
                show_default=show_default,
                show_choices=show_choices,
                console=console,
                **kwargs,
            )
        else:
            return Prompt.ask(
                question,
                default=default,
                show_default=show_default,
                console=console,
                **kwargs,
            )

    def confirm(
        self,
        question: str,
        *,
        default: bool = False,
        **kwargs,
    ) -> bool:
        """
        Display a yes/no confirmation prompt.

        Args:
            question: Question to ask the user
            default: Default value if user presses Enter
            **kwargs: Additional arguments passed to Rich Confirm

        Returns:
            True if user confirms, False otherwise

        Examples:
            # Simple confirmation
            if logger.confirm("Do you want to continue?"):
                proceed_with_installation()

            # With default value
            backup = logger.confirm("Backup existing files?", default=True)
        """
        console = self._get_console()
        if not console:
            return default

        return Confirm.ask(
            question,
            default=default,
            console=console,
            **kwargs,
        )

    def inspect(
        self,
        obj: Any,
        *,
        title: str | None = None,
        methods: bool | None = None,
        help: bool | None = None,
        private: bool | None = None,
        dunder: bool | None = None,
        sort: bool | None = None,
        **kwargs,
    ) -> None:
        """
        Inspect and display detailed information about an object.

        Args:
            obj: Object to inspect
            title: Optional title for the inspection
            methods: Whether to show methods (uses settings default if None)
            help: Whether to show help text (uses settings default if None)
            private: Whether to show private attributes (uses settings
                default if None)
            dunder: Whether to show dunder methods (uses settings default
                if None)
            sort: Whether to sort attributes (uses settings default if None)
            **kwargs: Additional arguments passed to Rich inspect

        Examples:
            # Inspect a configuration object
            logger.inspect(config_object, title="Configuration Settings")

            # Detailed inspection with methods
            logger.inspect(logger_instance, methods=True, help=True)

            # Inspect with custom options
            logger.inspect(obj, private=True, dunder=False, sort=True)
        """
        console = self._get_console()
        if not console:
            return

        # Use settings defaults for None values
        methods = (
            methods
            if methods is not None
            else self._rich_settings.inspect_methods
        )
        help = help if help is not None else self._rich_settings.inspect_help
        private = (
            private
            if private is not None
            else self._rich_settings.inspect_private
        )
        dunder = (
            dunder
            if dunder is not None
            else self._rich_settings.inspect_dunder
        )
        sort = sort if sort is not None else self._rich_settings.inspect_sort

        rich_inspect(
            obj,
            console=console,
            title=title,
            methods=methods,
            help=help,
            private=private,
            dunder=dunder,
            sort=sort,
            **kwargs,
        )

    def pretty(
        self,
        obj: Any,
        *,
        indent_guides: bool | None = None,
        max_length: int | None = None,
        max_string: int | None = None,
        max_depth: int | None = None,
        title: str | None = None,
        **kwargs,
    ) -> None:
        """
        Pretty print Python objects with Rich formatting.

        Args:
            obj: Object to pretty print
            indent_guides: Whether to show indent guides (uses settings
                default if None)
            max_length: Maximum length for sequences (uses settings default
                if None)
            max_string: Maximum string length (uses settings default if
                None)
            max_depth: Maximum depth for nested objects (uses settings
                default if None)
            title: Optional title for the pretty print display
            **kwargs: Additional arguments passed to Rich Pretty

        Examples:
            # Pretty print a dictionary
            logger.pretty({"config": config_dict, "errors": error_list})

            # Pretty print with limits
            logger.pretty(large_object, max_depth=3, max_length=10)

            # Custom formatting
            logger.pretty(
                obj, indent_guides=True, max_string=50, title="Debug Data"
            )
        """
        console = self._get_console()
        if not console:
            return

        # Use settings defaults for None values
        indent_guides = (
            indent_guides
            if indent_guides is not None
            else self._rich_settings.pretty_indent_guides
        )
        max_length = (
            max_length
            if max_length is not None
            else self._rich_settings.pretty_max_length
        )
        max_string = (
            max_string
            if max_string is not None
            else self._rich_settings.pretty_max_string
        )
        max_depth = (
            max_depth
            if max_depth is not None
            else self._rich_settings.pretty_max_depth
        )

        pretty = Pretty(
            obj,
            indent_guides=indent_guides,
            max_length=max_length,
            max_string=max_string,
            max_depth=max_depth,
            **kwargs,
        )

        if title:
            # Wrap in panel with title
            panel = Panel(pretty, title=title, expand=False)
            console.print(panel)
        else:
            console.print(pretty)


class _DummyProgress:
    """Dummy progress object for fallback when Rich is not available."""

    def add_task(self, _description: str, **_kwargs) -> int:
        """Add a dummy task."""
        return 0

    def update(self, task_id: int, **kwargs) -> None:
        """Update dummy task (no-op)."""
        pass

    def advance(self, task_id: int, advance: float = 1) -> None:
        """Advance dummy task (no-op)."""
        pass


class _DummyStatus:
    """Dummy status object for fallback when Rich is not available."""

    def update(self, message: str) -> None:
        """Update dummy status (no-op)."""
        pass
