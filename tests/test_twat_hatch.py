"""Test suite for twat_hatch."""

import twat_hatch


def test_version() -> None:
    """Verify package exposes version."""
    assert twat_hatch.__version__
