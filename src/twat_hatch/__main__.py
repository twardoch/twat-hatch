#!/usr/bin/env -S uv run
# /// script
# dependencies = ["fire", "rich", "pydantic"]
# ///

"""Command-line interface for twat-hatch.

This module provides the main CLI interface for creating Python packages
and plugins using twat-hatch.
"""

import sys
from pathlib import Path
from typing import Optional, Sequence

import fire
from pydantic import ValidationError
from rich.console import Console
from rich.panel import Panel

from .core import PackageInitializer

console = Console()


def create_packages(initializer: PackageInitializer) -> None:
    """Create packages using the provided initializer.

    Args:
        initializer: Configured PackageInitializer instance
    """
    if not initializer.config:
        console.print("[red]No configuration provided[/]")
        return

    try:
        # Initialize plugin host first if specified
        if initializer.config.plugin_host:
            initializer.initialize_package(initializer.config.plugin_host)

        # Initialize all other packages
        for package in initializer.config.packages:
            if package != initializer.config.plugin_host:
                initializer.initialize_package(package)

    except Exception as e:
        console.print(f"[red]Error creating packages: {str(e)}[/]")


def show_usage_help() -> None:
    """Display usage help when no configuration is provided."""
    console.print(
        Panel(
            """[yellow]No configuration provided. Either:
- Provide a configuration file with --config
- Have twat-hatch.toml in the current directory
- Use --help for usage information[/]"""
        )
    )


def cli(
    config: str | None = None,
    out_dir: str | None = None,
) -> bool:
    """Initialize Python packages with optional plugin functionality.

    Creates packages based on configuration file. If a plugin host is specified,
    additional packages will be set up as plugins. Without a plugin host,
    packages are created as standalone packages.

    Args:
        config: Path to TOML configuration file
        out_dir: Output directory for created packages (overrides config)

    Returns:
        True if packages were created successfully, False otherwise
    """
    # Use default config if exists
    if not config and Path("twat-hatch.toml").exists():
        config = "twat-hatch.toml"

    if not config:
        show_usage_help()
        return False

    try:
        initializer = PackageInitializer(out_dir=out_dir, config_path=config)
        create_packages(initializer)
        return True
    except FileNotFoundError as e:
        console.print(f"[red]Configuration file not found: {str(e)}[/]")
    except ValidationError as e:
        console.print(f"[red]Invalid configuration:\n{str(e)}[/]")
    except Exception as e:
        console.print(f"[red]Failed to initialize packages: {str(e)}[/]")

    return False


if __name__ == "__main__":
    fire.Fire(cli)
