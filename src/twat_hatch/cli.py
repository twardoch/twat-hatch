#!/usr/bin/env -S uv run
# /// script
# dependencies = ["fire>=0.5.0", "rich>=13.7.0", "tomli>=2.0.0"]
# ///

"""Command-line interface for twat-hatch."""

import sys
from pathlib import Path
from typing import Optional, Sequence

import fire
from rich.console import Console
from rich.panel import Panel

from .core import PackageInitializer

console = Console()


def main(
    *packages: str,
    core: Optional[str] = None,
    out_dir: Optional[str] = None,
    config: Optional[str] = None,
) -> None:
    """Initialize Python packages for a plugin system.

    Creates a core package if --core is provided, and plugin packages thereafter.
    Can be configured via CLI arguments or a TOML configuration file.

    Args:
        packages: Names of the plugin packages to create.
        core: Name of the core package.
        out_dir: Output directory for created packages.
        config: Path to TOML configuration file.
    """
    initializer = PackageInitializer(out_dir=out_dir, config_path=config)

    # If config file is provided, use its values unless overridden by CLI
    if config and initializer.config:
        if not core:
            core = initializer.config.core_package
        if not packages:
            packages = tuple(initializer.config.plugins)

    if core:
        initializer.init_core_package(core)

    for package in packages:
        if not core:
            console.print(
                "[red]Error: --core parameter is required when creating plugins[/]"
            )
            sys.exit(1)
        initializer.init_plugin_package(package, core)

    if not packages and not core:
        console.print(
            Panel(
                """[yellow]No packages specified. Either:
- Provide package names and --core via CLI
- Provide a configuration file with --config
- Use --help for usage information[/]"""
            )
        )
        sys.exit(1)


if __name__ == "__main__":
    fire.Fire(main)
