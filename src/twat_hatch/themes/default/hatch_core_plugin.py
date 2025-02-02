"""Core plugin functionality."""
from typing import Any, Dict, Optional


class Plugin:
    """Main plugin class."""
    
    def __init__(self) -> None:
        """Initialize the plugin."""
        self._data: Dict[str, Any] = {}

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """Retrieve a value from the plugin data.
        
        Args:
            key: The key to retrieve.
            default: The default value if key is not found.
            
        Returns:
            The value associated with the key, or default if not found.
        """
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a value in the plugin data.
        
        Args:
            key: The key to set.
            value: The value to store.
        """
        self._data[key] = value 