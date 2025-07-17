#!/bin/bash
# Local release script for twat-hatch
set -euo pipefail

# Function to display usage
usage() {
    echo "Usage: $0 [major|minor|patch|VERSION]"
    echo "Examples:"
    echo "  $0 patch      # Bump patch version (1.0.0 -> 1.0.1)"
    echo "  $0 minor      # Bump minor version (1.0.0 -> 1.1.0)"
    echo "  $0 major      # Bump major version (1.0.0 -> 2.0.0)"
    echo "  $0 1.2.3      # Set specific version"
    exit 1
}

# Check if version argument is provided
if [ $# -eq 0 ]; then
    usage
fi

VERSION_ARG="$1"

echo "🚀 Preparing release for twat-hatch..."

# Ensure we're on main branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "❌ Error: Must be on main branch for release. Current branch: $CURRENT_BRANCH"
    exit 1
fi

# Ensure working tree is clean
if [ -n "$(git status --porcelain)" ]; then
    echo "❌ Error: Working tree is not clean. Please commit or stash changes."
    git status
    exit 1
fi

# Pull latest changes
echo "📥 Pulling latest changes..."
git pull origin main

# Run tests
echo "🧪 Running tests..."
./scripts/test.sh

# Determine version
if [[ "$VERSION_ARG" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    NEW_VERSION="$VERSION_ARG"
else
    # Get current version from git tags
    CURRENT_VERSION=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
    CURRENT_VERSION=${CURRENT_VERSION#v}  # Remove 'v' prefix
    
    # Parse version components
    IFS='.' read -r -a VERSION_PARTS <<< "$CURRENT_VERSION"
    MAJOR=${VERSION_PARTS[0]:-0}
    MINOR=${VERSION_PARTS[1]:-0}
    PATCH=${VERSION_PARTS[2]:-0}
    
    # Bump version based on argument
    case "$VERSION_ARG" in
        major)
            NEW_VERSION="$((MAJOR + 1)).0.0"
            ;;
        minor)
            NEW_VERSION="$MAJOR.$((MINOR + 1)).0"
            ;;
        patch)
            NEW_VERSION="$MAJOR.$MINOR.$((PATCH + 1))"
            ;;
        *)
            echo "❌ Error: Invalid version argument: $VERSION_ARG"
            usage
            ;;
    esac
fi

echo "📝 Version: $CURRENT_VERSION -> $NEW_VERSION"

# Confirm release
read -p "🤔 Proceed with release v$NEW_VERSION? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Release cancelled."
    exit 1
fi

# Create git tag
echo "🏷️  Creating git tag v$NEW_VERSION..."
git tag -a "v$NEW_VERSION" -m "Release v$NEW_VERSION"

# Push tag
echo "📤 Pushing tag to remote..."
git push origin "v$NEW_VERSION"

# Build package
echo "🏗️  Building package..."
./scripts/build.sh

# Show release information
echo "🎉 Release v$NEW_VERSION completed!"
echo "📦 Package built in dist/"
echo "🏷️  Tag v$NEW_VERSION pushed to remote"
echo ""
echo "Next steps:"
echo "1. GitHub Actions will automatically create a release"
echo "2. To publish to PyPI manually: hatch publish"
echo "3. To create GitHub release manually: gh release create v$NEW_VERSION --generate-notes"