#!/usr/bin/env -S uv run
# /// script
# dependencies = ["fire", "rich", "pydantic", "jinja2", "tomli"]
# ///

"""Command-line interface for twat-hatch.

This module provides the main CLI interface for creating Python packages
and plugins using twat-hatch.
"""

import sys
from pathlib import Path
from typing import Any, Optional

import fire
from pydantic import ValidationError
from rich.console import Console
from rich.panel import Panel
from rich.traceback import install

from .config import ConfigurationGenerator, PackageType
from .hatch import PackageInitializer

# Install rich traceback handler
install(show_locals=True)

console = Console()


def init(
    type: PackageType = "package",
    output: str = "twat-hatch.toml",
    interactive: bool = True,
    **kwargs: Any,
) -> None:
    """Initialize a new package configuration.

    Args:
        type: Type of package to create (package, plugin, plugin-host)
        output: Output file path
        interactive: Whether to prompt for values interactively
        **kwargs: Optional pre-defined values
    """
    try:
        generator = ConfigurationGenerator()
        generator.write_config(type, output, interactive, **kwargs)
    except Exception as e:
        console.print(f"[red]Error creating configuration: {str(e)}[/]")
        sys.exit(1)


def config(command: str = "show", type: PackageType = "package") -> None:
    """Show example configuration for a package type.

    Args:
        command: Command to execute (show)
        type: Type of package to show config for
    """
    if command != "show":
        console.print("[red]Invalid command. Use 'show'.[/]")
        sys.exit(1)

    try:
        generator = ConfigurationGenerator()
        content = generator.generate_config(type, interactive=False)
        console.print(Panel(content, title=f"Example {type} configuration"))
    except Exception as e:
        console.print(f"[red]Error showing configuration: {str(e)}[/]")
        sys.exit(1)


def create(config_path: Optional[str] = None) -> None:
    """Create packages from configuration.

    Args:
        config_path: Path to configuration file (defaults to twat-hatch.toml)
    """
    if not config_path:
        config_path = "twat-hatch.toml"

    try:
        initializer = PackageInitializer(config_path=config_path)
        initializer.initialize_all()
    except Exception as e:
        console.print(f"[red]Error creating packages: {str(e)}[/]")
        sys.exit(1)


def main() -> None:
    """Main entry point."""
    fire.Fire(
        {
            "init": init,
            "config": config,
            "create": create,
        }
    )


if __name__ == "__main__":
    main()
