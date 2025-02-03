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
    name: str | None = None,
    author_name: str | None = None,
    author_email: str | None = None,
    github_username: str | None = None,
    min_python: str | None = None,
    max_python: str | None = None,
    license: str | None = None,
    development_status: str | None = None,
    use_mkdocs: bool | None = None,
    use_semver: bool | None = None,
    use_vcs: bool | None = None,
) -> None:
    """Initialize a new package configuration.

    Args:
        type: Type of package to create (package, plugin, plugin-host)
        output: Output file path
        name: Package name
        author_name: Author's name
        author_email: Author's email
        github_username: GitHub username
        min_python: Minimum Python version (e.g. "3.8")
        max_python: Maximum Python version (e.g. "3.12")
        license: Package license
        development_status: Development status
        use_mkdocs: Whether to use MkDocs for documentation
        use_semver: Whether to use semantic versioning
        use_vcs: Whether to initialize version control
    """
    try:
        # Determine if we have enough parameters to run non-interactively
        has_required_params = all(
            [
                name,
                author_name,
                author_email,
                github_username,
            ]
        )

        # Build kwargs for non-interactive mode
        kwargs = {}
        if has_required_params:
            kwargs.update(
                {
                    "name": name,
                    "author_name": author_name,
                    "author_email": author_email,
                    "github_username": github_username,
                }
            )
            if min_python:
                kwargs["min_python"] = min_python
            if max_python:
                kwargs["max_python"] = max_python
            if license:
                kwargs["license"] = license
            if development_status:
                kwargs["development_status"] = development_status
            if use_mkdocs is not None:
                kwargs["use_mkdocs"] = use_mkdocs
            if use_semver is not None:
                kwargs["use_semver"] = use_semver
            if use_vcs is not None:
                kwargs["use_vcs"] = use_vcs

        generator = ConfigurationGenerator()
        generator.write_config(
            type, output, interactive=not has_required_params, **kwargs
        )
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
