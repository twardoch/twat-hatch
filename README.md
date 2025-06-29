# `twat-hatch`: Modern Python Package Initialization

**`twat-hatch` is a powerful command-line tool for initializing modern Python projects.** It helps you quickly scaffold new standalone packages or complex plugin-based architectures, adhering to current best practices in Python development.

`twat-hatch` is part of the **[twat](https://pypi.org/project/twat/)** collection of Python developer utilities, aimed at streamlining and enhancing the Python development workflow.

## Who is `twat-hatch` for?

`twat-hatch` is designed for Python developers who want to:

*   **Bootstrap new projects rapidly:** Get a well-structured project skeleton in seconds.
*   **Build extensible applications:** Easily create systems with a core package and multiple installable plugins.
*   **Adhere to modern standards:** Automatically set up projects with `pyproject.toml` (PEP 621), `src/` layout, and robust tooling.
*   **Focus on code, not boilerplate:** Reduce the manual effort of setting up configurations, directory structures, and initial files.

## Why is `twat-hatch` useful?

*   **Accelerated Project Setup:** Generates all the necessary boilerplate for a new Python package, including directory structure, `pyproject.toml`, license, README, and basic test setup.
*   **Plugin Architecture Support:** Provides first-class support for creating plugin host packages and individual plugin packages, managing entry points and dependencies.
*   **Best Practices by Default:**
    *   Uses `pyproject.toml` for all package metadata and tool configuration (PEP 621).
    *   Implements the `src/` layout for cleaner package structure.
    *   Integrates with modern tooling like `ruff` for linting/formatting and `mypy` for type checking.
*   **Flexible Configuration:** Uses a simple TOML file (`twat-hatch.toml`) for defining project parameters, which can be generated interactively.
*   **Developer Tool Integration:** Optionally initializes Git repositories, creates GitHub repositories (via `gh` CLI), and sets up MkDocs for documentation.
*   **Type-Safe & Robust:** Leverages Pydantic for configuration validation, ensuring your setup is correct from the start.

## Installation

You can install `twat-hatch` using `pip` or `uv`:

```bash
pip install twat-hatch
```

Or with `uv`:

```bash
uv pip install twat-hatch
```

## How to Use `twat-hatch`

`twat-hatch` primarily operates through its command-line interface (CLI).

### 1. Initialize Configuration (`twat-hatch init`)

The first step is to create a configuration file, typically named `twat-hatch.toml`. The `init` command helps you generate this file.

**Interactive Mode:**

If you run `twat-hatch init` without arguments, it will guide you through an interactive prompt:

```bash
twat-hatch init
```

You'll be asked for:
*   Package type (standalone package, plugin, or plugin-host)
*   Package name
*   Author details
*   Python version constraints
*   License
*   Optional features like MkDocs and Git repository initialization.

This will create a `twat-hatch.toml` file in your current directory.

**Non-Interactive Mode:**

You can also provide all configuration values as command-line options. For example:

```bash
twat-hatch init --name "my-cool-package" --author-name "Your Name" --author-email "you@example.com" --min-python "3.10" --license "MIT"
```

This is useful for scripting or when you already know your desired configuration.

**Specify Package Type:**

Use the `package_type` argument to define the kind of project:
*   `twat-hatch init --package-type package` (default)
*   `twat-hatch init --package-type plugin --plugin-host "my-core-app"`
*   `twat-hatch init --package-type plugin-host`

### 2. Review Example Configuration (`twat-hatch config show`)

To see what a typical `twat-hatch.toml` looks like for different package types without generating a file, use:

```bash
twat-hatch config show --package-type plugin
```
This will print an example configuration to the console. Supported types are `package`, `plugin`, and `plugin-host`.

### 3. Create Your Package(s) (`twat-hatch create`)

Once you have your `twat-hatch.toml` (or a custom-named one), run the `create` command:

```bash
twat-hatch create
```

By default, it looks for `twat-hatch.toml` in the current directory. You can specify a different configuration file:

```bash
twat-hatch create --config-path "path/to/my-config.toml"
```

This command will:
*   Read the configuration.
*   Generate the directory structure for each package specified.
*   Populate files based on templates (e.g., `pyproject.toml`, `__init__.py`, `README.md`).
*   Initialize a Git repository and make an initial commit (if `use_vcs` is enabled).
*   Optionally set up MkDocs.

Your new Python project(s) will be ready in the specified output directory!

### Programmatic Usage

While primarily a CLI tool, `twat-hatch`'s core logic can be used programmatically.

**Generating Packages:**

```python
from pathlib import Path
from twat_hatch import PackageInitializer

# Ensure you have a 'twat-hatch.toml' or provide the path to one
# For example, create a dummy config for demonstration:
config_content = """
[project]
packages = ["my-programmatic-package"]
output_dir = "generated_packages"

[author]
name = "Dev Team"
email = "dev@example.com"
github_username = "devteam"

[package]
min_python = "3.9"
license = "Apache-2.0"
development_status = "3 - Alpha"

[features]
use_vcs = false
"""
Path("my_prog_config.toml").write_text(config_content)

try:
    # Initialize with the path to your config file
    initializer = PackageInitializer(config_path="my_prog_config.toml")

    # Create all packages defined in the configuration
    initializer.initialize_all()

    print("Package 'my-programmatic-package' created in 'generated_packages/'")

except FileNotFoundError:
    print("Error: Configuration file not found.")
except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Clean up the dummy config
    Path("my_prog_config.toml").unlink(missing_ok=True)
```

**Generating Configuration Programmatically:**

You can also generate the `twat-hatch.toml` content itself using `ConfigurationGenerator`:

```python
from twat_hatch.config import ConfigurationGenerator
from pathlib import Path

generator = ConfigurationGenerator()

config_str = generator.generate_config(
    package_type="package",
    name="another-package",
    author_name="AI Coder",
    author_email="ai@example.com",
    github_username="aicoder",
    min_python="3.10",
    license="BSD-3-Clause",
    use_mkdocs=True
)

# You can then write this string to a file
Path("generated_config.toml").write_text(config_str)
print("Configuration for 'another-package' written to generated_config.toml")

# Clean up
Path("generated_config.toml").unlink(missing_ok=True)
```
This allows for more dynamic or automated project setup scenarios from within other Python scripts or tools.

## Technical Deep Dive

This section provides a more detailed look into how `twat-hatch` works internally and outlines guidelines for coding and contributions.

### How `twat-hatch` Works

`twat-hatch` leverages a combination of configuration parsing, templating, and command-line utilities to generate Python projects.

**Core Components:**

*   **`PackageInitializer` (`src/twat_hatch/hatch.py`):** This is the main orchestrator. It reads the configuration, determines the package types, and uses the `TemplateEngine` to generate files and directories. It also handles Git repository initialization and optional GitHub integration.
*   **`PackageConfig` (`src/twat_hatch/hatch.py`):** A Pydantic model that defines the structure of the `twat-hatch.toml` configuration file. It's responsible for loading, validating, and providing type-safe access to configuration parameters.
*   **`TemplateEngine` (`src/twat_hatch/hatch.py`):** Manages the Jinja2 templating environment. It loads templates from the `src/twat_hatch/themes/` directory and renders them with the context derived from `PackageConfig`.
*   **`ConfigurationGenerator` (`src/twat_hatch/config.py`):** Responsible for generating the content of a `twat-hatch.toml` file, either for display (via `config show`) or for the `init` command when not using interactive prompts directly. It uses Jinja2 templates (`*.toml.j2`) for this.
*   **`ConfigurationPrompts` (`src/twat_hatch/__main__.py`):** Handles the interactive command-line prompts when `twat-hatch init` is run. It uses the `rich` library for a better user experience.
*   **CLI (`src/twat_hatch/__main__.py`):** The command-line interface is built using the `fire` library, which maps Python functions to CLI commands (`init`, `config`, `create`).

**Configuration (`twat-hatch.toml`):**

This TOML file is the heart of your project definition. It's parsed by `PackageConfig`. Key sections include:

*   `[project]`:
    *   `packages`: A list of package names to generate (distribution names, e.g., "my-package").
    *   `plugin_host` (optional): The name of the package that will act as the host for plugins. If specified, other packages in the `packages` list are treated as plugins for this host.
    *   `output_dir` (optional): Directory where packages will be created (defaults to current directory).
*   `[author]`:
    *   `name`, `email`, `github_username`: Information used in `pyproject.toml` and other generated files.
*   `[package]`:
    *   `min_python`: Minimum Python version (e.g., "3.8").
    *   `max_python` (optional): Maximum Python version (e.g., "3.12").
    *   `license`: SPDX license identifier (e.g., "MIT", "Apache-2.0").
    *   `development_status`: PyPI classifier for development status (e.g., "4 - Beta").
*   `[dependencies]`:
    *   `dependencies`: List of runtime dependencies for all packages.
    *   `plugin_dependencies`: Additional dependencies specifically for plugin packages.
    *   `dev_dependencies`: Dependencies for the development environment (e.g., `pytest`, `ruff`). In `twat-hatch.toml`, this corresponds to `[development.additional_dependencies]` in the example template, but `PackageConfig` maps it from `development_data.get("additional_dependencies", [])`. For clarity in this README, it's referred to as `dev_dependencies` as it's a common term and matches the `PackageConfig` field.
*   `[features]`:
    *   `mkdocs`: Boolean, enables MkDocs setup.
    *   `semver`: Boolean, for semantic versioning (primarily influences initial versioning "0.1.0"; ongoing versioning is VCS-based via `hatch-vcs`).
    *   `vcs`: Boolean, enables Git repository initialization.
*   `[tools]` (optional, in `twat-hatch.toml`):
    *   `ruff`: Custom Ruff configuration to be embedded in the generated `pyproject.toml`.
    *   `mypy`: Custom MyPy configuration to be embedded in the generated `pyproject.toml`.

**Templating System:**

`twat-hatch` uses Jinja2 for file generation. Templates are located in `src/twat_hatch/themes/`.

*   **Themes:**
    *   `_shared/`: Common snippets or base files used by multiple themes.
    *   `default/`: Base templates applied to ALL package types during `twat-hatch create`. This includes common files like `.gitignore`, basic `pyproject.toml` structure, etc.
    *   `package/`: Templates specific to standalone packages. Also, `package.toml.j2` is used by `ConfigurationGenerator` for generating `twat-hatch.toml` content for the `package` type.
    *   `plugin/`: Templates specific to plugin packages. Defines entry points in `pyproject.toml` to register with the host. Also, `plugin.toml.j2` is used by `ConfigurationGenerator` for `plugin` type configurations.
    *   `plugin_host/`: Templates specific to plugin host packages. Includes logic in `__init__.py` for plugin discovery. Also, `plugin_host.toml.j2` is used by `ConfigurationGenerator` for `plugin-host` type configurations.
    *   `mkdocs/`: Templates for setting up MkDocs documentation (if `features.mkdocs` is true).
*   **Layering (during `twat-hatch create`):** Themes are applied in a specific order. The `default` theme is always applied first. Then, the specific package type theme (`package`, `plugin`, or `plugin_host`) is applied. Finally, optional feature themes like `mkdocs` are applied. This allows for overriding and extending base templates.
*   **Context:** Templates are rendered with a context dictionary derived from `PackageConfig`. Key variables include `name` (distribution name), `import_name`, `author_name`, `license`, `python_version_info` (a dictionary with various Python version formats), etc. File and directory names containing `__package_name__` are renamed to the package's import name. Files starting with `hidden.` are renamed to have a leading dot (e.g., `hidden.gitignore` becomes `.gitignore`).

**Package Types (generated by `twat-hatch create`):**

*   **Standalone Package:** A standard Python package with its own `pyproject.toml`, `src/` directory, and tests. Generated using `default` and then `package` themes.
*   **Plugin Host Package:** A package designed to discover and load plugins.
    *   Its `pyproject.toml` may define extras for installing plugins.
    *   Its `src/<package_name>/__init__.py` often includes logic to discover plugins using `importlib.metadata.entry_points` for a specific group (e.g., `my_host_package.plugins`).
    *   Generated using `default` and then `plugin_host` themes.
*   **Plugin Package:** A package that extends a plugin host.
    *   Its `pyproject.toml` defines an entry point under the host's plugin group (e.g., `[project.entry-points."my_host_package.plugins"] my_plugin = "my_plugin_package.module:entry_point"`).
    *   Generated using `default` and then `plugin` themes.

**Version Control (Git):**

If `features.vcs` is true (default):
1.  `git init` is run in the newly created package directory.
2.  The default branch is renamed to `main`.
3.  All generated files are added (`git add .`).
4.  An initial commit is made (`git commit -m "Initial commit"`).
5.  If a `github_username` is provided in the config and the `gh` CLI tool is installed and authenticated, `twat-hatch` will attempt to create a public GitHub repository and push the initial commit.

**Python Version Handling (`src/twat_hatch/utils.py`):**

The `PyVer` class is a utility to:
*   Parse Python versions from strings (e.g., "3.10") or tuples.
*   Generate `requires_python` specifiers for `pyproject.toml` (e.g., `">=3.10, <3.13"` if a max version is given).
*   Produce a list of PyPI trove classifiers for supported Python versions.
*   Provide version strings suitable for `ruff` (`target-version`) and `mypy` (`python_version`).

### Coding and Contribution Guidelines

We welcome contributions to `twat-hatch`! Please follow these guidelines:

**Coding Conventions:**

*   **Style:** Code style is enforced by `Ruff`. Please run `ruff format .` and `ruff check .` before committing. Configuration is in `pyproject.toml`.
*   **Type Safety:** `MyPy` is used for static type checking. Ensure your code passes `mypy src/ tests/`. Configuration is in `pyproject.toml`.
*   **Pre-commit Hooks:** It's highly recommended to install and use `pre-commit` hooks provided in `.pre-commit-config.yaml`. Run `pre-commit install` in your cloned repository. This will automatically run checks before each commit.
*   **Imports:**
    *   Use absolute imports within the `src/twat_hatch` package.
    *   Imports are sorted by `Ruff` (which implements `isort` logic).
    *   Relative imports are generally discouraged for main package code, as per `flake8-tidy-imports` configuration (`ban-relative-imports = 'all'`).

**Project Structure:**

*   **`src/` Layout:** All main source code resides in `src/twat_hatch/`.
*   **`tests/`:** Unit and integration tests are located here.
*   **`src/twat_hatch/themes/`:** Contains Jinja2 templates for code generation.
    *   Each subdirectory typically represents a theme or a component of a theme (e.g., `default`, `package`, `plugin`, `plugin_host`, `mkdocs`).
    *   Templates for generated files usually end with `.j2` (e.g., `pyproject.toml.j2`).
    *   Templates for `twat-hatch.toml` generation itself are also in this directory (e.g., `package.toml.j2`, `plugin.toml.j2`, `plugin_host.toml.j2`).

**Dependency Management:**

*   Project dependencies are managed by `Hatch` and defined in `pyproject.toml`.
*   Runtime dependencies are under `[project.dependencies]`.
*   Development dependencies are listed under `[project.optional-dependencies]` (e.g., `dev`, `test`).
*   The project uses `hatch-pip-compile` which can be used to generate and manage constraints files for reproducible environments, though explicit lock files might not be versioned if broad compatibility is prioritized.

**Testing:**

*   `pytest` is the testing framework.
*   Write tests for new features and bug fixes in the `tests/` directory.
*   Ensure all tests pass by running `pytest` or `hatch run test`.
*   Aim for high test coverage. Check coverage with `hatch run test-cov`.

**Contribution Process:**

1.  **Fork the repository** on GitHub.
2.  **Clone your fork** locally: `git clone https://github.com/YOUR_USERNAME/twat-hatch.git`
3.  **Create a new branch** for your feature or bug fix: `git checkout -b feature/your-feature-name` or `bugfix/issue-number`.
4.  **Make your changes.**
5.  **Run linters and tests locally:**
    *   `hatch run lint:all` (runs ruff format, ruff check, mypy)
    *   `hatch run test` (runs pytest)
    *   Or use `pre-commit run --all-files` if hooks are installed.
6.  **Commit your changes** with a clear and descriptive commit message. Consider using [Conventional Commits](https://www.conventionalcommits.org/) format (e.g., `feat: add support for X`, `fix: resolve issue Y`).
    *   A good commit message subject line is concise (<=50 chars).
    *   The body (if needed) explains the "what" and "why" of the change.
7.  **Push your branch** to your fork: `git push origin feature/your-feature-name`.
8.  **Open a Pull Request (PR)** against the `main` branch of the `twardoch/twat-hatch` repository.
9.  Clearly describe your changes in the PR. Reference any related issues.

**Versioning:**

*   `twat-hatch` uses `hatch-vcs` for versioning. The version is automatically derived from Git tags (e.g., `v0.1.0`).
*   The version is written to `src/twat_hatch/__version__.py` during the build process by `hatch-vcs`.

**License:**

By contributing, you agree that your contributions will be licensed under the MIT License, as found in the `LICENSE` file.
