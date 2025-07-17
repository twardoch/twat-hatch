#!/bin/bash
# Local test script for twat-hatch
set -euo pipefail

echo "🧪 Running tests for twat-hatch..."

# Install test dependencies
echo "📥 Installing test dependencies..."
python -m pip install --upgrade pip hatch

# Run linting
echo "🔍 Running linting..."
hatch run lint:all

# Run type checking
echo "🔍 Running type checking..."
hatch run lint:typing

# Run tests
echo "🧪 Running tests..."
hatch run test

# Run tests with coverage
echo "📊 Running tests with coverage..."
hatch run test-cov

echo "✅ All tests passed!"