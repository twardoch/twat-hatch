"""Core functionality for Python package initialization."""

import subprocess
from importlib.resources import path
from pathlib import Path
from typing import Any, Callable, cast

import tomli
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pydantic import BaseModel, Field
from rich.console import Console

console = Console()


class TemplateEngine:
    """Jinja2-based template engine for package generation."""

    def __init__(self, themes_dir: Path) -> None:
        """Initialize template engine with themes directory.

        Args:
            themes_dir: Base directory containing theme templates
        """
        self.loader = FileSystemLoader(str(themes_dir))
        self.env = Environment(
            loader=self.loader,
            autoescape=select_autoescape(),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
        )

    def render_template(self, template_path: str, context: dict[str, Any]) -> str:
        """Render a template with given context.

        Args:
            template_path: Path to template file relative to themes directory
            context: Template variables

        Returns:
            Rendered template content

        Raises:
            jinja2.TemplateNotFound: If template doesn't exist
        """
        template = self.env.get_template(template_path)
        return template.render(**context)

    def apply_theme(
        self, theme_name: str, target_dir: Path, context: dict[str, Any]
    ) -> None:
        """Apply a theme to target directory.

        Args:
            theme_name: Name of theme to apply
            target_dir: Directory to write rendered files to
            context: Template variables
        """
        theme_dir = Path(cast(list[str], self.loader.searchpath)[0]) / theme_name
        if not theme_dir.exists():
            raise FileNotFoundError(f"Theme '{theme_name}' not found")

        for template_file in theme_dir.rglob("*.j2"):
            rel_path = template_file.relative_to(theme_dir)

            # Handle hidden prefix in file/directory names
            parts = list(rel_path.parts)
            for i, part in enumerate(parts):
                if part.startswith("hidden"):
                    parts[i] = "." + part[6:]  # Remove 'hidden' prefix and add '.'
            rel_path = Path(*parts)

            output_path = target_dir / rel_path.with_suffix("")

            # Create parent directories
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Render and write template
            content = self.render_template(
                f"{theme_name}/{template_file.relative_to(theme_dir)}", context
            )
            output_path.write_text(content, encoding="utf-8")
            console.print(f"Created: [cyan]{output_path}[/]")


class PackageConfig(BaseModel):
    """Stores configuration values for package generation."""

    # Package configuration
    packages: list[str] = Field(description="List of packages to initialize")
    plugin_host: str | None = Field(
        None, description="Optional plugin host package name"
    )
    output_dir: Path | None = Field(None, description="Where to create packages")

    # Package metadata
    author_name: str = Field(..., description="Name of the package author")
    author_email: str = Field(..., description="Email of the package author")
    github_username: str = Field(..., description="GitHub username")
    min_python: str = Field(..., description="Minimum Python version required")
    license: str = Field(..., description="Package license")
    development_status: str = Field(..., description="Package development status")

    # Dependencies
    dependencies: list[str] = Field(
        default_factory=list, description="Regular package dependencies"
    )
    plugin_dependencies: list[str] = Field(
        default_factory=list, description="Additional dependencies for plugins"
    )
    dev_dependencies: list[str] = Field(
        default_factory=list, description="Development dependencies"
    )

    # Tool configurations
    ruff_config: dict[str, Any] = Field(default_factory=dict)
    mypy_config: dict[str, Any] = Field(default_factory=dict)

    # Features
    use_mkdocs: bool = Field(
        default=False, description="Whether to use MkDocs for documentation"
    )
    use_semver: bool = Field(
        default=False, description="Whether to use semantic versioning"
    )
    use_vcs: bool = Field(
        default=False, description="Whether to initialize version control"
    )

    @classmethod
    def from_toml(cls, config_path: Path | str) -> "PackageConfig":
        """Create configuration from TOML file.

        Args:
            config_path: Path to configuration file

        Returns:
            Initialized PackageConfig instance

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValidationError: If required fields are missing or invalid
        """
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Missing config file: {config_file}")

        data = tomli.loads(config_file.read_text())

        # Extract sections
        project_data = data.get("project", {})
        author_data = data.get("author", {})
        package_data = data.get("package", {})
        dependencies_data = data.get("dependencies", {})
        development_data = data.get("development", {})
        tools_data = data.get("tools", {})
        features_data = data.get("features", {})

        # Combine all data into a single dict matching model structure
        config_dict = {
            "packages": project_data.get("packages", []),
            "plugin_host": project_data.get("plugin_host"),
            "output_dir": project_data.get("output_dir"),
            "author_name": author_data.get("name"),
            "author_email": author_data.get("email"),
            "github_username": author_data.get("github_username"),
            "min_python": package_data.get("min_python"),
            "license": package_data.get("license"),
            "development_status": package_data.get("development_status"),
            "dependencies": dependencies_data.get("dependencies", []),
            "plugin_dependencies": dependencies_data.get("plugin_dependencies", []),
            "dev_dependencies": development_data.get("additional_dependencies", []),
            "ruff_config": tools_data.get("ruff", {}),
            "mypy_config": tools_data.get("mypy", {}),
            "use_mkdocs": features_data.get("mkdocs", False),
            "use_semver": features_data.get("semver", False),
            "use_vcs": features_data.get("vcs", False),
        }

        return cls(**config_dict)


class PackageInitializer:
    """Manages creation of Python package structures."""

    def __init__(
        self,
        out_dir: str | Path | None = None,
        config_path: Path | str | None = None,
        base_dir: str | Path | None = None,
    ) -> None:
        """Initialize package generator with output directory and optional config.

        Args:
            out_dir: Base directory for generated packages
            config_path: Path to TOML configuration file
            base_dir: Base directory for resolving relative paths (defaults to cwd)
        """
        self.config: PackageConfig | None = None
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()

        if config_path:
            self.config = PackageConfig.from_toml(config_path)
            # If output_dir is specified in config and looks relative, make it relative to base_dir
            if self.config.output_dir:
                config_out_dir = Path(self.config.output_dir)
                if not config_out_dir.is_absolute():
                    out_dir = str(self.base_dir / config_out_dir)
                else:
                    out_dir = str(config_out_dir)

        self.out_dir = Path(out_dir) if out_dir else self.base_dir

        # Initialize template engine
        with path("twat_hatch.themes", "") as themes_dir:
            self.template_engine = TemplateEngine(Path(themes_dir))

    def _init_git_repo(self, pkg_path: Path) -> None:
        """Initialize Git repository in target directory.

        Args:
            pkg_path: Directory to initialize repository in
        """
        try:
            result = subprocess.run(
                ["git", "init"],
                cwd=pkg_path,
                check=True,
                capture_output=True,
                text=True,
            )
            console.print(f"[green]Initialized Git repo: {pkg_path}[/]")
        except (subprocess.CalledProcessError, FileNotFoundError) as err:
            console.print(f"[yellow]Git init failed: {err}[/]")

    def _get_context(self, name: str) -> dict[str, Any]:
        """Generate template context for package files.

        Args:
            name: Package name

        Returns:
            Dictionary of template context variables
        """
        import_name = name.replace("-", "_")
        is_plugin = bool(self.config and self.config.plugin_host)
        is_plugin_host = bool(
            self.config and self.config.plugin_host and name == self.config.plugin_host
        )

        context = {
            "name": name,
            "import_name": import_name,
            "title": f"{name} Package",
            "description": "Python package",
            "is_plugin": is_plugin,
            "is_plugin_host": is_plugin_host,
        }

        if is_plugin and self.config and self.config.plugin_host:
            context.update(
                {
                    "plugin_host": self.config.plugin_host,
                    "description": f"Plugin for {self.config.plugin_host}",
                }
            )

        if self.config:
            context.update(
                {
                    "author_name": self.config.author_name,
                    "author_email": self.config.author_email,
                    "github_username": self.config.github_username,
                    "min_python": self.config.min_python,
                    "license": self.config.license,
                    "development_status": self.config.development_status,
                    "dependencies": self.config.dependencies,
                    "plugin_dependencies": self.config.plugin_dependencies,
                    "dev_dependencies": self.config.dev_dependencies,
                    "ruff_config": self.config.ruff_config,
                    "mypy_config": self.config.mypy_config,
                    "use_mkdocs": self.config.use_mkdocs,
                    "use_semver": self.config.use_semver,
                    "use_vcs": self.config.use_vcs,
                }
            )

        return context

    def initialize_package(self, name: str) -> None:
        """Initialize a package with appropriate theme.

        Args:
            name: Name of package to create

        The theme selection logic works as follows:
        1. If no plugin_host is specified, use default theme
        2. If plugin_host is specified:
           - If this package is the plugin_host, use plugin_host theme
           - Otherwise, use plugin theme
        """
        if not self.config:
            raise ValueError("No configuration provided")

        pkg_path = self.out_dir / name
        context = self._get_context(name)

        # Always apply default theme first
        self.template_engine.apply_theme("default", pkg_path, context)

        # Apply additional theme based on package role
        if self.config.plugin_host:
            if name == self.config.plugin_host:
                # This is the plugin host - apply plugin_host theme
                self.template_engine.apply_theme("plugin_host", pkg_path, context)
            else:
                # This is a plugin - apply plugin theme
                self.template_engine.apply_theme("plugin", pkg_path, context)

        # Apply optional themes
        if self.config.use_mkdocs:
            self.template_engine.apply_theme("mkdocs", pkg_path, context)

        # Initialize Git repository if requested
        if self.config.use_vcs:
            self._init_git_repo(pkg_path)

    def initialize_all(self) -> None:
        """Initialize all packages specified in config.

        The initialization order is:
        1. Initialize plugin_host first (if specified)
        2. Initialize all other packages
        """
        if not self.config:
            raise ValueError("No configuration provided")

        # Initialize plugin host first if specified
        if self.config.plugin_host:
            self.initialize_package(self.config.plugin_host)

        # Initialize all other packages
        for name in self.config.packages:
            if name != self.config.plugin_host:
                self.initialize_package(name)
