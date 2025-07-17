# GitHub Actions Workflows

This document contains the GitHub Actions workflow configurations that need to be manually added to your repository.

## Setup Instructions

1. Create `.github/workflows/` directory in your repository
2. Create the following workflow files with the content provided below
3. Configure required secrets in GitHub repository settings

## Required Secrets

Configure these secrets in your GitHub repository settings (Settings → Secrets and variables → Actions):

- `PYPI_TOKEN` - PyPI API token for publishing packages
- `CODECOV_TOKEN` - Codecov token for coverage reporting (optional)

## Workflow Files

### `.github/workflows/test.yml`

```yaml
name: Test

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ["3.10", "3.11", "3.12"]

    steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: 0

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install hatch

    - name: Run linting
      run: |
        hatch run lint:all

    - name: Run type checking
      run: |
        hatch run lint:typing

    - name: Run tests
      run: |
        hatch run test-cov

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v4
      if: matrix.os == 'ubuntu-latest' && matrix.python-version == '3.10'
      with:
        file: ./coverage.xml
        fail_ci_if_error: false
        token: ${{ secrets.CODECOV_TOKEN }}

  security:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: "3.10"
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install hatch bandit safety
    
    - name: Run security checks with bandit
      run: |
        bandit -r src/
    
    - name: Check for known security vulnerabilities
      run: |
        safety check

  build:
    needs: [test, security]
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: 0
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: "3.10"
    
    - name: Install build dependencies
      run: |
        python -m pip install --upgrade pip
        pip install hatch
    
    - name: Build package
      run: |
        hatch build
    
    - name: Upload build artifacts
      uses: actions/upload-artifact@v4
      with:
        name: dist-${{ github.sha }}
        path: dist/
        retention-days: 30
```

### `.github/workflows/release.yml`

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

permissions:
  contents: write
  id-token: write

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ["3.10", "3.11", "3.12"]

    steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: 0

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install hatch

    - name: Run tests
      run: |
        hatch run test

  build:
    needs: test
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ["3.10", "3.11", "3.12"]

    steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: 0

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install build dependencies
      run: |
        python -m pip install --upgrade pip
        pip install hatch

    - name: Build package
      run: |
        hatch build

    - name: Upload build artifacts
      uses: actions/upload-artifact@v4
      with:
        name: dist-${{ matrix.os }}-py${{ matrix.python-version }}-${{ github.sha }}
        path: dist/
        retention-days: 90

  create-release:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: pypi
      url: https://pypi.org/p/twat-hatch
      
    steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: 0

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: "3.12"

    - name: Install UV
      uses: astral-sh/setup-uv@v5
      with:
        version: "latest"
        python-version: "3.12"
        enable-cache: true

    - name: Install build tools
      run: uv pip install build hatchling hatch-vcs

    - name: Build distributions
      run: uv run python -m build --outdir dist

    - name: Verify distribution files
      run: |
        ls -la dist/
        test -n "$(find dist -name '*.whl')" || (echo "Wheel file missing" && exit 1)
        test -n "$(find dist -name '*.tar.gz')" || (echo "Source distribution missing" && exit 1)

    - name: Download all artifacts
      uses: actions/download-artifact@v4
      with:
        path: artifacts/

    - name: Extract version from tag
      id: version
      run: |
        echo "VERSION=${GITHUB_REF#refs/tags/v}" >> $GITHUB_OUTPUT

    - name: Create GitHub Release
      uses: softprops/action-gh-release@v2
      with:
        tag_name: ${{ github.ref }}
        name: Release v${{ steps.version.outputs.VERSION }}
        draft: false
        prerelease: false
        generate_release_notes: true
        files: |
          dist/*
          artifacts/*/dist/*

    - name: Publish to PyPI
      uses: pypa/gh-action-pypi-publish@release/v1
      with:
        print-hash: true
        verify-metadata: true
```

### `.github/workflows/dependencies.yml`

```yaml
name: Dependencies

on:
  schedule:
    - cron: '0 0 * * 1'  # Run every Monday at midnight
  workflow_dispatch:

jobs:
  security:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: "3.12"
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install hatch safety bandit
    
    - name: Run security checks with bandit
      run: |
        bandit -r src/ -f json -o bandit-report.json || true
        bandit -r src/
    
    - name: Check for known security vulnerabilities
      run: |
        safety check --json --output safety-report.json || true
        safety check
    
    - name: Upload security reports
      uses: actions/upload-artifact@v4
      if: always()
      with:
        name: security-reports
        path: |
          bandit-report.json
          safety-report.json
        retention-days: 30

  dependency-update:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
      with:
        token: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: "3.12"
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install hatch
    
    - name: Check for dependency updates
      run: |
        hatch run pip list --outdated
    
    - name: Create issue for outdated dependencies
      if: always()
      uses: actions/github-script@v7
      with:
        script: |
          const { execSync } = require('child_process');
          
          try {
            const outdated = execSync('hatch run pip list --outdated --format=json', { encoding: 'utf8' });
            const packages = JSON.parse(outdated);
            
            if (packages.length > 0) {
              const body = `## Outdated Dependencies\n\n` +
                packages.map(pkg => `- ${pkg.name}: ${pkg.version} → ${pkg.latest_version}`).join('\n') +
                `\n\n_This issue was automatically created by the dependency check workflow._`;
              
              github.rest.issues.create({
                owner: context.repo.owner,
                repo: context.repo.repo,
                title: 'Outdated Dependencies Found',
                body: body,
                labels: ['dependencies', 'maintenance']
              });
            }
          } catch (error) {
            console.log('No outdated dependencies found or error occurred:', error.message);
          }
```

## Features

### Test Workflow
- **Multi-platform testing**: Ubuntu, Windows, macOS
- **Python version matrix**: 3.10, 3.11, 3.12
- **Comprehensive checks**: Linting, type checking, unit tests
- **Security scanning**: Bandit and Safety checks
- **Coverage reporting**: Codecov integration

### Release Workflow
- **Automated releases**: Triggered by git tags (v*)
- **Multi-platform builds**: Artifacts for all platforms
- **PyPI publishing**: Automated package publishing
- **GitHub releases**: Automatic release creation with notes
- **Binary artifacts**: Generated and attached to releases

### Dependencies Workflow
- **Weekly security scans**: Automated vulnerability checks
- **Dependency monitoring**: Alerts for outdated packages
- **Issue creation**: Automated GitHub issues for updates

## Usage

1. **For testing**: Push to main/develop branches or create pull requests
2. **For releases**: Create and push git tags (e.g., `git tag v1.2.3 && git push origin v1.2.3`)
3. **For security**: Runs automatically weekly or can be triggered manually

All workflows are designed to work with the existing local scripts and build system.