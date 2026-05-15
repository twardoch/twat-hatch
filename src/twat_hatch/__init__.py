"""Package initialization functionality for twat."""

from .__version__ import __version__  # noqa: F401

from twat_hatch.hatch import PackageInitializer

__all__ = ["PackageInitializer", "__version__"]
