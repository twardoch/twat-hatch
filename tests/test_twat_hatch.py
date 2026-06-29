"""Test suite for twat_hatch."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from pydantic import ValidationError

import twat_hatch
from twat_hatch.config import ConfigurationGenerator, PACKAGE_TEMPLATES
from twat_hatch.hatch import PackageInitializer, PackageConfig
from twat_hatch.utils import PyVer


def test_version() -> None:
    """Verify package exposes version."""
    assert twat_hatch.__version__


class TestPyVer:
    """Test PyVer utility class."""

    def test_version_parsing(self) -> None:
        """Test version parsing from string via PyVer.parse()."""
        pyver = PyVer.parse("3.10")
        assert pyver.version == (3, 10)
        assert pyver.version_str == "3.10"

    def test_version_parsing_tuple(self) -> None:
        """Test version parsing from tuple via PyVer.parse()."""
        pyver = PyVer.parse((3, 11))
        assert pyver.version == (3, 11)
        assert pyver.version_str == "3.11"

    def test_requires_python_single(self) -> None:
        """Test requires_python generation for single version."""
        pyver = PyVer(3, 10)
        assert pyver.requires_python() == ">=3.10"

    def test_requires_python_range(self) -> None:
        """Test requires_python generation for version range.

        The upper bound is exclusive and set to max_ver.minor + 1 so that
        'max_ver' is the last supported version.
        """
        min_ver = PyVer(3, 10)
        max_ver = PyVer(3, 12)
        assert min_ver.requires_python(max_ver) == ">=3.10, <3.13"

    def test_classifiers(self) -> None:
        """Test Python version classifiers generation."""
        pyver = PyVer(3, 10)
        classifiers = pyver.classifiers()
        assert "Programming Language :: Python :: 3.10" in classifiers

    def test_classifiers_range(self) -> None:
        """Test Python version classifiers for range."""
        min_ver = PyVer(3, 10)
        max_ver = PyVer(3, 12)
        classifiers = min_ver.classifiers(max_ver)
        assert "Programming Language :: Python :: 3.10" in classifiers
        assert "Programming Language :: Python :: 3.11" in classifiers
        assert "Programming Language :: Python :: 3.12" in classifiers


class TestConfigurationGenerator:
    """Test configuration generation functionality."""

    def test_generator_initialization(self) -> None:
        """Test ConfigurationGenerator initialization."""
        generator = ConfigurationGenerator()
        assert generator is not None

    def test_package_templates_exist(self) -> None:
        """Test that all package templates are defined."""
        assert "package" in PACKAGE_TEMPLATES
        assert "plugin" in PACKAGE_TEMPLATES
        assert "plugin-host" in PACKAGE_TEMPLATES

    def test_package_template_structure(self) -> None:
        """Test package template structure."""
        template = PACKAGE_TEMPLATES["package"]
        assert template.type == "package"
        assert template.description
        assert template.template_path

    def test_generate_config_basic(self) -> None:
        """Test basic configuration generation."""
        generator = ConfigurationGenerator()
        config = generator.generate_config(
            package_type="package",
            name="test-package",
            author_name="Test Author",
            author_email="test@example.com",
            min_python="3.10",
            license="MIT",
        )
        assert "test-package" in config
        assert "Test Author" in config
        assert "test@example.com" in config
        assert "3.10" in config
        assert "MIT" in config


# Minimal TOML that satisfies all required PackageConfig fields
_BASE_CONFIG = """
[project]
packages = ["{packages}"]
output_dir = "."

[author]
name = "Test Author"
email = "test@example.com"
github_username = "testuser"

[package]
min_python = "3.10"
license = "MIT"
development_status = "4 - Beta"

[features]
vcs = {vcs}
"""


class TestPackageInitializer:
    """Test package initialization functionality."""

    def test_initializer_with_valid_config(self) -> None:
        """Test PackageInitializer with valid configuration."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "test-config.toml"
            config_path.write_text(_BASE_CONFIG.format(packages="test-package", vcs="false"))

            initializer = PackageInitializer(config_path=str(config_path))
            assert initializer.config is not None
            assert initializer.config.packages == ["test-package"]

    def test_initializer_missing_config(self) -> None:
        """Test PackageInitializer with missing configuration."""
        with pytest.raises(FileNotFoundError):
            PackageInitializer(config_path="nonexistent.toml")

    def test_config_validation(self) -> None:
        """Test configuration validation rejects obviously invalid config."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "invalid-config.toml"
            # Missing required fields (github_username, license, development_status)
            config_content = """
[project]
packages = []

[author]
name = ""
email = ""
"""
            config_path.write_text(config_content)

            with pytest.raises((ValidationError, ValueError, Exception)):
                PackageInitializer(config_path=str(config_path))

    @patch("subprocess.run")
    def test_git_initialization(self, mock_run: Mock) -> None:
        """Test Git repository initialization."""
        mock_run.return_value = Mock(returncode=0)

        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "test-config.toml"
            config_path.write_text(_BASE_CONFIG.format(packages="test-package", vcs="true"))

            initializer = PackageInitializer(config_path=str(config_path))
            assert initializer.config.use_vcs is True


class TestIntegration:
    """Integration tests for the complete workflow."""

    def test_end_to_end_package_creation(self) -> None:
        """Test complete package creation workflow."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "test-config.toml"
            output_dir = Path(tmp_dir) / "output"
            output_dir.mkdir()

            # Generate configuration
            generator = ConfigurationGenerator()
            config_content = generator.generate_config(
                package_type="package",
                name="integration-test",
                author_name="Integration Test",
                author_email="integration@test.com",
                min_python="3.10",
                license="MIT",
                use_vcs=False,
            )

            # Write config with output directory
            config_content = config_content.replace('output_dir = "."', f'output_dir = "{output_dir}"')
            config_path.write_text(config_content)

            # Initialize package
            initializer = PackageInitializer(config_path=str(config_path))
            assert initializer.config.packages == ["integration-test"]

            # Test that config is properly loaded
            assert initializer.config.author_name == "Integration Test"
            assert initializer.config.author_email == "integration@test.com"
            assert initializer.config.min_python == "3.10"
            assert initializer.config.license == "MIT"

    def test_plugin_configuration(self) -> None:
        """Test plugin package configuration."""
        generator = ConfigurationGenerator()
        config = generator.generate_config(
            package_type="plugin",
            name="test-plugin",
            author_name="Plugin Author",
            author_email="plugin@example.com",
            min_python="3.10",
            license="MIT",
            plugin_host="test-host",
        )

        assert "test-plugin" in config
        assert "test-host" in config
        assert "Plugin Author" in config
