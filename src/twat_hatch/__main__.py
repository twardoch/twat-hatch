# this_file: src/twat_hatch/__main__.py
"""Fire CLI entry point for twat-hatch."""

from __future__ import annotations

import sys
from typing import Any

import fire


def _version() -> str:
    """Print the twat-hatch package version."""
    from twat_hatch.__version__ import __version__

    return __version__


def _init(
    package_type: str = "package",
    output: str = "twat-hatch.toml",
    name: str | None = None,
    author_name: str | None = None,
    author_email: str | None = None,
    github_username: str | None = None,
    min_python: str | None = None,
    max_python: str | None = None,
    license_str: str | None = None,
    development_status: str | None = None,
    use_mkdocs: bool | None = None,
    use_vcs: bool | None = None,
    plugin_host: str | None = None,
) -> None:
    """Initialize a new Python package configuration file.

    Writes a twat-hatch.toml. Runs interactively when no options given;
    non-interactive when options are supplied.

    Args:
        package_type: 'package', 'plugin', or 'plugin-host'.
        output: Output path for the configuration file.
        name: Package name.
        author_name: Author's full name.
        author_email: Author's email address.
        github_username: GitHub username.
        min_python: Minimum Python version as 'MAJOR,MINOR' e.g. '3,10'.
        max_python: Maximum Python version as 'MAJOR,MINOR' e.g. '3,12'.
        license_str: Package license (e.g. 'MIT').
        development_status: PyPI development status classifier.
        use_mkdocs: Whether to use MkDocs for documentation.
        use_vcs: Whether to initialize a Git repository.
        plugin_host: Host package name (for plugin packages only).
    """
    from pathlib import Path

    from pydantic import ValidationError
    from rich.ansi import AnsiDecoder
    from rich.console import Console, Group
    from rich.panel import Panel
    from rich.prompt import Confirm, IntPrompt, Prompt
    from rich.theme import Theme

    from twat_hatch.config import ConfigurationGenerator
    from twat_hatch.utils import PyVer

    console = Console(theme=Theme({"prompt": "cyan", "question": "bold cyan"}))

    try:
        try:
            min_ver = PyVer.from_cli_input(min_python)
            max_ver = PyVer.from_cli_input(max_python) if max_python is not None else None
        except ValueError as e:
            console.print(f"[red]Error: {e}[/]")
            sys.exit(1)

        user_provided = {
            k: v
            for k, v in {
                "name": name,
                "author_name": author_name,
                "author_email": author_email,
                "github_username": github_username,
                "min_python": min_python,
                "max_python": max_python,
                "license_str": license_str,
                "development_status": development_status,
                "use_mkdocs": use_mkdocs,
                "use_vcs": use_vcs,
                "plugin_host": plugin_host,
            }.items()
            if v is not None
        }
        interactive = not bool(user_provided)

        license_val: str | None = license_str

        if interactive:
            name = Prompt.ask(
                "[question]Package name[/]",
                default="my-package" if package_type == "package" else "my-plugin",
                show_default=True,
            )
            if package_type == "plugin":
                plugin_host = Prompt.ask(
                    "[question]Plugin host package name[/]",
                    default="my-plugin-host",
                    show_default=True,
                )
            author_name = Prompt.ask("[question]Author name[/]", default="Your Name", show_default=True)
            author_email = Prompt.ask("[question]Author email[/]", default="your.email@example.com", show_default=True)
            github_username = Prompt.ask("[question]GitHub username[/]", default="yourusername", show_default=True)
            min_major = IntPrompt.ask("[question]Minimum Python major version[/]", default=3, show_default=True)
            min_minor = IntPrompt.ask("[question]Minimum Python minor version[/]", default=10, show_default=True)
            min_ver = PyVer(min_major, min_minor)
            max_ver = None
            if Confirm.ask("[question]Specify maximum Python version?[/]", default=False, show_default=True):
                max_major = IntPrompt.ask(
                    "[question]Maximum Python major version[/]", default=min_major, show_default=True
                )
                max_minor = IntPrompt.ask("[question]Maximum Python minor version[/]", default=12, show_default=True)
                max_ver = PyVer(max_major, max_minor)
            license_val = Prompt.ask("[question]License[/]", default="MIT", show_default=True)
            development_status = Prompt.ask(
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
            )
            use_mkdocs = Confirm.ask("[question]Use MkDocs for documentation?[/]", default=False, show_default=True)
            use_vcs = Confirm.ask("[question]Initialize Git repository?[/]", default=True, show_default=True)

        config_generator = ConfigurationGenerator()
        config = config_generator.generate_config(
            package_type=package_type,
            name=name,
            author_name=author_name,
            author_email=author_email,
            github_username=github_username,
            min_python=str(min_ver),
            max_python=str(max_ver) if max_ver else None,
            license=license_val,
            development_status=development_status,
            use_mkdocs=use_mkdocs,
            use_vcs=use_vcs,
            plugin_host=plugin_host,
        )

        output_path = Path(output)
        output_path.write_text(config)
        console.print(
            Panel(
                f"[green]Configuration written to {output_path}[/]\n"
                "[yellow]Run `twat-hatch create` to create the package[/]"
            )
        )

    except ValidationError as e:
        console.print("[red]Error: Invalid configuration[/]")
        console.print(e)
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/]")
        sys.exit(1)


def _plugin_init(
    output: str = "twat-hatch.toml",
    name: str | None = None,
    plugin_host: str | None = None,
    author_name: str | None = None,
    author_email: str | None = None,
    github_username: str | None = None,
    min_python: str | None = None,
    max_python: str | None = None,
    license_str: str | None = None,
    development_status: str | None = None,
    use_mkdocs: bool | None = None,
    use_vcs: bool | None = None,
) -> None:
    """Initialize a new plugin package configuration (shorthand for init --package-type plugin).

    Args:
        output: Output path for the configuration file.
        name: Package name.
        plugin_host: Host package name.
        author_name: Author's full name.
        author_email: Author's email address.
        github_username: GitHub username.
        min_python: Minimum Python version as 'MAJOR,MINOR' e.g. '3,10'.
        max_python: Maximum Python version as 'MAJOR,MINOR' e.g. '3,12'.
        license_str: Package license (e.g. 'MIT').
        development_status: PyPI development status classifier.
        use_mkdocs: Whether to use MkDocs for documentation.
        use_vcs: Whether to initialize a Git repository.
    """
    _init(
        package_type="plugin",
        output=output,
        name=name,
        author_name=author_name,
        author_email=author_email,
        github_username=github_username,
        min_python=min_python,
        max_python=max_python,
        license_str=license_str,
        development_status=development_status,
        use_mkdocs=use_mkdocs,
        use_vcs=use_vcs,
        plugin_host=plugin_host,
    )


def _create(config_path: str | None = None) -> None:
    """Create packages from a twat-hatch.toml configuration file.

    Args:
        config_path: Path to configuration file (defaults to twat-hatch.toml).
    """
    from rich.console import Console

    console = Console()
    if not config_path:
        config_path = "twat-hatch.toml"
    try:
        from twat_hatch.hatch import PackageInitializer

        initializer = PackageInitializer(config_path=config_path)
        initializer.initialize_all()
    except Exception as e:
        console.print(f"[red]Error creating packages: {e!s}[/]")
        sys.exit(1)


def _config(command: str = "show", package_type: str = "package") -> None:
    """Show example configuration for a package type.

    Args:
        command: Command to execute ('show').
        package_type: Type of package to show config for ('package', 'plugin', 'plugin-host').
    """
    from rich.console import Console
    from rich.panel import Panel

    console = Console()
    if command != "show":
        console.print("[red]Invalid command. Use 'show'.[/]")
        sys.exit(1)
    try:
        from twat_hatch.config import ConfigurationGenerator

        generator = ConfigurationGenerator()
        content = generator.generate_config(package_type)
        console.print(Panel(content, title=f"Example {package_type} configuration"))
    except Exception as e:
        console.print(f"[red]Error showing configuration: {e!s}[/]")
        sys.exit(1)


# Explicit allow-list — only expose implemented behaviour
COMMANDS: dict[str, object] = {
    "version": _version,
    "init": _init,
    "plugin-init": _plugin_init,
    "create": _create,
    "config": _config,
}


def main() -> None:
    """Main entry point for twat-hatch."""
    fire.Fire(COMMANDS, name="twat-hatch")


# Per-leaf dashed-entry helpers (one per leaf)
def cmd_version() -> None:
    """Entry point for twat-hatch-version."""
    fire.Fire(_version, name="twat-hatch-version")


def cmd_init() -> None:
    """Entry point for twat-hatch-init."""
    fire.Fire(_init, name="twat-hatch-init")


def cmd_plugin_init() -> None:
    """Entry point for twat-hatch-plugin-init."""
    fire.Fire(_plugin_init, name="twat-hatch-plugin-init")


def cmd_create() -> None:
    """Entry point for twat-hatch-create."""
    fire.Fire(_create, name="twat-hatch-create")


def cmd_config() -> None:
    """Entry point for twat-hatch-config."""
    fire.Fire(_config, name="twat-hatch-config")


if __name__ == "__main__":
    main()
