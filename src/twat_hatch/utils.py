"""Utility functions for twat-hatch."""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PyVer:
    """Python version representation.

    Handles various Python version formats:
    - Tuple: (3, 10, 0)
    - String: "3.10" or "3.10.0" or "3.10 Final"
    - Ruff format: "py310"
    - sys.version_info
    - Command-line input: "3,10" or (3,10)

    If no version is specified, defaults to Python 3.10.
    """

    major: int = 3
    minor: int = 10
    micro: int = 0

    def __post_init__(self) -> None:
        """Validate version numbers."""
        if self.minor < 0 or self.minor > 99:
            msg = f"Invalid minor version: {self.minor}"
            raise ValueError(msg)
        if self.micro < 0:
            msg = f"Invalid micro version: {self.micro}"
            raise ValueError(msg)

    def __str__(self) -> str:
        """Convert to string format (e.g. '3.10')."""
        return f"{self.major}.{self.minor:02d}"

    def __repr__(self) -> str:
        """Full representation including micro version."""
        return f"PyVer(major={self.major}, minor={self.minor}, micro={self.micro})"

    def as_tuple(self) -> tuple[int, int, int]:
        """Get version as a tuple (major, minor, micro)."""
        return (self.major, self.minor, self.micro)

    @property
    def ruff_target(self) -> str:
        """Get Ruff target version (e.g. 'py310')."""
        return f"py{self.major}{self.minor:02d}"

    @property
    def mypy_version(self) -> str:
        """Get MyPy version string (e.g. '3.10')."""
        return str(self)

    @property
    def classifier_version(self) -> str:
        """Get version string for Python classifier (e.g. '3.10')."""
        return str(self)

    @property
    def full_version(self) -> str:
        """Get full version string (e.g. '3.10.0')."""
        return f"{self.major}.{self.minor:02d}.{self.micro}"

    @classmethod
    def parse(cls, version: str | tuple[int, ...] | Any | None = None) -> PyVer:
        """Parse a version from various formats into a PyVer instance.

        Args:
            version: Version in any supported format or None for defaults
                    Supports:
                    - None (defaults to 3.10)
                    - Tuple[int, ...] like (3, 10) or (3, 10, 0)
                    - sys.version_info style object
                    - String like "3.10" or "3.10.0" or "3.10 Final"
                    - Ruff style string like "py310"

        Returns:
            PyVer instance with Python 3.10 as default

        Raises:
            ValueError: If version string is invalid
        """
        if version is None:
            return cls(major=3, minor=10)

        # Handle tuples and version_info style objects
        if isinstance(version, tuple) or hasattr(version, "major"):
            try:
                major = int(getattr(version, "major", version[0]))
                minor = int(
                    getattr(version, "minor", version[1] if len(version) > 1 else 0)
                )
                micro = int(
                    getattr(version, "micro", version[2] if len(version) > 2 else 0)
                )
                return cls(major=major, minor=minor, micro=micro)
            except (IndexError, AttributeError, ValueError) as e:
                msg = f"Invalid version tuple/object: {version}"
                raise ValueError(msg) from e

        # Convert to string and clean it up
        version_str = str(version).strip().lower()

        # Handle Ruff style strings (py310)
        if version_str.startswith("py"):
            match = re.match(r"py(\d)(\d{2,})", version_str)
            if match:
                major = int(match.group(1))
                minor = int(match.group(2))
                return cls(major=major, minor=minor)
            msg = f"Invalid Ruff version format: {version_str}"
            raise ValueError(msg)

        # Handle version strings (e.g., "3.10" or "3.10.0")
        # Try to parse as X.Y format first
        match = re.match(r"(\d+)\.(\d+)", version_str)
        if match:
            major = int(match.group(1))
            minor = int(match.group(2))
            return cls(major=major, minor=minor)

        # Then try to parse as X.Y.Z format
        match = re.match(r"(\d+)\.(\d+)\.(\d+)", version_str)
        if match:
            major = int(match.group(1))
            minor = int(match.group(2))
            micro = int(match.group(3))
            return cls(major=major, minor=minor, micro=micro)

        # Finally, try to parse as just X format (e.g., "3")
        try:
            major = int(version_str)
            return cls(major=major, minor=0)
        except ValueError as e:
            msg = f"Invalid version string: {version_str}"
            raise ValueError(msg) from e

    @classmethod
    def from_sys_version(cls) -> PyVer:
        """Create PyVer from current Python version."""
        return cls.parse(sys.version_info)

    @classmethod
    def get_supported_versions(
        cls, min_ver: PyVer, max_ver: PyVer | None = None
    ) -> list[str]:
        """Get list of supported Python version classifiers.

        Args:
            min_ver: Minimum Python version
            max_ver: Maximum Python version or None

        Returns:
            List of Python version classifiers
        """
        current_max = 12  # Update this as new Python versions are released
        max_minor = max_ver.minor if max_ver else current_max
        if max_ver and max_ver.major != min_ver.major:
            msg = f"Maximum Python version {max_ver} must have same major version as minimum {min_ver}"
            raise ValueError(msg)

        return [
            f"Programming Language :: Python :: {min_ver.major}.{i:02d}"
            for i in range(min_ver.minor, max_minor + 1)
        ]

    def requires_python(self, max_ver: PyVer | None = None) -> str:
        """Get requires-python string.

        Args:
            max_ver: Maximum Python version or None

        Returns:
            requires-python string (e.g. ">=3.10" or ">=3.10,<3.12")
        """
        requires = f">={self}"
        if max_ver:
            requires += f",<{max_ver}"
        return requires

    @classmethod
    def from_cli_input(
        cls, version: str | tuple[int, ...] | Any | None = None
    ) -> PyVer:
        """Parse Python version from command-line input.

        Args:
            version: Version in CLI format:
                    - None (defaults to 3.10)
                    - Tuple[int, ...] like (3, 10)
                    - String like "3,10"

        Returns:
            PyVer instance with Python 3.10 as default

        Raises:
            ValueError: If version string is invalid or if float is provided
        """
        if version is None:
            return cls(major=3, minor=10)

        if isinstance(version, float):
            msg = (
                "Python version must be specified as comma-separated integers. "
                'Use: "3,10" NOT "3.10"'
            )
            raise ValueError(msg)

        if isinstance(version, tuple):
            if len(version) != 2:
                msg = "Version tuple must have exactly 2 elements"
                raise ValueError(msg)
            return cls(major=version[0], minor=version[1])

        if isinstance(version, str):
            try:
                major, minor = map(int, version.split(","))
                return cls(major=major, minor=minor)
            except ValueError as e:
                msg = 'Version string must be comma-separated integers (e.g. "3,10")'
                raise ValueError(msg) from e

        msg = f"Unsupported version format: {version}"
        raise ValueError(msg)
