"""Plugin implementation."""
from importlib import metadata
from typing import Any, Dict, Optional

from .core import Plugin

__version__ = metadata.version(__name__)
__all__ = ["Plugin", "__version__"] 