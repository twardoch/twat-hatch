# `twat-hatch`

(work in progress)

A powerful Python package initializer that supports both standalone packages and plugin-based architectures. Built with modern Python practices and robust configuration management.

## Features

- 🎯 **Flexible package creation**: Create standalone packages or plugin-based architectures
- 🔧 **Modern configuration**: Type-safe configuration using Pydantic
- 📦 **Multiple package types**: Support for core packages and plugins
- 🎨 **Templating system**: Jinja2-based templating with multiple themes
- 📚 **Documentation support**: Optional MkDocs integration
- 🔄 **Version control**: Git integration and semantic versioning support
- ✨ **Best practices**: Enforces Python packaging best practices

## Why `twat-hatch`?

`twat-hatch` helps you create modern Python packages with a focus on plugin systems. It implements best practices for:

### Modern python packaging

- PEP 621-style configuration via `pyproject.toml`
- `src/` layout pattern for better packaging practices
- Type hints and runtime type checking with Pydantic
- Automated dependency management

### Plugin system architecture

- **Namespace packages**: Create plugin host packages that dynamically expose plugins
- **Dynamic discovery**: Automatic plugin registration via entry points
- **Flexible usage**: Support both direct imports and namespace-based imports
- **Clean dependencies**: Proper handling of optional plugin dependencies

### Best practices implementation

- **Code organization**: Enforced `src/` layout and modern project structure
- **Error handling**: Built-in validation and error checking
- **Documentation**: Automated documentation setup with MkDocs
- **Testing**: Pre-configured test structure with pytest
- **Type safety**: MyPy configuration and Pydantic validation

## Installation

```bash
uv pip install twat-hatch
```

Or with `pip`:

```bash
pip install twat-hatch
```


## Quick start

1. Create a configuration file `twat-hatch.toml`:

```toml
[project]
packages = ["my-package"]
output_dir = "packages"

[author]
name = "Your Name"
email = "your.email@example.com"
github_username = "yourusername"

[package]
min_python = "3.8"
license = "MIT"
development_status = "4 - Beta"
```

1. Run the package initializer:

```bash
twat-hatch --config twat-hatch.toml
```

## Creating plugin-based packages

### Plugin system overview

When creating a plugin-based architecture, `twat-hatch` generates:

1. **Plugin host package**: The core package that provides plugin discovery and management
2. **Plugin packages**: Individual plugins that integrate with the host package

Example configuration:

```toml
[project]
packages = ["my-plugin-a", "my-plugin-b"]
plugin_host = "my-core-package"
output_dir = "packages"

# ... other configuration ...
```

### Plugin system usage

Once packages are created, they can be used in several ways:

```python
# Direct import of a plugin
import my_plugin_a
instance = my_plugin_a.SomeClass()

# Via namespace package (if configured)
from my_core_package import plugin_a
instance = plugin_a.SomeClass()
```

Installation options:

```bash
# Install a plugin directly
pip install my-plugin-a

# Install via the host package with extras
pip install my-core-package[plugin-a]

# Install multiple plugins
pip install my-core-package[plugin-a,plugin-b]

# Install all available plugins
pip install my-core-package[all]
```

## Configuration reference

The configuration file ( `twat-hatch.toml` ) supports the following sections:

### Project configuration

```toml
[project]
packages = ["package-name"]        # List of packages to create
plugin_host = "host-package"       # Optional plugin host package
output_dir = "path/to/output"      # Output directory (optional)
```

### Author information

```toml
[author]
name = "Author Name"
email = "author@example.com"
github_username = "username"
```

### Package settings

```toml
[package]
min_python = "3.8"                 # Minimum Python version
license = "MIT"                    # Package license
development_status = "4 - Beta"    # PyPI development status
```

### Dependencies

```toml
[dependencies]
dependencies = [                   # Regular dependencies
    "package>=1.0.0"
]
plugin_dependencies = [            # Plugin-specific dependencies
    "plugin-package>=1.0.0"
]
dev_dependencies = [               # Development dependencies
    "pytest>=7.0.0"
]
```

### Features

```toml
[features]
mkdocs = false                     # Enable MkDocs documentation
semver = true                      # Use semantic versioning
vcs = true                        # Initialize Git repository
```

## Generated package structure

### Standalone package

```
my-package/
├── README.md
├── pyproject.toml                 # Project configuration
├── src/
│   └── my_package/               # Package source
│       ├── __init__.py
│       └── core.py
└── tests/                        # Test directory
    ├── conftest.py
    └── test_my_package.py
```

### Plugin host package

```
my-core-package/
├── README.md
├── pyproject.toml
├── src/
│   └── my_core_package/
│       ├── __init__.py           # Plugin discovery logic
│       └── core.py               # Core functionality
└── tests/
    ├── conftest.py
    └── test_my_core_package.py
```

### Plugin package

```
my-plugin/
├── README.md
├── pyproject.toml                # Includes plugin entry points
├── src/
│   └── my_plugin/
│       ├── __init__.py
│       └── plugin.py             # Plugin implementation
└── tests/
    ├── conftest.py
    └── test_my_plugin.py
```

## Development

To set up the development environment:

```bash
git clone https://github.com/twardoch/twat-hatch.git
cd twat-hatch
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

Run linting:

```bash
ruff check .
mypy src/
```

## Technical details

### Package naming convention

- Distribution names use hyphens: `my-plugin`
- Import names use underscores: `my_plugin`
- Plugin host packages follow the same convention

### Plugin discovery

- Plugins register via entry points under `{host}.plugins`
- Plugin host packages support both direct imports and entry point discovery
- Dynamic loading ensures plugins are only imported when needed

### Dependencies management

- Plugin packages can depend on their host package
- Host packages define optional dependencies via extras
- Version compatibility is managed through dependency specifications

### Building and publishing

1. Build and publish the plugin host package first
2. Build and publish plugin packages separately
3. Use consistent versioning across packages

## License

MIT License, see <LICENSE> for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
 
.
