#!/bin/bash
# Local build script for twat-hatch
set -euo pipefail

echo "🔧 Building twat-hatch..."

# Clean previous builds
echo "📦 Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info/

# Install build dependencies
echo "📥 Installing build dependencies..."
python -m pip install --upgrade pip hatch

# Build the package
echo "🏗️  Building package..."
hatch build

# Verify build
echo "✅ Build completed successfully!"
echo "📦 Built packages:"
ls -la dist/

echo "✨ Build complete!"