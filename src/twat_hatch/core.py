"""Core functionality for Python package initialization."""

import subprocess
from dataclasses import dataclass
from importlib.resources import path
from pathlib import Path
from typing import Any, Callable

import tomli
from rich.console import Console

console = Console()


@dataclass
class PackageTemplate:
    """Represents a collection of template files for package generation."""

    theme_path: Path

    @classmethod
    def from_theme(cls, theme_name: str = "default") -> "PackageTemplate":
        """Load template files from a named theme directory.

        Args:
            theme_name: Name of theme directory to load

        Returns:
            Initialized PackageTemplate with theme files

        Raises:
            FileNotFoundError: If theme directory doesn't exist
        """
        with path("twat_hatch.themes", theme_name) as theme_path:
            if not theme_path.exists():
                raise FileNotFoundError(f"Theme '{theme_name}' not found")
            return cls(theme_path=Path(theme_path))


@dataclass
class PackageConfig:
    """Stores configuration values for package generation."""

    core_package: str | None
    plugins: list[str]
    output_dir: str | Path | None
    author_name: str
    author_email: str
    github_username: str
    min_python: str
    license: str
    development_status: str
    core_dependencies: list[str]
    plugin_dependencies: list[str]
    dev_dependencies: list[str]
    ruff_config: dict[str, Any]
    mypy_config: dict[str, Any]
    theme_name: str
    use_mkdocs: bool = False
    use_semver: bool = False
    use_vcs: bool = False

    @classmethod
    def from_toml(cls, config_path: Path | str) -> "PackageConfig":
        """Create configuration from TOML file.

        Args:
            config_path: Path to configuration file

        Returns:
            Initialized PackageConfig instance

        Raises:
            FileNotFoundError: If config file doesn't exist
            KeyError: If required fields are missing
        """
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Missing config file: {config_file}")

        data = tomli.loads(config_file.read_text())
        return cls(
            core_package=data["project"].get("core_package"),
            plugins=data["project"].get("plugins", []),
            output_dir=data["project"].get("output_dir"),
            author_name=data["author"]["name"],
            author_email=data["author"]["email"],
            github_username=data["author"]["github_username"],
            min_python=data["package"]["min_python"],
            license=data["package"]["license"],
            development_status=data["package"]["development_status"],
            core_dependencies=data["dependencies"].get("core", []),
            plugin_dependencies=data["dependencies"].get("plugins", []),
            dev_dependencies=data["development"].get("additional_dependencies", []),
            ruff_config=data["tools"].get("ruff", {}),
            mypy_config=data["tools"].get("mypy", {}),
            theme_name=data["theme"].get("name", "default"),
            use_mkdocs=data["features"].get("mkdocs", False),
            use_semver=data["features"].get("semver", False),
            use_vcs=data["features"].get("vcs", False),
        )


class PackageInitializer:
    """Manages creation of Python package structures."""

    def __init__(
        self, out_dir: str | Path | None = None, config_path: Path | str | None = None
    ) -> None:
        """Initialize package generator with output directory and optional config.

        Args:
            out_dir: Base directory for generated packages
            config_path: Path to TOML configuration file
        """
        self.config: PackageConfig | None = None
        if config_path:
            self.config = PackageConfig.from_toml(config_path)
            out_dir = self.config.output_dir or out_dir

        self.out_dir = Path(out_dir) if out_dir else Path.cwd()
        theme_name = self.config.theme_name if self.config else "default"
        self.template = PackageTemplate.from_theme(theme_name)

    def _create_test_file(self, tests_dir: Path, import_name: str) -> None:
        """Generate basic test file for package.

        Args:
            tests_dir: Directory to create test file in
            import_name: Python import name for the package
        """
        test_content = f'''"""Test suite for {import_name}."""
            
def test_version():
    """Verify package exposes version."""
    import {import_name}
    assert {import_name}.__version__
'''
        self._write_file(tests_dir / f"test_{import_name}.py", test_content)

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

    def _write_file(self, file_path: Path, content: str) -> None:
        """Write content to file with parent directory creation.

        Args:
            file_path: Target file path
            content: Content to write
        """
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        console.print(f"Created: [cyan]{file_path}[/]")

    def _copy_template_file(
        self, src: Path, dst: Path, replacements: dict[str, Any]
    ) -> None:
        """Copy template file with placeholder replacements.

        Args:
            src: Source template file
            dst: Destination path
            replacements: Key-value mappings for template variables
        """
        content = src.read_text(encoding="utf-8")
        for key, value in replacements.items():
            content = content.replace(f"{{{key}}}", str(value))
        self._write_file(dst, content)

    def _get_replacements(
        self, name: str, core_name: str | None = None, is_plugin: bool = False
    ) -> dict[str, Any]:
        """Generate template variable replacements for package files.

        Args:
            name: Package name
            core_name: Core package name for plugins
            is_plugin: Whether generating a plugin package

        Returns:
            Dictionary of template replacements
        """
        import_name = name.replace("-", "_")
        plugin_name = name.split("-")[-1] if is_plugin else import_name
        replacements = {
            "name": name,
            "core_name": core_name or name,
            "plugin_name": plugin_name,
            "import_name": import_name,
            "description": f"Plugin for {core_name}" if is_plugin else "Core package",
        }

        if self.config:
            replacements.update(
                {
                    "author_name": self.config.author_name,
                    "author_email": self.config.author_email,
                    "github_username": self.config.github_username,
                    "min_python": self.config.min_python,
                    "license": self.config.license,
                    "development_status": self.config.development_status,
                }
            )

        return replacements

    def _process_theme_files(
        self,
        theme_path: Path,
        transform: Callable[[Path], Path],
        replacements: dict[str, Any],
    ) -> None:
        """Process template files from theme directory.

        Args:
            theme_path: Path to theme directory
            transform: Function to map source files to destination paths
            replacements: Template variables to replace
        """
        for file in (f for f in theme_path.rglob("*") if f.is_file()):
            self._copy_template_file(file, transform(file), replacements)

    def _create_dir(self, path: Path) -> None:
        """Create directory if it doesn't exist.

        Args:
            path: Directory path to create
        """
        path.mkdir(parents=True, exist_ok=True)

    def _create_directory_structure(
        self, pkg_path: Path, src_path: Path, import_name: str
    ) -> None:
        """Create standard package directory structure.

        Args:
            pkg_path: Root package directory
            src_path: Source code directory
            import_name: Python import name
        """
        self._create_dir(pkg_path)
        self._create_dir(src_path)

        tests_dir = pkg_path / "tests"
        self._create_dir(tests_dir)
        (tests_dir / "__init__.py").touch()
        self._create_test_file(tests_dir, import_name)

        def core_transform(file: Path) -> Path:
            target_name = file.name.replace("hatch_", "")
            return (
                src_path / target_name
                if target_name.endswith(".py")
                else pkg_path / target_name
            )

        core_replacements = {
            "name": import_name,
            "core_name": import_name,
            "plugin_name": import_name.split("_")[-1],
            "import_name": import_name,
            "title": f"{import_name} - Core Package",
            "description": "Core package for plugin management",
            "usage": f"import {import_name}\nplugin = {import_name}.plugin_name",
        }
        self._process_theme_files(
            self.template.theme_path, core_transform, core_replacements
        )

        if self.config and self.config.use_mkdocs:
            self._setup_mkdocs(pkg_path, import_name)

        if self.config and self.config.use_vcs:
            self._init_git_repo(pkg_path)

    def _setup_mkdocs(self, pkg_path: Path, import_name: str) -> None:
        """Configure MkDocs documentation setup.

        Args:
            pkg_path: Root package directory
            import_name: Python import name
        """
        docs_dir = pkg_path / "docs"
        self._create_dir(docs_dir)

        mkdocs_theme = PackageTemplate.from_theme("mkdocs")

        def mkdocs_transform(file: Path) -> Path:
            match file.name:
                case "hatch_mkdocs.yml":
                    return pkg_path / "mkdocs.yml"
                case _:
                    return docs_dir / file.name.replace("hatch_docs_", "")

        self._process_theme_files(
            mkdocs_theme.theme_path,
            mkdocs_transform,
            self._get_replacements(import_name),
        )

    def init_core_package(self, name: str) -> None:
        """Generate core package structure.

        Args:
            name: Name of core package
        """
        import_name = name.replace("-", "_")
        pkg_path = self.out_dir / name
        src_path = pkg_path / "src" / import_name
        self._create_directory_structure(pkg_path, src_path, import_name)

    def init_plugin_package(self, name: str, core_name: str) -> None:
        """Generate plugin package structure.

        Args:
            name: Name of plugin package
            core_name: Name of core package
        """
        import_name = name.replace("-", "_")
        pkg_path = self.out_dir / name
        src_path = pkg_path / "src" / import_name
        self._create_directory_structure(pkg_path, src_path, import_name)
