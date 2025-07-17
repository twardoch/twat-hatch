# Development Guide

## Overview

This document provides a comprehensive guide for developing, testing, and releasing the twat-hatch package.

## Quick Start

1. **Setup development environment:**
   ```bash
   ./scripts/dev-setup.sh
   ```

2. **Run tests:**
   ```bash
   ./scripts/test.sh
   # or
   make test
   ```

3. **Build package:**
   ```bash
   ./scripts/build.sh
   # or
   make build
   ```

4. **Create release:**
   ```bash
   ./scripts/release.sh patch  # or minor, major, or specific version
   # or
   make release VERSION=1.2.3
   ```

## Development Scripts

### `scripts/dev-setup.sh`
- Sets up complete development environment
- Installs all dependencies
- Configures pre-commit hooks
- Runs initial tests

### `scripts/test.sh`
- Runs comprehensive test suite
- Includes linting, type checking, and unit tests
- Generates coverage reports

### `scripts/build.sh`
- Builds wheel and source distributions
- Cleans previous builds
- Verifies build artifacts

### `scripts/release.sh`
- Creates git tags for releases
- Supports semantic versioning (major/minor/patch)
- Runs tests before release
- Pushes tags to trigger CI/CD

## GitHub Actions Workflows

> **Note**: The GitHub Actions workflow files need to be created manually due to repository permissions. The following workflows are recommended:

### `.github/workflows/test.yml` (Manual Setup Required)
- Runs on push/PR to main/develop branches
- Tests on Ubuntu, Windows, macOS
- Python 3.10, 3.11, 3.12 matrix
- Includes security scanning
- Uploads coverage reports

### `.github/workflows/release.yml` (Manual Setup Required)
- Triggers on git tags (v*)
- Multiplatform builds
- Automated PyPI publishing
- GitHub release creation
- Binary artifact generation

### `.github/workflows/dependencies.yml` (Manual Setup Required)
- Weekly dependency security scans
- Automated dependency update notifications
- Security vulnerability checks

### Setting up GitHub Actions

1. Create `.github/workflows/` directory in your repository
2. Add the workflow files as described in the original implementation
3. Configure required secrets in GitHub repository settings:
   - `PYPI_TOKEN` - For PyPI publishing
   - `CODECOV_TOKEN` - For coverage reporting (optional)

The workflow configurations are designed to work with the existing scripts and build system.

## Versioning Strategy

The project uses **git-tag-based semversioning** with hatch-vcs:

- **Development versions**: Auto-generated from git commits
- **Release versions**: Created from git tags (e.g., `v1.2.3`)
- **Version scheme**: `guess-next-dev` with fallback to `0.1.0`

### Creating Releases

1. **Patch release** (1.0.0 → 1.0.1):
   ```bash
   ./scripts/release.sh patch
   ```

2. **Minor release** (1.0.0 → 1.1.0):
   ```bash
   ./scripts/release.sh minor
   ```

3. **Major release** (1.0.0 → 2.0.0):
   ```bash
   ./scripts/release.sh major
   ```

4. **Specific version**:
   ```bash
   ./scripts/release.sh 1.2.3
   ```

## Testing

### Test Structure
- `tests/test_twat_hatch.py` - Comprehensive test suite
- Unit tests for all major components
- Integration tests for end-to-end workflows
- Mock tests for external dependencies

### Test Categories
- **PyVer utility tests** - Version parsing and formatting
- **Configuration tests** - Config generation and validation
- **Package initialization tests** - Core functionality
- **Integration tests** - Complete workflows

### Running Tests
```bash
# All tests
hatch run test

# With coverage
hatch run test-cov

# Specific test file
hatch run test tests/test_twat_hatch.py

# Specific test class
hatch run test tests/test_twat_hatch.py::TestPyVer
```

## Code Quality

### Linting and Formatting
- **Ruff** - Fast Python linter and formatter
- **MyPy** - Static type checking
- **Bandit** - Security vulnerability scanning
- **Safety** - Known vulnerability checking

### Running Quality Checks
```bash
# All linting
hatch run lint:all

# Type checking
hatch run lint:typing

# Security scanning
bandit -r src/
safety check
```

## Installation Methods

### From Source
```bash
git clone https://github.com/twardoch/twat-hatch.git
cd twat-hatch
pip install -e .
```

### Universal Installer
```bash
curl -sSL https://raw.githubusercontent.com/twardoch/twat-hatch/main/install.sh | bash
```

### Manual Installation
```bash
# Via pip
pip install twat-hatch

# Via uv
uv pip install twat-hatch
```

## Build Configuration

### Package Structure
- **Wheel builds** - Binary distributions
- **Source distributions** - Full source code
- **Multiple Python versions** - 3.10, 3.11, 3.12
- **Multiple platforms** - Linux, Windows, macOS

### Build Targets
- `hatch build` - Build all distributions
- `hatch build -t wheel` - Build wheel only
- `hatch build -t sdist` - Build source distribution only

## CI/CD Pipeline

### Automated Workflows
1. **Pull Request** - Run tests and checks
2. **Git Tag** - Create release and publish
3. **Weekly** - Dependency security scans
4. **On Demand** - Manual workflow triggers

### Release Process
1. Developer creates git tag
2. GitHub Actions runs tests
3. Builds multiplatform artifacts
4. Creates GitHub release
5. Publishes to PyPI
6. Generates release notes

## Configuration Files

### `pyproject.toml`
- Project metadata and dependencies
- Build system configuration
- Tool configurations (ruff, mypy, pytest)
- Hatch environment definitions

### `.github/workflows/`
- GitHub Actions workflow definitions
- Automated testing and release pipelines
- Security and dependency scanning

### `scripts/`
- Local development automation
- Build, test, and release scripts
- Development environment setup

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Run quality checks
5. Submit pull request

### Development Workflow
```bash
# Setup
./scripts/dev-setup.sh

# Make changes
# ... edit code ...

# Test changes
./scripts/test.sh

# Build and verify
./scripts/build.sh

# Create PR or release
git push origin feature-branch
```

## Troubleshooting

### Common Issues
1. **Python version** - Ensure Python 3.10+
2. **Dependencies** - Run `./scripts/dev-setup.sh`
3. **Tests failing** - Check test output for specific errors
4. **Build issues** - Clean with `make clean`

### Getting Help
- Check existing issues on GitHub
- Review test output for error details
- Consult documentation and README
- Create new issue with reproduction steps

## Future Enhancements

- Binary executable creation
- Additional platform support
- Performance optimizations
- Enhanced security features
- Extended test coverage
- Documentation improvements