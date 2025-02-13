"""Core functionality for Python package initialization."""

import subprocess
from datetime import datetime
from importlib.resources import path
from pathlib import Path
from typing import Any, cast

import tomli
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pydantic import BaseModel, Field
from rich.console import Console

from .utils import PyVer

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
        # Add filters
        self.env.filters["split"] = lambda value, delimiter: value.split(delimiter)
        self.env.filters["strftime"] = lambda format: datetime.now().strftime(format)

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
            msg = f"Theme '{theme_name}' not found"
            raise FileNotFoundError(msg)

        for template_file in theme_dir.rglob("*.j2"):
            rel_path = template_file.relative_to(theme_dir)

            # Handle hidden prefix in file/directory names
            parts = list(rel_path.parts)
            for i, part in enumerate(parts):
                if part.startswith("hidden."):
                    parts[i] = part.replace("hidden.", ".")
                # Handle __package_name__ template in both files and directories
                elif "__package_name__" in part:
                    parts[i] = part.replace("__package_name__", context["import_name"])
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
    max_python: str | None = Field(
        None, description="Maximum Python version supported (optional)"
    )
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

    @property
    def python_version_info(self) -> dict[str, Any]:
        """Get Python version information in various formats needed by tools.

        Returns:
            Dictionary containing:
            - requires_python: Version specifier string for pyproject.toml
            - classifiers: List of Python version classifiers
            - ruff_target: Target version for ruff
            - mypy_version: Version for mypy config
        """
        min_ver = PyVer.parse(self.min_python) or PyVer(3, 10)
        max_ver = PyVer.parse(self.max_python) if self.max_python else None

        if max_ver and max_ver.major != min_ver.major:
            msg = f"Maximum Python version {max_ver} must have same major version as minimum {min_ver}"
            raise ValueError(msg)

        return {
            "requires_python": min_ver.requires_python(max_ver),
            "classifiers": PyVer.get_supported_versions(min_ver, max_ver),
            "ruff_target": min_ver.ruff_target,
            "mypy_version": min_ver.mypy_version,
        }

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
            msg = f"Missing config file: {config_file}"
            raise FileNotFoundError(msg)

        data = tomli.loads(config_file.read_text())

        # Extract sections
        project_data = data.get("project", {})
        author_data = data.get("author", {})
        package_data = data.get("package", {})
        dependencies_data = data.get("dependencies", {})
        development_data = data.get("development", {})
        tools_data = data.get("tools", {})
        features_data = data.get("features", {})

        # Parse Python versions
        min_ver = PyVer.parse(package_data.get("min_python")) or PyVer(3, 10)
        max_ver = (
            PyVer.parse(package_data.get("max_python"))
            if package_data.get("max_python")
            else None
        )

        # Combine all data into a single dict matching model structure
        config_dict = {
            "packages": project_data.get("packages", []),
            "plugin_host": project_data.get("plugin_host"),
            "output_dir": project_data.get("output_dir"),
            "author_name": author_data.get("name"),
            "author_email": author_data.get("email"),
            "github_username": author_data.get("github_username"),
            "min_python": str(min_ver),
            "max_python": str(max_ver) if max_ver else None,
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
        """Initialize Git repository in target directory with 'main' branch.

        Args:
            pkg_path: Directory to initialize repository in
        """
        try:
            subprocess.run(
                ["git", "init"],
                cwd=pkg_path,
                check=True,
                capture_output=True,
                text=True,
                shell=False,
            )
            # Rename default branch to 'main'
            subprocess.run(
                ["git", "branch", "-M", "main"],
                cwd=pkg_path,
                check=True,
                capture_output=True,
                text=True,
                shell=False,
            )
            console.print(f"[green]Initialized Git repo: {pkg_path} (branch: main)[/]")
        except (subprocess.CalledProcessError, FileNotFoundError) as err:
            console.print(f"[yellow]Git init failed: {err}[/]")

    def _create_github_repo(self, pkg_path: Path, repo_name: str) -> None:
        """Create and link GitHub repository using gh CLI.

        Args:
            pkg_path: Package directory path.
            repo_name: Repository name (local package import name)
        """
        owner = self.config.github_username  # Assumes non-empty if GitHub linking is desired
        full_repo = f"{owner}/{repo_name}"
        try:
            subprocess.run(
                [
                    "gh", "repo", "create", full_repo, "--public",
                    "--source", str(pkg_path), "--remote=origin", "--push"
                ],
                cwd=pkg_path,
                check=True,
                capture_output=True,
                text=True,
                shell=False,
            )
            console.print(f"[green]Linked GitHub repo: {full_repo}[/]")
        except subprocess.CalledProcessError as e:
            console.print(f"[yellow]GitHub repo creation failed: {e}[/]")

    def _create_version_file(self, pkg_path: Path, import_name: str) -> None:
        """Create empty __version__.py file in package source directory.

        Args:
            pkg_path: Base package directory
            import_name: Python import name for the package
        """
        version_file = pkg_path / "src" / import_name / "__version__.py"
        version_file.parent.mkdir(parents=True, exist_ok=True)
        version_file.touch()
        console.print(f"[green]Created version file: {version_file}[/]")

    def _get_context(self, name: str) -> dict[str, Any]:
        """Get template context for package.

        Args:
            name: Package name

        Returns:
            Template context dictionary
        """
        if not self.config:
            msg = "Configuration not loaded"
            raise RuntimeError(msg)

        # Convert package name to Python import name
        import_name = name.replace("-", "_")

        # For plugins, create a shorter import name by removing the plugin host prefix if present
        plugin_import_name = import_name
        if self.config.plugin_host:
            plugin_host_prefix = f"{self.config.plugin_host}_"
            if import_name.startswith(plugin_host_prefix):
                plugin_import_name = import_name[len(plugin_host_prefix) :]
            elif import_name.startswith(self.config.plugin_host):
                plugin_import_name = import_name[len(self.config.plugin_host) :]
                if plugin_import_name.startswith("-") or plugin_import_name.startswith(
                    "_"
                ):
                    plugin_import_name = plugin_import_name[1:]

        # Build template context
        context = {
            "name": name,
            "import_name": import_name,
            "plugin_import_name": plugin_import_name,
            "author_name": self.config.author_name,
            "author_email": self.config.author_email,
            "github_username": self.config.github_username,
            "min_python": self.config.min_python,
            "max_python": self.config.max_python,
            "license": self.config.license,
            "development_status": self.config.development_status,
            "dependencies": self.config.dependencies,
            "plugin_dependencies": self.config.plugin_dependencies,
            "dev_dependencies": self.config.dev_dependencies,
            "use_mkdocs": self.config.use_mkdocs,
            "use_vcs": self.config.use_vcs,
            "python_version_info": self.config.python_version_info,
        }

        # Add plugin host if specified
        if self.config.plugin_host:
            context["plugin_host"] = self.config.plugin_host

        return context

    def initialize_package(self, name: str) -> None:
        """Initialize a package with appropriate theme.

        Args:
            name: Name of package to create

        The theme selection logic works as follows:
        1. Always apply default theme first as the base
        2. Then apply one of:
           - If plugin_host is specified:
             * If this package is the plugin_host, apply plugin_host theme
             * Otherwise, apply plugin theme
           - Otherwise, apply package theme for regular packages
        3. Apply optional themes (e.g. mkdocs) if enabled
        """
        if not self.config:
            msg = "No configuration provided"
            raise ValueError(msg)

        context = self._get_context(name)
        pkg_path = self.out_dir / context["import_name"]

        # Create package source directory structure
        src_path = pkg_path / "src" / context["import_name"]
        src_path.mkdir(parents=True, exist_ok=True)

        # Always apply default theme first as the base
        self.template_engine.apply_theme("default", pkg_path, context)

        # Apply additional theme based on package role
        if self.config.plugin_host:
            if name == self.config.plugin_host:
                # This is the plugin host - apply plugin_host theme
                self.template_engine.apply_theme("plugin_host", pkg_path, context)
            else:
                # This is a plugin - apply plugin theme
                self.template_engine.apply_theme("plugin", pkg_path, context)
        else:
            # Regular package - apply package theme
            self.template_engine.apply_theme("package", pkg_path, context)

        # Apply optional themes
        if self.config.use_mkdocs:
            self.template_engine.apply_theme("mkdocs", pkg_path, context)

        # Create version file
        self._create_version_file(pkg_path, context["import_name"])

        # Initialize Git repository if requested
        if self.config.use_vcs:
            self._init_git_repo(pkg_path)
            # Add all files and make initial commit
            try:
                subprocess.run(
                    ["git", "add", "."],
                    cwd=pkg_path,
                    check=True,
                    capture_output=True,
                    text=True,
                    shell=False,
                )
                subprocess.run(
                    ["git", "commit", "-m", "Initial commit"],
                    cwd=pkg_path,
                    check=True,
                    capture_output=True,
                    text=True,
                    shell=False,
                )
                console.print(f"[green]Created initial commit in: {pkg_path}[/]")
            except (subprocess.CalledProcessError, FileNotFoundError) as err:
                console.print(f"[yellow]Git commit failed: {err}[/]")
            # Create and link GitHub repository if GitHub username is provided
            if self.config.github_username:
                self._create_github_repo(pkg_path, context["import_name"])

    def initialize_all(self) -> None:
        """Initialize all packages specified in config.

        The initialization order is:
        1. Initialize plugin_host first (if specified AND included in packages)
        2. Initialize all other packages
        """
        if not self.config:
            msg = "No configuration provided"
            raise ValueError(msg)

        # Initialize plugin host first if specified AND included in packages
        if self.config.plugin_host and self.config.plugin_host in self.config.packages:
            self.initialize_package(self.config.plugin_host)

        # Initialize all other packages
        for name in self.config.packages:
            if name != self.config.plugin_host:
                self.initialize_package(name)
