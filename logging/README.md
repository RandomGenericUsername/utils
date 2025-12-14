# Dotfiles Logging Module

Comprehensive logging module with Rich integration for the dotfiles project.

## Features

- 🎨 Rich console output with colors, tables, panels, and more
- 📝 Multiple log levels and formatters
- 📁 File logging with rotation support
- 🔧 Type-safe configuration
- 🎯 Clean, simple API

## Installation

This module is used as a path dependency within the dotfiles project:

```toml
[project]
dependencies = [
    "logging @ file://../../common/modules/logging",
]
```

## Usage

```python
from rich_logging import Log, LogLevels, ConsoleHandlers

# Create a logger
logger = Log.create_logger(
    "myapp",
    log_level=LogLevels.INFO,
    console_handler_type=ConsoleHandlers.RICH
)

# Use it
logger.info("Hello, world!")
logger.error("Something went wrong!")

# Rich features
logger.panel("Important Message", title="Alert", border_style="red")
logger.table(data, headers=["Name", "Value"])
```

## Documentation

See the `docs/` directory for comprehensive documentation:
- [Usage Guide](docs/usage-guide.md)
- [API Reference](docs/api-reference.md)
- [Architecture](docs/architecture.md)

## Development

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Format code
uv run black .
uv run isort .

# Type check
uv run mypy .
```

## License

MIT
