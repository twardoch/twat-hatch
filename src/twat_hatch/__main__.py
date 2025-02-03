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
from rich.ansi import AnsiDecoder
from rich.console import Console, Group
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.text import Text
from rich.theme import Theme
from rich.traceback import install

from .config import ConfigurationGenerator, PackageType
from .hatch import PackageInitializer
from .utils import PyVer

# Install rich traceback handler
install(show_locals=True)
ansi_decoder = AnsiDecoder()

# Set up console with theme
console = Console(theme=Theme({"prompt": "cyan", "question": "bold cyan"}))


class ConfigurationPrompts:
    """Interactive configuration prompts."""

    def get_package_name(self, package_type: PackageType) -> str:
        """Get package name from user.

        Args:
            package_type: Type of package being created

        Returns:
            Package name
        """
        default = "my-package"
        if package_type == "plugin":
            default = "my-plugin"
        elif package_type == "plugin-host":
            default = "my-plugin-host"

        return Prompt.ask(
            "[question]Package name[/]",
            default=default,
            show_default=True,
        )

    def get_plugin_host(self) -> str:
        """Get plugin host package name for plugins.

        Returns:
            Plugin host package name
        """
        return Prompt.ask(
            "[question]Plugin host package name[/]",
            default="my-plugin-host",
            show_default=True,
        )

    def get_author_info(self) -> dict[str, str]:
        """Get author information.

        Returns:
            Dictionary with author name, email, and GitHub username
        """
        return {
            "author_name": Prompt.ask(
                "[question]Author name[/]",
                default="Your Name",
                show_default=True,
            ),
            "author_email": Prompt.ask(
                "[question]Author email[/]",
                default="your.email@example.com",
                show_default=True,
            ),
            "github_username": Prompt.ask(
                "[question]GitHub username[/]",
                default="yourusername",
                show_default=True,
            ),
        }

    def get_python_versions(self) -> dict[str, str | None]:
        """Get Python version requirements.

        Returns:
            Dictionary with min_python and optional max_python
        """
        min_major = IntPrompt.ask(
            "[question]Minimum Python major version[/]",
            default=3,
            show_default=True,
        )
        min_minor = IntPrompt.ask(
            "[question]Minimum Python minor version[/]",
            default=10,
            show_default=True,
        )
        min_ver = PyVer(min_major, min_minor)

        if Confirm.ask(
            "[question]Specify maximum Python version?[/]",
            default=False,
            show_default=True,
        ):
            max_major = IntPrompt.ask(
                "[question]Maximum Python major version[/]",
                default=min_major,
                show_default=True,
            )
            max_minor = IntPrompt.ask(
                "[question]Maximum Python minor version[/]",
                default=12,
                show_default=True,
            )
            max_ver = PyVer(max_major, max_minor)
            max_python = str(max_ver)
        else:
            max_python = None

        return {
            "min_python": str(min_ver),
            "max_python": max_python,
        }

    def get_package_info(self) -> dict[str, Any]:
        """Get package information.

        Returns:
            Dictionary with license and development status
        """
        return {
            "license": Prompt.ask(
                "[question]License[/]",
                default="MIT",
                show_default=True,
            ),
            "development_status": Prompt.ask(
                "[question]Development status[/]",
                default="4 - Beta",
                show_default=True,
                choices=[
                    "1 - Planning",
                    "2 - Pre-Alpha",
                    "3 - Alpha",
                    "4 - Beta",
                    "5 - Production/Stable",
                    "6 - Mature",
                    "7 - Inactive",
                ],
            ),
        }

    def get_features(self) -> dict[str, bool]:
        """Get feature flags.

        Returns:
            Dictionary with feature flags
        """
        return {
            "use_mkdocs": Confirm.ask(
                "[question]Use MkDocs for documentation?[/]",
                default=False,
                show_default=True,
            ),
            "use_vcs": Confirm.ask(
                "[question]Initialize Git repository?[/]",
                default=True,
                show_default=True,
            ),
        }


def init(
    type: PackageType = "package",
    output: str = "twat-hatch.toml",
    name: str | None = None,
    author_name: str | None = None,
    author_email: str | None = None,
    github_username: str | None = None,
    min_python: str | tuple[int, int] | None = None,
    max_python: str | tuple[int, int] | None = None,
    license: str | None = None,
    development_status: str | None = None,
    use_mkdocs: bool | None = None,
    use_vcs: bool | None = None,
    plugin_host: str | None = None,
) -> None:
    """Initialize a new Python package or plugin.

    Args:
        type: Type of package to create ("package", "plugin", or "plugin-host")
        output: Output path for configuration file
        name: Package name
        author_name: Author's name
        author_email: Author's email
        github_username: GitHub username
        min_python: Minimum Python version as tuple (3,10) or string "3,10"
        max_python: Maximum Python version as tuple (3,12) or string "3,12"
        license: Package license
        development_status: Package development status
        use_mkdocs: Whether to use MkDocs for documentation
        use_vcs: Whether to use version control
        plugin_host: Host package name (for plugins only)

    Note:
        For Python versions, use comma-separated integers like "3,10" or (3,10).
        Do NOT use decimal notation like "3.10" as it will be incorrectly parsed.
    """
    try:
        # Parse Python versions using PyVer
        try:
            min_ver = PyVer.from_cli_input(min_python)
            max_ver = (
                PyVer.from_cli_input(max_python) if max_python is not None else None
            )
        except ValueError as e:
            console.print(f"[red]Error: {e}[/]")
            sys.exit(1)

        # Check if we should use interactive mode
        user_provided_values = {
            k: v
            for k, v in locals().items()
            if k
            in [
                "name",
                "author_name",
                "author_email",
                "github_username",
                "min_python",
                "max_python",
                "license",
                "development_status",
                "use_mkdocs",
                "use_vcs",
                "plugin_host",
            ]
            and v is not None
        }
        interactive = not bool(user_provided_values)

        # If in interactive mode, gather values from prompts
        if interactive:
            prompts = ConfigurationPrompts()
            name = prompts.get_package_name(type)
            if type == "plugin":
                plugin_host = prompts.get_plugin_host()
            author_info = prompts.get_author_info()
            author_name = author_info["author_name"]
            author_email = author_info["author_email"]
            github_username = author_info["github_username"]
            python_versions = prompts.get_python_versions()
            min_ver = PyVer.parse(python_versions["min_python"])
            max_ver = PyVer.parse(python_versions.get("max_python"))
            package_info = prompts.get_package_info()
            license = package_info["license"]
            development_status = package_info["development_status"]
            features = prompts.get_features()
            use_mkdocs = features["use_mkdocs"]
            use_vcs = features["use_vcs"]

        # Generate configuration
        config_generator = ConfigurationGenerator()
        config = config_generator.generate_config(
            package_type=type,
            interactive=False,  # We handle interactive mode here
            name=name,
            author_name=author_name,
            author_email=author_email,
            github_username=github_username,
            min_python=str(min_ver),
            max_python=str(max_ver) if max_ver else None,
            license=license,
            development_status=development_status,
            use_mkdocs=use_mkdocs,
            use_vcs=use_vcs,
            plugin_host=plugin_host,
        )

        # Write configuration to file
        output_path = Path(output)
        output_path.write_text(config)

        console.print(
            Panel(
                f"[green]Configuration written to {output_path}[/]\n"
                f"[yellow]Run `twat-hatch create` to create the package[/]"
            )
        )

    except ValidationError as e:
        console.print("[red]Error: Invalid configuration[/]")
        console.print(e)
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/]")
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

    def display(lines, out):
        console.print(Group(*map(ansi_decoder.decode_line, lines)))

    fire.core.Display = display

    fire.Fire(
        {
            "init": init,
            "config": config,
            "create": create,
        }
    )


if __name__ == "__main__":
    main()
