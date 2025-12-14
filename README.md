# Core Libraries

A uv workspace containing core shared libraries.

## Workspace Structure

This is a uv workspace containing multiple Python projects:

```
dotfiles-core/
├── pyproject.toml          # Workspace configuration
├── uv.lock                 # Unified lock file for all projects
├── .venv/                  # Shared virtual environment
├── logging/                # Rich logging module
│   ├── pyproject.toml
│   └── src/rich_logging/
└── pipeline/               # Task pipeline framework
    ├── pyproject.toml
    └── src/task_pipeline/
```

## Projects

### rich-logging
Comprehensive logging module with Rich integration.

### task-pipeline
Flexible pipeline execution framework with serial and parallel task support.

## Usage

### Installing the workspace

From the `dotfiles-core` directory:

```bash
# Install all workspace members and dev dependencies
uv sync

# Install without dev dependencies
uv sync --no-dev
```

### Running commands

```bash
# Run Python with access to all workspace packages
uv run python

# Run tests for all projects
uv run pytest

# Run tests for a specific project
uv run pytest logging/tests
uv run pytest pipeline/tests

# Format code
uv run black .
uv run isort .

# Type check
uv run mypy logging/src pipeline/src

# Lint
uv run ruff check .
```

### Adding new workspace members

1. Create a new project directory with its own `pyproject.toml`
2. Add the project to the workspace members in the root `pyproject.toml`:
   ```toml
   [tool.uv.workspace]
   members = ["logging", "pipeline", "new-project"]
   ```
3. If the new project depends on other workspace members, use workspace references:
   ```toml
   [tool.uv.sources]
   rich-logging = { workspace = true }
   ```
4. Run `uv sync` to update the workspace

## Development

All development dependencies are managed at the workspace level and shared across all projects.

### Pre-commit hooks

```bash
uv run pre-commit install
uv run pre-commit run --all-files
```

## Benefits of the Workspace

- **Single virtual environment**: All projects share the same `.venv`
- **Unified dependency management**: One `uv.lock` file for consistent versions
- **Easy cross-project development**: Changes in one project are immediately available to others
- **Shared dev dependencies**: No need to duplicate dev tools in each project
- **Simplified CI/CD**: Single sync command installs everything

