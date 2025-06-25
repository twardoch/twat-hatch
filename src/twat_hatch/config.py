#!/usr/bin/env python3
"""Configuration generation and management for twat-hatch."""

from __future__ import annotations

from dataclasses import dataclass
from importlib.resources import path
from pathlib import Path
from typing import Any, Literal

from jinja2 import Environment, FileSystemLoader, select_autoescape

from twat_hatch.utils import PyVer

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
            # Add the split filter
            self.env.filters["split"] = lambda value, delimiter: value.split(delimiter)

    def generate_config(  # noqa: C901
        self,
        package_type: PackageType,
        **kwargs: Any,
    ) -> str:
        """Generate configuration content.

        Args:
            package_type: Type of package to create
            **kwargs: Configuration values to use

        Returns:
            Configuration content as string
        """
        # Get template
        template = PACKAGE_TEMPLATES[package_type]

        # Initialize context with provided values
        context = kwargs.copy()

        # Set default values for missing fields
        if not context.get("name"):
            context["name"] = "my-package"
        if package_type == "plugin" and not context.get("plugin_host"):
            context["plugin_host"] = "my-plugin-host"

        # Set author defaults if not provided
        if not context.get("author_name"):
            context["author_name"] = "AUTHOR_NAME"
        if not context.get("author_email"):
            context["author_email"] = "author@example.com"
        if not context.get("github_username"):
            context["github_username"] = "github_username"

        # Set standard defaults
        if not context.get("license"):
            context["license"] = "MIT"
        if not context.get("development_status"):
            context["development_status"] = "4 - Beta"
        context["use_mkdocs"] = bool(context.get("use_mkdocs", False))
        context["use_vcs"] = bool(context.get("use_vcs", True))
        if "dependencies" not in context:
            context["dependencies"] = []
        if "dev_dependencies" not in context:
            context["dev_dependencies"] = []
        if "plugin_dependencies" not in context:
            context["plugin_dependencies"] = []

        # Parse Python versions
        min_ver = PyVer.parse(context.get("min_python")) or PyVer(3, 10)
        max_ver = (
            PyVer.parse(context.get("max_python"))
            if context.get("max_python")
            else None
        )

        # Update context with version info
        context["min_python"] = str(min_ver)
        context["max_python"] = str(max_ver) if max_ver else None
        context["python_version_info"] = {
            "requires_python": min_ver.requires_python(max_ver),
            "classifiers": PyVer.get_supported_versions(min_ver, max_ver),
            "ruff_target": min_ver.ruff_target,
            "mypy_version": min_ver.mypy_version,
        }

        # Render template
        template_obj = self.env.get_template(template.template_path)
        return template_obj.render(**context)

    def write_config(
        self,
        package_type: PackageType,
        output_path: Path | str,
        **kwargs: Any,
    ) -> None:
        """Generate and write configuration file.

        Args:
            package_type: Type of package to generate config for
            output_path: Where to write the configuration file
            **kwargs: Optional pre-defined values
        """
        content = self.generate_config(package_type, **kwargs)
        output_file = Path(output_path)
        output_file.write_text(content)
