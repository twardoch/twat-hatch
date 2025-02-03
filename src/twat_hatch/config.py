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
        template_path="package.toml.j2",
    ),
    "plugin": PackageTemplate(
        type="plugin",
        description="Plugin package for a plugin host",
        template_path="plugin.toml.j2",
    ),
    "plugin-host": PackageTemplate(
        type="plugin-host",
        description="Plugin host package that can load plugins",
        template_path="plugin_host.toml.j2",
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
            self.loader = FileSystemLoader(str(themes_dir), followlinks=True)
            self.env = Environment(
                loader=self.loader,
                autoescape=select_autoescape(),
                trim_blocks=True,
                lstrip_blocks=True,
                keep_trailing_newline=True,
                auto_reload=True,
            )
        self.prompts = ConfigurationPrompts()

    def _get_python_version_info(
        self, min_python: str | None = None, max_python: str | None = None
    ) -> dict[str, Any]:
        """Get Python version information in various formats needed by tools.

        Args:
            min_python: Minimum Python version (e.g. "3.8")
            max_python: Maximum Python version (e.g. "3.12") or None

        Returns:
            Dictionary with Python version information
        """
        # Use default min_python if not provided
        min_python = min_python if min_python is not None else "3.8"

        # Extract major.minor from min_python (e.g. "3.8" from "3.8")
        min_ver = min_python.split(".")
        min_major, min_minor = int(min_ver[0]), int(min_ver[1])

        # Default max version is current latest Python
        current_max = 12  # Update this as new Python versions are released

        # If max_python is specified, use it instead
        if max_python:
            max_ver = max_python.split(".")
            max_major, max_minor = int(max_ver[0]), int(max_ver[1])
            if max_major != min_major:
                raise ValueError(
                    f"Maximum Python version {max_python} must have same major version as minimum {min_python}"
                )
            current_max = max_minor

        # Generate supported version classifiers
        classifiers = []
        for i in range(min_minor, current_max + 1):
            classifiers.append(f"Programming Language :: Python :: {min_major}.{i}")

        # Build requires-python string
        requires = f">={min_python}"
        if max_python:
            requires += f",<{max_python}.999"

        return {
            "requires_python": requires,
            "classifiers": classifiers,
            "ruff_target": f"py{min_major}{min_minor}",
            "black_target": [f"py{min_major}{min_minor}"],
            "mypy_version": min_python,
        }

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

            # Get Python versions and version info
            python_versions = self.prompts.get_python_versions()
            min_python = python_versions["min_python"]
            max_python = python_versions.get("max_python")
            context.update(python_versions)
            context["python_version_info"] = self._get_python_version_info(
                min_python,
                max_python,
            )

            # Get package information
            context.update(self.prompts.get_package_info())

            # Get feature flags
            context.update(self.prompts.get_features())
        else:
            context.update(kwargs)
            if "python_version_info" not in context:
                # Get min_python with a default value
                min_python_val = context.get("min_python", "3.10")
                min_python = str(min_python_val)
                max_python = context.get("max_python")
                context["python_version_info"] = self._get_python_version_info(
                    min_python,
                    max_python,
                )

            # Set default values for missing fields
            if "name" not in context:
                context["name"] = "my-package"
            if package_type == "plugin" and "plugin_host" not in context:
                context["plugin_host"] = "my-plugin-host"
            if "min_python" not in context:
                context["min_python"] = "3.10"
            if "license" not in context:
                context["license"] = "MIT"
            if "development_status" not in context:
                context["development_status"] = "4 - Beta"
            if "use_mkdocs" not in context:
                context["use_mkdocs"] = False
            if "use_semver" not in context:
                context["use_semver"] = True
            if "use_vcs" not in context:
                context["use_vcs"] = True
            if "dependencies" not in context:
                context["dependencies"] = []
            if "dev_dependencies" not in context:
                context["dev_dependencies"] = []
            if "plugin_dependencies" not in context:
                context["plugin_dependencies"] = []

        # Print debug information
        console.print(f"[yellow]Template path: {template.template_path}[/]")
        console.print(f"[yellow]Context: {context}[/]")

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
