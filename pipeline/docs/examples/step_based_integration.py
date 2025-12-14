"""Example integration using PipelineStep classes."""

import logging
from pathlib import Path
from typing import Any

from src.modules.pipeline import (
    LogicOperator,
    ParallelConfig,
    Pipeline,
    PipelineConfig,
    PipelineContext,
    PipelineStep,
)


# Concrete step implementations
class PrintInstallationMessageStep(PipelineStep):
    """Step to print installation start message."""

    @property
    def step_id(self) -> str:
        return "print_installation_message"

    @property
    def description(self) -> str:
        return "Print installation start message"

    def run(self, context: PipelineContext) -> PipelineContext:
        """Print the installation message."""
        context.logger_instance.info("Starting installation...")
        context.results["message_printed"] = True
        return context


class BackupFilesStep(PipelineStep):
    """Step to backup existing files."""

    @property
    def step_id(self) -> str:
        return "backup_files"

    @property
    def description(self) -> str:
        return "Backup existing dotfiles"

    @property
    def timeout(self) -> float:
        return 60.0  # 1 minute timeout

    def run(self, context: PipelineContext) -> PipelineContext:
        """Backup existing files."""
        backup_directory: Path = context.app_config.install.backup_directory

        context.logger_instance.info(f"Backing up files to {backup_directory}")
        # Your backup logic here
        context.results["backup_completed"] = True
        context.results["backup_path"] = str(backup_directory)
        return context


class CopyDotfilesStep(PipelineStep):
    """Step to copy dotfiles to install directory."""

    @property
    def step_id(self) -> str:
        return "copy_dotfiles"

    @property
    def description(self) -> str:
        return "Copy dotfiles to install directory"

    def run(self, context: PipelineContext) -> PipelineContext:
        """Copy dotfiles to install directory."""
        install_directory: Path = context.app_config.install.directory

        context.logger_instance.info(
            f"Copying dotfiles to {install_directory}"
        )
        # Your copy logic here
        context.results["copy_completed"] = True
        context.results["files_copied"] = 42  # Example: number of files copied
        return context


class SetupSymlinksStep(PipelineStep):
    """Step to setup symbolic links."""

    @property
    def step_id(self) -> str:
        return "setup_symlinks"

    @property
    def description(self) -> str:
        return "Setup symbolic links"

    def run(self, context: PipelineContext) -> PipelineContext:
        """Setup symbolic links."""
        context.logger_instance.info("Setting up symbolic links")
        # Your symlink logic here
        context.results["symlinks_completed"] = True
        context.results["symlinks_created"] = 15  # Example: number of symlinks
        return context


class VerifyInstallationStep(PipelineStep):
    """Step to verify installation completed successfully."""

    @property
    def step_id(self) -> str:
        return "verify_installation"

    @property
    def description(self) -> str:
        return "Verify installation completed successfully"

    def run(self, context: PipelineContext) -> PipelineContext:
        """Verify installation completed successfully."""
        context.logger_instance.info("Verifying installation")

        # Check that required steps completed
        required_results = [
            "backup_completed",
            "copy_completed",
            "symlinks_completed",
        ]
        if all(context.results.get(key, False) for key in required_results):
            context.logger_instance.info("Installation verified successfully")
            context.results["verification_passed"] = True
        else:
            context.logger_instance.error("Installation verification failed")
            context.results["verification_passed"] = False
            raise RuntimeError("Installation verification failed")

        return context


def create_install_pipeline() -> Pipeline:
    """Create the installation pipeline using PipelineStep classes."""
    # Configure parallel execution
    parallel_config = ParallelConfig(
        operator=LogicOperator.AND,  # Both copy and symlinks must succeed
        max_workers=2,  # Limit to 2 concurrent operations
        timeout=30.0,  # 30 second timeout
    )

    # Configure pipeline
    pipeline_config = PipelineConfig(
        fail_fast=True,  # Stop on first failure
        parallel_config=parallel_config,
    )

    # Define pipeline steps
    steps: list[PipelineStep | list[PipelineStep]] = [
        PrintInstallationMessageStep(),  # Serial: print message first
        BackupFilesStep(),  # Serial: backup existing files
        [  # Parallel: copy and symlink simultaneously
            CopyDotfilesStep(),
            SetupSymlinksStep(),
        ],
        VerifyInstallationStep(),  # Serial: verify everything worked
    ]

    return Pipeline(steps, pipeline_config)


# Example usage in install command
def example_step_based_integration(
    logger: logging.Logger,
    app_config: Any,  # Should be AppConfig type
) -> Any:
    """Example of how to integrate pipeline with PipelineStep classes."""

    # Create context
    # Note: Paths are accessed via app_config.install.get_paths()
    context = PipelineContext(
        logger_instance=logger,
        app_config=app_config,
    )

    # Access installation paths dynamically from config
    # paths = context.app_config.install.get_paths()
    # dependencies_dir = paths.dependencies
    # scripts_dir = paths.scripts
    # config_dir = paths.config

    # Create and run pipeline
    pipeline = create_install_pipeline()
    final_context = pipeline.run(context)

    # Check results
    if final_context.errors:
        logger.error(f"Installation had {len(final_context.errors)} errors:")
        for error in final_context.errors:
            logger.error(f"  - {error}")

    if final_context.results.get("verification_passed", False):
        logger.info("Installation completed successfully!")
        logger.info(
            f"Files copied: {final_context.results.get('files_copied', 0)}"
        )
        logger.info(
            "Symlinks created: "
            f"{final_context.results.get('symlinks_created', 0)}"
        )
    else:
        logger.error("Installation failed verification")

    return final_context
