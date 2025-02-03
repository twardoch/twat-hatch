#!/usr/bin/env python3
"""Configuration generation and management for twat-hatch."""

from dataclasses import dataclass
from importlib.resources import path
from pathlib import Path
from typing import Any, Literal

from jinja2 import Environment, FileSystemLoader, select_autoescape
from pydantic import BaseModel, Field
from rich.console import Console
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.theme import Theme

console = Console(theme=Theme({"prompt": "cyan", "question": "bold cyan"}))

PackageType = Literal["package", "plugin", "plugin-host"]


@dataclass
class PackageTemplate:
    """Package template information."""

    type: PackageType
    description: str
    template_path: str


PACKAGE_TEMPLATES = {
    "package": PackageTemplate(
        type="package",
        description="Standalone Python package",
        template_path="package/package.toml.j2",
    ),
    "plugin": PackageTemplate(
        type="plugin",
        description="Plugin package for a plugin host",
        template_path="plugin/plugin.toml.j2",
    ),
    "plugin-host": PackageTemplate(
        type="plugin-host",
        description="Plugin host package that can load plugins",
        template_path="plugin_host/plugin_host.toml.j2",
    ),
}


class ConfigurationPrompts:
    """Interactive configuration prompts."""

    def __init__(self) -> None:
        """Initialize prompts."""
        self.console = Console()

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
            default=8,
            show_default=True,
        )
        min_python = f"{min_major}.{min_minor}"

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
            max_python = f"{max_major}.{max_minor}"
        else:
            max_python = None

        return {"min_python": min_python, "max_python": max_python}

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
            "use_semver": Confirm.ask(
                "[question]Use semantic versioning?[/]",
                default=True,
                show_default=True,
            ),
            "use_vcs": Confirm.ask(
                "[question]Initialize Git repository?[/]",
                default=True,
                show_default=True,
            ),
        }


class ConfigurationGenerator:
    """Generates package configuration files."""

    def __init__(self) -> None:
        """Initialize generator with template engine."""
        with path("twat_hatch.themes", "") as themes_dir:
            self.loader = FileSystemLoader(str(themes_dir))
            self.env = Environment(
                loader=self.loader,
                autoescape=select_autoescape(),
                trim_blocks=True,
                lstrip_blocks=True,
                keep_trailing_newline=True,
            )
        self.prompts = ConfigurationPrompts()

    def generate_config(
        self,
        package_type: PackageType,
        interactive: bool = True,
        **kwargs: Any,
    ) -> str:
        """Generate configuration file content.

        Args:
            package_type: Type of package to generate config for
            interactive: Whether to prompt for values interactively
            **kwargs: Optional pre-defined values

        Returns:
            Generated configuration file content
        """
        template = PACKAGE_TEMPLATES[package_type]
        context = {}

        if interactive:
            # Get package name
            context["name"] = self.prompts.get_package_name(package_type)

            # Get plugin host for plugins
            if package_type == "plugin":
                context["plugin_host"] = self.prompts.get_plugin_host()

            # Get author information
            context.update(self.prompts.get_author_info())

            # Get Python versions
            context.update(self.prompts.get_python_versions())

            # Get package information
            context.update(self.prompts.get_package_info())

            # Get feature flags
            context.update(self.prompts.get_features())
        else:
            context.update(kwargs)

        # Render template
        template_obj = self.env.get_template(template.template_path)
        return template_obj.render(**context)

    def write_config(
        self,
        package_type: PackageType,
        output_path: Path | str,
        interactive: bool = True,
        **kwargs: Any,
    ) -> None:
        """Generate and write configuration file.

        Args:
            package_type: Type of package to generate config for
            output_path: Where to write the configuration file
            interactive: Whether to prompt for values interactively
            **kwargs: Optional pre-defined values
        """
        content = self.generate_config(package_type, interactive, **kwargs)
        output_file = Path(output_path)
        output_file.write_text(content)
        console.print(f"[green]Created configuration file: {output_file}[/]")
