# Installation Guide

## Installation Methods

### From PyPI (Recommended)

```bash
pip install twat-hatch
```

Or with uv:

```bash
uv pip install twat-hatch
```

### From Source

```bash
git clone https://github.com/twardoch/twat-hatch.git
cd twat-hatch
pip install -e .
```

### Development Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/twardoch/twat-hatch.git
   cd twat-hatch
   ```

2. Run the development setup script:
   ```bash
   ./scripts/dev-setup.sh
   ```

This will:
- Install all dependencies
- Set up pre-commit hooks
- Create development environment
- Run initial tests

### Binary Releases

Pre-built binaries are available from the [GitHub Releases](https://github.com/twardoch/twat-hatch/releases) page for:

- Linux (x86_64)
- Windows (x86_64)
- macOS (x86_64, arm64)

Download the appropriate binary for your platform and place it in your PATH.

## Requirements

- Python 3.10 or later
- Git (for VCS features)
- GitHub CLI (`gh`) - optional, for GitHub integration

## Verification

After installation, verify it works:

```bash
twat-hatch --version
```

## Platform-Specific Notes

### Windows

If you encounter permission errors, you may need to run as Administrator or use:

```bash
pip install --user twat-hatch
```

### macOS

On macOS, you may need to install Xcode Command Line Tools:

```bash
xcode-select --install
```

### Linux

Most Linux distributions should work out of the box. If you encounter issues with system packages, try installing in a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
pip install twat-hatch
```

## Troubleshooting

### Common Issues

1. **Permission Errors**: Use `--user` flag or virtual environment
2. **Git Not Found**: Install Git and ensure it's in PATH
3. **Python Version**: Ensure Python 3.10+ is installed
4. **Network Issues**: Check firewall/proxy settings

### Getting Help

- Check the [README](README.md) for usage instructions
- Report bugs at [GitHub Issues](https://github.com/twardoch/twat-hatch/issues)
- View logs with `twat-hatch --verbose`

## Uninstallation

```bash
pip uninstall twat-hatch
```