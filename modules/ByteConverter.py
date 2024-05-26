class ByteConverter:
    """
    Converts a size in bytes to a human-readable string representation.

    Parameters:
        size_in_bytes (int): The size in bytes to be converted.

    Returns:
        str: A human-readable string representation of the size, with units such as B, KB, MB, or GB.
    """

    def __init__(self, size_in_bytes):
        self._size_in_bytes = int(size_in_bytes)
        self._convert()

    def _convert(self):
        if self._size_in_bytes < 0:
            if abs(self._size_in_bytes) < 1024:
                self._size_str = f"-{abs(self._size_in_bytes)} B"
            elif abs(self._size_in_bytes) < 1024**2:
                self._size_str = f"-{abs(self._size_in_bytes) / 1024:.2f} KB"
            elif abs(self._size_in_bytes) < 1024**3:
                self._size_str = f"-{(abs(self._size_in_bytes) / (1024**2)):.2f} MB"
            elif abs(self._size_in_bytes) < 1024**4:
                self._size_str = f"-{((abs(self._size_in_bytes) / (1024**3))):.2f} GB"
            else:
                self._size_str = f"-{(self._size_in_bytes / (1024**4)):.2f} TB"
        else:
            if self._size_in_bytes < 1024:
                self._size_str = f"{self._size_in_bytes} B"
            elif self._size_in_bytes < 1024**2:
                self._size_str = f"{self._size_in_bytes / 1024:.2f} KB"
            elif self._size_in_bytes < 1024**3:
                self._size_str = f"{self._size_in_bytes / (1024**2):.2f} MB"
            elif self._size_in_bytes < 1024**4:
                self._size_str = f"{self._size_in_bytes / (1024**3):.2f} GB"
            else:
                self._size_str = f"{self._size_in_bytes / (1024**4):.2f} TB"

    def __str__(self):
        return self._size_str
    def __float__(self):
        return float(self._size_str[:-3])

if __name__ == "__main__":
    size_in_bytes = int(input("Enter the file size in bytes: "))
    converter = ByteConverter(size_in_bytes)
    print(converter)
