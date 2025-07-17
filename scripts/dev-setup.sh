#!/bin/bash
# Development environment setup script for twat-hatch
set -euo pipefail

echo "🔧 Setting up development environment for twat-hatch..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
if [[ "$(printf '%s\n' "3.10" "$PYTHON_VERSION" | sort -V | head -n1)" != "3.10" ]]; then
    echo "❌ Error: Python 3.10 or later is required (found: $PYTHON_VERSION)"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION found"

# Install/upgrade pip
echo "📥 Installing/upgrading pip..."
python3 -m pip install --upgrade pip

# Install hatch
echo "📥 Installing hatch..."
python3 -m pip install --upgrade hatch

# Install development dependencies
echo "📥 Installing development dependencies..."
hatch env create

# Install pre-commit hooks
echo "🔧 Setting up pre-commit hooks..."
hatch run pre-commit install

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x scripts/*.sh

# Run initial tests
echo "🧪 Running initial tests..."
hatch run test

echo "✅ Development environment setup complete!"
echo ""
echo "Available commands:"
echo "  hatch run test       # Run tests"
echo "  hatch run test-cov   # Run tests with coverage"
echo "  hatch run lint:all   # Run linting and formatting"
echo "  hatch run lint:typing # Run type checking"
echo "  ./scripts/build.sh   # Build package"
echo "  ./scripts/test.sh    # Run all tests"
echo "  ./scripts/release.sh # Create release"