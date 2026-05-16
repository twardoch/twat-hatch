# this_file: tests/test_cli.py
"""Tests for twat-hatch Fire CLI entry points."""

from __future__ import annotations

import subprocess
import sys


def run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "twat_hatch", *args],
        capture_output=True,
        text=True,
    )


def _help_output(result: subprocess.CompletedProcess[str]) -> str:
    """Fire writes help to stderr; fall back to stdout."""
    return result.stderr or result.stdout


def test_help_exits_zero():
    """twat-hatch --help exits 0 and prints a command listing."""
    result = run(["--help"])
    assert result.returncode == 0
    assert _help_output(result)


def test_version_leaf():
    """twat-hatch version prints a semver string."""
    result = run(["version"])
    assert result.returncode == 0
    # Fire prints return value to stdout
    version = (result.stdout or result.stderr).strip()
    assert version, "version output must not be empty"
    parts = version.split(".")
    assert len(parts) >= 2, f"Expected semver, got: {version!r}"


def test_init_help():
    """twat-hatch init --help exits 0."""
    result = run(["init", "--help"])
    assert result.returncode == 0
    assert _help_output(result)


def test_plugin_init_help():
    """twat-hatch plugin-init --help exits 0."""
    result = run(["plugin-init", "--help"])
    assert result.returncode == 0
    assert _help_output(result)


def test_create_help():
    """twat-hatch create --help exits 0."""
    result = run(["create", "--help"])
    assert result.returncode == 0
    assert _help_output(result)


def test_config_help():
    """twat-hatch config --help exits 0."""
    result = run(["config", "--help"])
    assert result.returncode == 0
    assert _help_output(result)
