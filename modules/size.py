#!/usr/bin/env python3
"""Convert bytes to a human-readble string."""

import sys
from enum import Enum


class ByteConverterError(Exception):
    """Raised when an error is encountered during conversion."""

    pass  # noqa


class SizeUnit(Enum):
    B = 1
    KB = 1024
    MB = 1024**2
    GB = 1024**3
    TB = 1024**4


class Size:
    """Converts a size in bytes to a human-readable string representation."""

    def __init__(self, size_in_bytes: int):
        """Initialize ByteConverter object with a size in bytes.

        Parameters:
        ----------
            - `size_in_bytes` (int): Size in bytes."""

        self.size_in_bytes = abs(int(size_in_bytes))
        # if size_in_bytes < 0:
        # self._size_str = "-" + self._size_str

    def _convert(self) -> str:
        """Convert bytes to the appropriate unit (B, KB, MB, GB, or TB)."""
        size = self.size_in_bytes
        for unit in SizeUnit:
            if size < unit.value:
                return f"{size:.2f} {unit.name}"
            size /= 1024

        return f"{size / 1024:.2f} {SizeUnit.TB.name}"  # Last unit is TB

    def __str__(self):
        return self._convert()

    def __float__(self) -> float:
        return float(self._convert().split()[0])

    def __int__(self) -> int:
        return int(float(self))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}" + f"(raw={self.size_in_bytes}, human={self._convert()})"

    def __format__(self, format_spec: str, /) -> str:
        match format_spec:
            case "r":
                return repr(self)
            case "s":
                return str(self)
            case "d":
                return f"{int(self):d}"
            case ",":
                return f"{int(self):,}"
            case _:
                return str(self)


if __name__ == "__main__":
    try:
        # isatty() returns True if file descriptor is a TTY
        arg = sys.stdin.read() if not sys.stdin.isatty() else sys.argv[1]
        print(Size(int(arg)))
    except (IndexError, ValueError):
        print("Usage: ./size  <size in bytes>")
        sys.exit(1)
