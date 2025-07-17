# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **CI/CD**: Complete GitHub Actions workflow for testing, building, and releasing
- **Scripts**: Local development scripts for build, test, and release management
- **Testing**: Comprehensive test suite with multiplatform support
- **Security**: Automated security scanning with bandit and safety
- **Dependencies**: Automated dependency update checking
- **Installation**: Universal installation script and comprehensive installation guide
- **Packaging**: Improved build configuration for multiple distribution formats
- **Documentation**: Enhanced installation and development documentation

### Changed
- **Versioning**: Updated to use `guess-next-dev` version scheme for better semver support
- **Build**: Enhanced build configuration with proper source distribution includes/excludes
- **Testing**: Expanded test coverage for all major components
- **CI**: Multiplatform testing on Ubuntu, Windows, and macOS with Python 3.10-3.12

### Fixed
- **Versioning**: Improved git-tag-based semversioning with fallback version
- **Build**: Fixed package metadata and build artifact generation
- **Security**: Added security scanning and vulnerability checks

## [v2.7.6] - 2025-03-07

### Changed
- **Refactor(PyVer)**: Streamlined `PyVer.parse()` logic in `src/twat_hatch/utils.py`. Removed handling for space-separated suffixes (e.g., "3.10 Final") and eliminated redundant internal validation for minor version numbers. Parsing is now stricter, relying on `__post_init__` for validation.
- **Refactor(.gitignore)**: Simplified the `.gitignore` file to be more focused on Python projects. Removed numerous patterns irrelevant to Python development, while ensuring essential ignores for Python artifacts, OS files, IDE directories, and project-specific generated files (`__version__.py`, `llms.txt`, `REPO_CONTENT.txt`, `CLEANUP.txt`) are present.
- **Refactor(Templates)**: Reviewed and refined comments within the `src/twat_hatch/themes/default/pyproject.toml.j2` template. Removed overly verbose, redundant, or prescriptive comments, particularly regarding dependency versioning. Corrected minor typos and added brief clarifications for less obvious configurations to enhance understanding.
- **Docs(PLAN)**: Consolidated initial analysis and decisions for `cleanup.py`/`repomix` usage, `PyVer` parsing, `PackageConfig.from_toml` review, `.gitignore` simplification, CLI argument review, and template comment review into the main `PLAN.md`. These steps were previously part of an implicit plan and are now explicitly documented as completed.
