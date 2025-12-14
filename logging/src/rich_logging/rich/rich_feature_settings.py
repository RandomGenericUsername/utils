"""Configuration settings for Rich features in logging."""

from dataclasses import dataclass


@dataclass
class RichFeatureSettings:
    """
    Type-safe configuration for Rich features.

    Provides default settings for Rich tables, panels, progress bars,
    and other Rich components used in logging.
    """

    # Global Rich features control
    enabled: bool = True
    """Whether Rich features are enabled (fallback to no-op if False)."""

    # Table settings
    table_show_header: bool = True
    """Whether to show table headers by default."""

    table_show_lines: bool = False
    """Whether to show lines between table rows by default."""

    table_show_edge: bool = True
    """Whether to show table border by default."""

    table_expand: bool = False
    """Whether tables should expand to fill available width by default."""

    # Panel settings
    panel_border_style: str = "blue"
    """Default border color/style for panels."""

    panel_box_style: str = "rounded"
    """Default box style for panels ('rounded', 'square', 'double',
    'heavy', 'ascii')."""

    panel_expand: bool = True
    """Whether panels should expand to fill available width by default."""

    panel_padding: tuple[int, int] = (0, 1)
    """Default padding for panels (vertical, horizontal)."""

    # Rule settings
    rule_style: str = "rule.line"
    """Default style for rules/separators."""

    rule_align: str = "center"
    """Default alignment for rule titles ('left', 'center', 'right')."""

    # Progress settings
    progress_auto_refresh: bool = True
    """Whether progress bars should auto-refresh."""

    progress_refresh_per_second: int = 10
    """Refresh rate for progress bars (times per second)."""

    progress_speed_estimate_period: float = 30.0
    """Period for speed estimation in progress bars (seconds)."""

    # Status settings
    status_spinner: str = "dots"
    """Default spinner style for status indicators."""

    status_refresh_per_second: int = 12.5
    """Refresh rate for status spinners (times per second)."""

    # Console settings
    console_width: int | None = None
    """Fixed console width (None for auto-detection)."""

    console_height: int | None = None
    """Fixed console height (None for auto-detection)."""

    # Tree settings
    tree_guide_style: str = "tree.line"
    """Default style for tree guide lines."""

    tree_expanded: bool = True
    """Whether tree nodes should be expanded by default."""

    # Columns settings
    columns_equal: bool = False
    """Whether columns should have equal width."""

    columns_expand: bool = False
    """Whether columns should expand to fill available width."""

    columns_padding: tuple[int, int] = (0, 1)
    """Default padding for columns (vertical, horizontal)."""

    # Syntax highlighting settings
    syntax_theme: str = "monokai"
    """Default theme for syntax highlighting."""

    syntax_line_numbers: bool = False
    """Whether to show line numbers in syntax highlighting."""

    syntax_word_wrap: bool = False
    """Whether to enable word wrap in syntax highlighting."""

    syntax_background_color: str | None = None
    """Background color for syntax highlighting (None for default)."""

    # Markdown settings
    markdown_code_theme: str = "monokai"
    """Theme for code blocks in markdown."""

    markdown_hyperlinks: bool = True
    """Whether to enable hyperlinks in markdown."""

    markdown_inline_code_lexer: str | None = None
    """Lexer for inline code in markdown."""

    # JSON settings
    json_indent: int = 2
    """Default indentation for JSON display."""

    json_highlight: bool = True
    """Whether to enable syntax highlighting for JSON."""

    json_sort_keys: bool = False
    """Whether to sort keys in JSON display."""

    # Live display settings
    live_refresh_per_second: int = 4
    """Refresh rate for live displays (times per second)."""

    live_vertical_overflow: str = "ellipsis"
    """How to handle vertical overflow in live displays ('crop',
    'ellipsis', 'visible')."""

    live_auto_refresh: bool = True
    """Whether live displays should auto-refresh."""

    # Bar chart settings
    bar_chart_width: int = 20
    """Default width for bar chart bars."""

    bar_chart_character: str = "█"
    """Character to use for bar chart bars."""

    bar_chart_show_values: bool = True
    """Whether to show values in bar charts."""

    # Text and alignment settings
    text_justify: str = "left"
    """Default text justification ('left', 'center', 'right', 'full')."""

    text_overflow: str = "fold"
    """How to handle text overflow ('crop', 'fold', 'ellipsis')."""

    text_no_wrap: bool = False
    """Whether to disable text wrapping by default."""

    # Prompt settings
    prompt_show_default: bool = True
    """Whether to show default values in prompts."""

    prompt_show_choices: bool = True
    """Whether to show available choices in prompts."""

    # Inspection settings
    inspect_methods: bool = False
    """Whether to show methods in object inspection."""

    inspect_help: bool = False
    """Whether to show help text in object inspection."""

    inspect_private: bool = False
    """Whether to show private attributes in object inspection."""

    inspect_dunder: bool = False
    """Whether to show dunder methods in object inspection."""

    inspect_sort: bool = True
    """Whether to sort attributes in object inspection."""

    # Pretty printing settings
    pretty_indent_guides: bool = True
    """Whether to show indent guides in pretty printing."""

    pretty_max_length: int | None = None
    """Maximum length for pretty printing (None for no limit)."""

    pretty_max_string: int | None = None
    """Maximum string length in pretty printing (None for no limit)."""

    pretty_max_depth: int | None = None
    """Maximum depth for pretty printing (None for no limit)."""

    def __post_init__(self):
        """Validate settings after initialization."""
        # Existing validations
        if self.progress_refresh_per_second <= 0:
            raise ValueError("progress_refresh_per_second must be positive")

        if self.status_refresh_per_second <= 0:
            raise ValueError("status_refresh_per_second must be positive")

        if self.progress_speed_estimate_period <= 0:
            raise ValueError("progress_speed_estimate_period must be positive")

        if self.panel_box_style not in {
            "rounded",
            "square",
            "double",
            "heavy",
            "ascii",
        }:
            raise ValueError(
                f"Invalid panel_box_style: {self.panel_box_style}. "
                "Must be one of: rounded, square, double, heavy, ascii"
            )

        if self.rule_align not in {"left", "center", "right"}:
            raise ValueError(
                f"Invalid rule_align: {self.rule_align}. "
                "Must be one of: left, center, right"
            )

        if len(self.panel_padding) != 2:
            raise ValueError(
                "panel_padding must be a tuple of (vertical, horizontal)"
            )

        if any(p < 0 for p in self.panel_padding):
            raise ValueError("panel_padding values must be non-negative")

        # New validations for additional features
        if len(self.columns_padding) != 2:
            raise ValueError(
                "columns_padding must be a tuple of (vertical, horizontal)"
            )

        if any(p < 0 for p in self.columns_padding):
            raise ValueError("columns_padding values must be non-negative")

        if self.json_indent < 0:
            raise ValueError("json_indent must be non-negative")

        if self.live_refresh_per_second <= 0:
            raise ValueError("live_refresh_per_second must be positive")

        if self.live_vertical_overflow not in {"crop", "ellipsis", "visible"}:
            raise ValueError(
                f"Invalid live_vertical_overflow: "
                f"{self.live_vertical_overflow}. "
                "Must be one of: crop, ellipsis, visible"
            )

        if self.bar_chart_width <= 0:
            raise ValueError("bar_chart_width must be positive")

        if self.text_justify not in {"left", "center", "right", "full"}:
            raise ValueError(
                f"Invalid text_justify: {self.text_justify}. "
                "Must be one of: left, center, right, full"
            )

        if self.text_overflow not in {"crop", "fold", "ellipsis"}:
            raise ValueError(
                f"Invalid text_overflow: {self.text_overflow}. "
                "Must be one of: crop, fold, ellipsis"
            )
