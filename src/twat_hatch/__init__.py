"""Package initialization functionality for twat."""

from importlib import metadata

from .hatch import PackageInitializer

__version__ = metadata.version(__name__)
__all__ = ["PackageInitializer", "__version__"]
