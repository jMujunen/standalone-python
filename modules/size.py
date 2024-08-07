#!/usr/bin/env python3
"""Convert bytes to a human-readble string"""

import sys


class Converter:
    """Converts a size in bytes to a human-readable string representation."""

    def __init__(self, size_in_bytes: int):
        """Initialize ByteConverter object with a size in bytes.

        Parameters:
        ----------
            `size_in_bytes` (int): Size in bytes."""

        self.size_in_bytes = abs(int(size_in_bytes))
        self._size_str = self._convert()
        if size_in_bytes < 0:
            self._size_str = "-" + self._size_str

    def _convert(self) -> str:
        """
        Converts a given size in bytes to the appropriate unit (B, KB, MB, GB, or TB).

        Returns:
        ---------
            `str` : A string representation of the size with its corresponding unit attached.
        """
        size = self.size_in_bytes
        units = ["B", "KB", "MB", "GB", "TB"]
        for unit in units[:-1]:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024

        return f"{size / 1024:.2f} {units[-1]}"  # Last unit is TB

    def __str__(self):
        return self._size_str

    def __float__(self) -> float:
        return float(self._size_str.split()[0])

    def __int__(self) -> int:
        return int(float(self))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.__dict__})"


if __name__ == "__main__":
    try:
        print(Converter(int(sys.argv[1])))
    except (IndexError, ValueError):
        print("Usage: ./size  <size in bytes>")
        sys.exit(1)
