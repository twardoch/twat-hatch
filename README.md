# twat-hatch

A plugin for the `twat` package system that provides package initialization functionality. It helps create new core namespace packages and plugin packages following modern Python packaging best practices.

## Features

- Create core namespace packages for plugin systems
- Create plugin packages that integrate with core packages
- Modern Python packaging with PEP 621 compliance
- Type hints and runtime type checking
- Comprehensive test suite and documentation
- CI/CD ready configuration
- Theme-based template system

## Installation

```bash
pip install twat-hatch
```

## Usage

### Command Line Interface

Create a core package:

```bash
twat-hatch --core mypackage
```

Create plugin packages:

```bash
twat-hatch mypackage-plugin1 mypackage-plugin2 --core mypackage
```

Specify output directory:

```bash
twat-hatch --core mypackage --out-dir /path/to/directory
```

### Python API

```python
from twat import hatch

# Initialize a package creator
initializer = hatch.PackageInitializer(out_dir="/path/to/directory")

# Create a core package
initializer.init_core_package("mypackage")

# Create plugin packages
initializer.init_plugin_package("mypackage-plugin1", "mypackage")
initializer.init_plugin_package("mypackage-plugin2", "mypackage")
```

## Development

This project uses [Hatch](https://hatch.pypa.io/) for development workflow management.

### Setup Development Environment

```bash
# Install hatch if you haven't already
pip install hatch

# Create and activate development environment
hatch shell

# Run tests
hatch run test

# Run tests with coverage
hatch run test-cov

# Run linting
hatch run lint

# Format code
hatch run format
```

## Theme System

The package uses a theme-based template system. Templates are stored in the `themes` directory, with the default theme in `themes/default`. Each theme can contain template files that are used to generate package files.

Template files can use placeholders in the format `{placeholder_name}`. Available placeholders include:

- `{name}`: Package name
- `{core_name}`: Core package name (for plugins)
- `{plugin_name}`: Plugin name (for plugins)
- `{import_name}`: Python import name
- `{title}`: Package title
- `{description}`: Package description
- `{usage}`: Usage example

Files with the prefix `hatch_` will have the prefix removed when copied to the target package.

## License

MIT License 