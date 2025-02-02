"""Core namespace package for dynamic plugin loading."""

from importlib import metadata
from typing import Any, Dict, Optional

__version__ = metadata.version(__name__)


def __getattr__(name: str) -> Any:
    """Dynamic attribute lookup for plugins.

    Args:
        name: The name of the plugin to load.

    Returns:
        The loaded plugin module.

    Raises:
        AttributeError: If the plugin cannot be found or loaded.
    """
    try:
        module_name = f"{name}_{name}"
        return __import__(module_name)
    except ImportError:
        pass

    try:
        eps = metadata.entry_points(group="{name}.plugins")
        for ep in eps:
            if ep.name == name:
                return ep.load()
    except Exception as e:
        raise AttributeError(f"Failed to load plugin '{name}': {e}") from e

    raise AttributeError(f"module '{name}' has no attribute '{name}'")
